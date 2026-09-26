#!/usr/bin/env bash
# check-allowlist-expiry.sh
#
# Gate paso determinista: falla (exit != 0) si alguna entrada de la allowlist de
# pip-audit ha superado su fecha de caducidad. Una entrada caducada vuelve a
# bloquear el gate (NFR-SEC.3). Coste 0 EUR (bash puro, sin dependencias).
#
# Formato del fichero de allowlist (columnas separadas por espacios en blanco):
#   CVE_ID  dependencia  version  motivo  fecha_alta(YYYY-MM-DD)  caducidad(YYYY-MM-DD)
# Las lineas que empiezan por '#' y las vacias se ignoran (comentarios/cabecera).
#
# Uso:
#   scripts/check-allowlist-expiry.sh [ruta-allowlist]
# Por defecto: backend/.pip-audit-allowlist

set -euo pipefail

ALLOWLIST_FILE="${1:-backend/.pip-audit-allowlist}"

if [ ! -f "$ALLOWLIST_FILE" ]; then
  echo "check-allowlist-expiry: no existe $ALLOWLIST_FILE; nada que comprobar."
  exit 0
fi

today="$(date -u +%F)"
fail=0

while IFS= read -r line || [ -n "$line" ]; do
  # Salta comentarios y lineas en blanco.
  case "$line" in
    ''|'#'*) continue ;;
  esac
  # Campos: cve dep version motivo fecha caducidad (caducidad = ultimo campo).
  # shellcheck disable=SC2086
  set -- $line
  cve="${1:-}"
  dep="${2:-<dep>}"
  expiry="${!#}"   # ultimo argumento = fecha de caducidad
  if [ -z "$cve" ] || [ -z "$expiry" ]; then
    echo "::error::check-allowlist-expiry: entrada malformada -> '$line'"
    fail=1
    continue
  fi
  # Comparacion lexicografica de fechas ISO-8601 (valida para YYYY-MM-DD).
  if [ "$expiry" \< "$today" ]; then
    echo "::error::allowlist $cve ($dep) caducada el $expiry (hoy $today); revisar o eliminar la excepcion"
    fail=1
  fi
done < "$ALLOWLIST_FILE"

if [ "$fail" -ne 0 ]; then
  echo "check-allowlist-expiry: hay entradas caducadas o malformadas; el gate bloquea."
  exit 1
fi

echo "check-allowlist-expiry: OK (ninguna entrada caducada)."
exit 0
