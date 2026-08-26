"""Shared constants for the Futmondo Analytics backend."""

# LaLiga teams — Futmondo IDs → name + logo
# Used as static fallback when the API doesn't return team info
LALIGA_TEAMS = {
    "504e581e4d8bec9a670000c6": {"name": "Real Madrid", "logo": "real-madrid.png"},
    "504e581e4d8bec9a670000c7": {"name": "Barcelona", "logo": "barcelona.png"},
    "504e581e4d8bec9a670000c8": {"name": "Atlético de Madrid", "logo": "atletico-de-madrid.png"},
    "504e581e4d8bec9a670000c9": {"name": "Athletic de Bilbao", "logo": "athletic-de-bilbao.png"},
    "504e581e4d8bec9a670000ca": {"name": "Rayo Vallecano", "logo": "rayo-vallecano.png"},
    "504e581e4d8bec9a670000cb": {"name": "Valencia", "logo": "valencia.png"},
    "504e581e4d8bec9a670000cc": {"name": "Betis", "logo": "betis.png"},
    "504e581e4d8bec9a670000cd": {"name": "Getafe", "logo": "getafe.png"},
    "504e581e4d8bec9a670000ce": {"name": "Real Sociedad", "logo": "real-sociedad.png"},
    "504e581e4d8bec9a670000cf": {"name": "Levante", "logo": "levante.png"},
    "504e581e4d8bec9a670000d0": {"name": "Espanyol", "logo": "espanyol.png"},
    "504e581e4d8bec9a670000d1": {"name": "Osasuna", "logo": "osasuna.png"},
    "504e581e4d8bec9a670000d5": {"name": "Sevilla", "logo": "sevilla.png"},
    "504e581e4d8bec9a670000d6": {"name": "Málaga", "logo": "malaga.png"},
    "504e581e4d8bec9a670000d8": {"name": "Deportivo de la Coruña", "logo": "deportivo-de-la-coruna.png"},
    "504e581e4d8bec9a670000d9": {"name": "Celta de Vigo", "logo": "celta-de-vigo.png"},
    "51b889b1e401a15f2c0000f0": {"name": "Elche", "logo": "elche.png"},
    "51b890f5b986415a2c000012": {"name": "Villarreal", "logo": "villarreal.png"},
    "52038563b8d07d930b00008a": {"name": "Alavés", "logo": "deportivo-alaves.png"},
    "520e4ee4a776cc826b00004b": {"name": "Racing", "logo": "racing-santander.png"},
}

# Convenience: ID → name only (for endpoints that just need the name)
LALIGA_TEAM_NAMES = {tid: info["name"] for tid, info in LALIGA_TEAMS.items()}
