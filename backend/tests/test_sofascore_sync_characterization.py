"""Tests de regresión — reemplazo transaccional de la caché de Sofascore.

Intent `260911-sofascore-cache-atomica` (scope bugfix, metodología test-after).
Cubren la lógica de negocio (criterio de éxito y señalización de baneo) y la
regresión del endpoint (transacción atómica DELETE+INSERT vs. caché intacta).

No usan BD real ni credenciales: se inyectan fakes de la conexión `db` (patrón
de `test_analytics_service.py`) y fakes de los clientes Sofascore/Futmondo. El
fake de `db` registra el ORDEN de operaciones (DELETE/INSERT) sobre una única
conexión para verificar la atomicidad.
"""

import asyncio

import pytest

import app.api.v1.endpoints.sofascore_sync as endpoint
from app.api.v1.endpoints.sofascore_sync import should_apply_replacement
from app.core.constants import SOFASCORE_MIN_COVERAGE_RATIO
from app.services.sofascore_client import SofascoreClient, SofascoreIPBanError


# ---------------------------------------------------------------------------
# Business logic — should_apply_replacement (función pura, FR2.2 / FR2.4)
# ---------------------------------------------------------------------------

def test_should_apply_replacement_ok_por_encima_del_umbral():
    # 8 de 10 (80% ≥ 50%) → se aplica el reemplazo.
    applied, reason = should_apply_replacement(
        synced=8, processed=10, banned=False, min_ratio=SOFASCORE_MIN_COVERAGE_RATIO
    )
    assert applied is True
    assert reason == "ok"


def test_should_apply_replacement_baneo_no_swap():
    # Baneo tiene prioridad sobre cualquier ratio → no se aplica, razón ip_ban.
    applied, reason = should_apply_replacement(
        synced=9, processed=10, banned=True, min_ratio=SOFASCORE_MIN_COVERAGE_RATIO
    )
    assert applied is False
    assert reason == "ip_ban"


def test_should_apply_replacement_parcial_por_debajo_del_umbral():
    # 4 de 10 (40% < 50%) → no se aplica, razón below_threshold.
    applied, reason = should_apply_replacement(
        synced=4, processed=10, banned=False, min_ratio=SOFASCORE_MIN_COVERAGE_RATIO
    )
    assert applied is False
    assert reason == "below_threshold"


def test_should_apply_replacement_justo_en_el_umbral_aplica():
    # 5 de 10 (50% == umbral) → se aplica (el umbral es un mínimo inclusivo).
    applied, reason = should_apply_replacement(
        synced=5, processed=10, banned=False, min_ratio=SOFASCORE_MIN_COVERAGE_RATIO
    )
    assert applied is True
    assert reason == "ok"


def test_should_apply_replacement_sin_jugadores_procesados_no_vacia_cache():
    # processed == 0 → no hay conjunto nuevo válido, se preserva la caché.
    applied, reason = should_apply_replacement(
        synced=0, processed=0, banned=False, min_ratio=SOFASCORE_MIN_COVERAGE_RATIO
    )
    assert applied is False
    assert reason == "below_threshold"


# ---------------------------------------------------------------------------
# Cliente Sofascore — distinción 403 (baneo) vs 404 (no encontrado) (FR2.1)
# ---------------------------------------------------------------------------

class _FakeResponse:
    """Respuesta HTTP mínima parametrizable por status_code."""

    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeSession:
    """Sesión cffi falsa: devuelve un _FakeResponse fijo en cada get."""

    def __init__(self, response):
        self._response = response

    def get(self, url, params=None, timeout=None):
        return self._response


def _build_client(response):
    """Crea un SofascoreClient con sesión falsa y sin throttling real."""
    client = SofascoreClient.__new__(SofascoreClient)
    client.session = _FakeSession(response)
    client._last_request = 0
    client._min_delay = 0
    client._throttle = lambda: None
    return client


def test_search_player_403_lanza_ip_ban_error():
    client = _build_client(_FakeResponse(403))
    with pytest.raises(SofascoreIPBanError):
        client.search_player("Jugador Baneado")


def test_search_player_404_devuelve_none():
    # 404 / status ≠ 200 no es baneo: comportamiento preservado (warning + None).
    client = _build_client(_FakeResponse(404))
    assert client.search_player("Jugador Inexistente") is None


def test_get_403_lanza_ip_ban_error():
    client = _build_client(_FakeResponse(403))
    with pytest.raises(SofascoreIPBanError):
        client._get("/player/123")


def test_get_404_devuelve_none():
    client = _build_client(_FakeResponse(404))
    assert client._get("/player/123") is None


# ---------------------------------------------------------------------------
# Endpoint — regresión de la transacción atómica (FR1 / NFR1)
# ---------------------------------------------------------------------------

class _RecordingCursor:
    """Cursor falso que registra cada operación SQL (verbo inicial) en el log
    compartido de la conexión."""

    def __init__(self, op_log):
        self._op_log = op_log

    def _record(self, sql):
        verb = sql.strip().split()[0].upper()
        self._op_log.append(verb)

    def execute(self, sql, params=None):
        self._record(sql)

    def executemany(self, sql, params_list):
        # Registramos como INSERT el batch insert de la rama sqlite.
        self._op_log.append("INSERT")


class _RecordingConnection:
    """Conexión falsa (context manager) que comparte el log de operaciones."""

    def __init__(self, op_log):
        self._op_log = op_log

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeDB:
    """Fake de DBConnection para la rama sqlite. Registra el orden global de
    operaciones y cuántas conexiones se abrieron."""

    def __init__(self):
        self.db_type = "sqlite"
        self.op_log = []
        self.connections_opened = 0

    def get_connection(self):
        self.connections_opened += 1
        return _RecordingConnection(self.op_log)

    def get_cursor(self, conn):
        return _RecordingCursor(self.op_log)


class _FakeFutmondoClient:
    """Cliente Futmondo mínimo: devuelve standings y un mercado con jugadores
    del computer."""

    def __init__(self, computer_names):
        self.user_id = "user-1"
        self.token = "fake-token"
        self.base_url = "https://futmondo.test"
        self._computer_names = computer_names
        self.session = self._FakeHTTP(computer_names)

    def get_matchday_standings(self, championship_id):
        return {"teams": [{"userid": "user-1", "teamid": "team-1"}]}

    class _FakeHTTP:
        def __init__(self, computer_names):
            self._computer_names = computer_names

        def post(self, url, json=None, timeout=None):
            players = [
                {"name": name, "computer": True, "team": "Equipo"}
                for name in self._computer_names
            ]
            return _FakeResponse(200, {"answer": {"players": players}})


class _FakeSofascoreClient:
    """Cliente Sofascore falso parametrizable.

    - `found_names`: nombres para los que devuelve un resultado con rating.
    - `ban_on`: nombre que dispara SofascoreIPBanError al buscarse (baneo a
      mitad del repoblado).
    """

    def __init__(self, found_names=None, ban_on=None):
        self._found = set(found_names or [])
        self._ban_on = ban_on
        self._next_id = 1000

    def search_player(self, name, team_hint=None):
        if self._ban_on is not None and name == self._ban_on:
            raise SofascoreIPBanError(f"403 buscando '{name}'")
        if name in self._found:
            self._next_id += 1
            return {"id": self._next_id, "name": name}
        return None

    def get_player_full_info(self, player_id):
        return {"id": player_id, "name": "X", "rating": 7.0}


def _patch_endpoint(monkeypatch, fake_db, fake_sofa, computer_names):
    monkeypatch.setattr(endpoint, "get_db", lambda: fake_db)
    monkeypatch.setattr(endpoint, "get_sofascore_client", lambda: fake_sofa)
    monkeypatch.setattr(
        endpoint,
        "get_user_futmondo_client",
        lambda request: _FakeFutmondoClient(computer_names),
    )


def _run_sync(monkeypatch, fake_db, fake_sofa, computer_names):
    _patch_endpoint(monkeypatch, fake_db, fake_sofa, computer_names)
    return asyncio.run(endpoint.sync_sofascore(request=None, championship_id="champ-1"))


def test_endpoint_repoblado_exitoso_delete_e_insert_misma_conexion(monkeypatch):
    names = ["A", "B", "C", "D"]
    fake_db = _FakeDB()
    fake_sofa = _FakeSofascoreClient(found_names=names)  # 4/4 = 100%

    resp = _run_sync(monkeypatch, fake_db, fake_sofa, names)

    assert resp["success"] is True
    assert resp["applied"] is True
    assert resp["reason"] == "ok"
    assert resp["synced"] == 4
    assert resp["total_players"] == 4
    # DELETE + INSERT en una única conexión (misma transacción), en ese orden.
    assert fake_db.op_log == ["DELETE", "INSERT"]
    assert fake_db.connections_opened == 1


def test_endpoint_baneo_a_mitad_no_delete_cache_intacta(monkeypatch):
    names = ["A", "B", "C", "D"]
    fake_db = _FakeDB()
    # Baneo al buscar "B": aborta el repoblado tras "A".
    fake_sofa = _FakeSofascoreClient(found_names=names, ban_on="B")

    resp = _run_sync(monkeypatch, fake_db, fake_sofa, names)

    assert resp["success"] is True
    assert resp["applied"] is False
    assert resp["reason"] == "ip_ban"
    # NUNCA se abre una conexión de escritura: la caché queda intacta (FR1.3).
    assert fake_db.op_log == []
    assert fake_db.connections_opened == 0


def test_endpoint_parcial_por_debajo_del_umbral_no_delete(monkeypatch):
    names = ["A", "B", "C", "D"]
    fake_db = _FakeDB()
    # Solo "A" encontrado → 1/4 = 25% < 50%.
    fake_sofa = _FakeSofascoreClient(found_names=["A"])

    resp = _run_sync(monkeypatch, fake_db, fake_sofa, names)

    assert resp["success"] is True
    assert resp["applied"] is False
    assert resp["reason"] == "below_threshold"
    assert resp["synced"] == 1
    assert fake_db.op_log == []
    assert fake_db.connections_opened == 0


def test_endpoint_parcial_por_encima_del_umbral_aplica_swap(monkeypatch):
    names = ["A", "B", "C", "D"]
    fake_db = _FakeDB()
    # "A", "B", "C" encontrados → 3/4 = 75% ≥ 50%.
    fake_sofa = _FakeSofascoreClient(found_names=["A", "B", "C"])

    resp = _run_sync(monkeypatch, fake_db, fake_sofa, names)

    assert resp["success"] is True
    assert resp["applied"] is True
    assert resp["reason"] == "ok"
    assert resp["synced"] == 3
    assert fake_db.op_log == ["DELETE", "INSERT"]
    assert fake_db.connections_opened == 1
