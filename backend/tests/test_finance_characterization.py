"""
Tests de caracterización del cálculo de FINANZAS por usuario (FR7.1, FR4.1).

Congelan el comportamiento ACTUAL de `player_finances.get_player_finances`:
la fórmula de agregación por usuario, el orden del ranking, la lectura de
premios desde `team_prizes` (única fuente de verdad) y los caminos de borde
(sin usuarios, config por defecto). No usan BD real: se inyecta un doble de
`DataManagerV2` y un `get_db` falso para `_get_finance_config`.

Prioridad afirmada en team.md: finanzas es una de las tres áreas prioritarias.
"""

import os

import pytest

# El módulo importa app.core.config (JWT endurecido): fijar un secreto válido
# ANTES de cualquier import de la app evita el fallo de arranque en el test.
os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.api.v1.endpoints.player_finances as pf  # noqa: E402


DEFAULT_BUDGET = 200_000_000


class FakeDataManager:
    """Doble de DataManagerV2 con datos sintéticos deterministas."""

    def __init__(self, users, transactions=None, adjustments=None,
                 bonuses=None, prizes=None):
        self._users = users
        self._transactions = transactions or {}
        self._adjustments = adjustments or {}
        self._bonuses = bonuses or {}
        self._prizes = prizes or {}

    def get_all_users_with_points(self, championship_id):
        return self._users

    def get_user_transactions(self, championship_id, user_id=None):
        return self._transactions

    def get_user_punishments_bonuses(self, championship_id):
        return self._adjustments

    def get_dream_team_bonus_stats(self, championship_id):
        return self._bonuses

    def get_prizes_by_team(self, championship_id):
        return self._prizes

    def get_user_info_from_db(self, key):
        return None


class FakeCursor:
    def __init__(self, row):
        self._row = row

    def execute(self, *args, **kwargs):
        return self

    def fetchone(self):
        return self._row


class FakeConnCtx:
    def __init__(self, row):
        self._row = row

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeDB:
    """Doble de conexión para `_get_finance_config` (sin BD real)."""

    def __init__(self, budget_row):
        self._budget_row = budget_row

    def get_connection(self):
        return FakeConnCtx(self._budget_row)

    def get_cursor(self, conn):
        return FakeCursor(self._budget_row)

    def adapt_params(self, sql):
        return sql


def _make_client(fake_dm, budget_row=(DEFAULT_BUDGET,), monkeypatch=None):
    """Monta una app FastAPI mínima con el router de finanzas y los dobles."""
    monkeypatch.setattr(pf, "DataManagerV2", lambda *a, **k: fake_dm)
    monkeypatch.setattr(pf, "get_db", lambda: FakeDB(budget_row))
    application = FastAPI()
    application.include_router(pf.router, prefix="/api/v1/player-finances")
    return TestClient(application)


@pytest.fixture
def base_users():
    return [
        {"team_id": "team-1", "user_id": "u1", "team_name": "Alpha",
         "username": "Alpha", "total_points": 500},
        {"team_id": "team-2", "user_id": "u2", "team_name": "Beta",
         "username": "Beta", "total_points": 400},
    ]


def test_finances_happy_path_aggregation_formula(base_users, monkeypatch):
    """Congela la fórmula: budget + points + profit + bonus + ranking + adj."""
    dm = FakeDataManager(
        users=base_users,
        transactions={"team-1": {"transaction_profit": 1_000_000,
                                 "total_spent": 3_000_000,
                                 "total_received": 4_000_000,
                                 "transaction_count": 2}},
        bonuses={"team-1": {"ideal_team_count": 1, "mvp_count": 2}},
        prizes={"team-1": {"ranking": 5_000_000, "mvp": 2_000_000,
                           "points": 10_000_000, "dream_team": 1_000_000,
                           "total": 18_000_000}},
        adjustments={"team-1": {"net_adjustment": -500_000,
                                "total_punishments": 500_000,
                                "total_bonuses": 0, "punishment_count": 1,
                                "bonus_count": 0}},
    )
    client = _make_client(dm, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=champ")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["total_users"] == 2

    alpha = next(u for u in body["users"] if u["team_name"] == "Alpha")
    # total = 200_000_000 + 10_000_000 (points) + 1_000_000 (profit)
    #         + (1_000_000 dream_team + 2_000_000 mvp) (total_bonus)
    #         + 5_000_000 (ranking) + (-500_000) (net_adjustment)
    assert alpha["total_money"] == 218_500_000
    assert alpha["points_money"] == 10_000_000
    assert alpha["transaction_profit"] == 1_000_000
    assert alpha["total_bonus"] == 3_000_000
    assert alpha["ranking_money"] == 5_000_000
    assert alpha["net_adjustment"] == -500_000


def test_finances_defaults_when_no_data_for_user(base_users, monkeypatch):
    """Sin premios/transacciones/ajustes, el total es solo el budget inicial."""
    dm = FakeDataManager(users=base_users)
    client = _make_client(dm, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=champ")
    assert resp.status_code == 200
    beta = next(u for u in resp.json()["users"] if u["team_name"] == "Beta")
    assert beta["total_money"] == DEFAULT_BUDGET
    assert beta["points_money"] == 0
    assert beta["ranking_money"] == 0
    assert beta["total_bonus"] == 0


def test_finances_ranking_sorted_desc_by_total_money(base_users, monkeypatch):
    """El resultado se ordena por total_money descendente."""
    dm = FakeDataManager(
        users=base_users,
        prizes={"team-2": {"ranking": 0, "mvp": 0, "points": 50_000_000,
                           "dream_team": 0, "total": 50_000_000}},
    )
    client = _make_client(dm, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=champ")
    users = resp.json()["users"]
    # Beta recibe 50M en puntos, supera a Alpha (solo budget) -> primero.
    assert users[0]["team_name"] == "Beta"
    assert users[1]["team_name"] == "Alpha"


def test_finances_empty_championship_returns_zero_users(monkeypatch):
    """Sin usuarios en BD, respuesta success con total_users=0 y lista vacía."""
    dm = FakeDataManager(users=[])
    client = _make_client(dm, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=empty")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_users"] == 0
    assert body["users"] == []


def test_finances_config_falls_back_to_default_budget(base_users, monkeypatch):
    """Si user_championships no tiene fila, se usa el budget por defecto (200M)."""
    dm = FakeDataManager(users=base_users)
    # budget_row=None simula que _get_finance_config no encuentra config.
    client = _make_client(dm, budget_row=None, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=champ")
    assert resp.status_code == 200
    alpha = next(u for u in resp.json()["users"] if u["team_name"] == "Alpha")
    assert alpha["initial_budget"] == DEFAULT_BUDGET


def test_finances_upstream_error_maps_to_500(base_users, monkeypatch):
    """Si el DataManager lanza, el endpoint devuelve 500 (comportamiento actual)."""

    class ExplodingDM(FakeDataManager):
        def get_all_users_with_points(self, championship_id):
            raise RuntimeError("db down")

    dm = ExplodingDM(users=base_users)
    client = _make_client(dm, monkeypatch=monkeypatch)
    resp = client.get("/api/v1/player-finances/?championship_id=champ")
    assert resp.status_code == 500
