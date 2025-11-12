import json
from typing import Optional, Any, Dict

from openai import OpenAI

from app.core import config
from app.services.data_manager_v2 import DataManagerV2
from app.services.matchday_humor_data import MatchdayHumorDataAssembler


class MatchdayHumorService:
    """
    Service responsible for crafting humorous matchday articles using OpenAI.
    It orchestrates data aggregation, prompt construction, OpenAI calls, and persistence.
    """

    def __init__(
        self,
        data_manager: Optional[DataManagerV2] = None,
        data_assembler: Optional[MatchdayHumorDataAssembler] = None,
        openai_client: Optional[OpenAI] = None,
        model: Optional[str] = None
    ):
        self.data_manager = data_manager or DataManagerV2(skip_init=True)
        self.assembler = data_assembler or MatchdayHumorDataAssembler(self.data_manager)
        api_key = config.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required to generate humorous articles.")
        self.client = openai_client or OpenAI(api_key=api_key)
        self.model = model or config.OPENAI_MODEL or "gpt-4o-mini"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_or_generate_article(self, championship_id: str, matchday: int, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh:
            cached = self.data_manager.get_matchday_article(championship_id, matchday)
            if cached:
                return {
                    "championship_id": championship_id,
                    "matchday": matchday,
                    "article": cached["article"],
                    "summary": cached["summary"],
                    "generated_at": cached["generated_at"],
                    "updated_at": cached["updated_at"],
                    "source": "cache"
                }

        dataset = self.assembler.build_dataset(championship_id, matchday)
        self._validate_rank_consistency(dataset)
        internal_snapshot = self._build_debug_snapshot(dataset)
        ai_payload = self._generate_with_openai(dataset)

        article_text = ai_payload.get("article") or ai_payload.get("body")
        if not article_text:
            raise RuntimeError("OpenAI response did not include an article.")

        summary = ai_payload.get("highlights") or ai_payload.get("summary")
        self.data_manager.save_matchday_article(
            championship_id=championship_id,
            matchday=matchday,
            article=article_text,
            summary=summary,
            generated_at=ai_payload.get("generated_at")
        )

        stored = self.data_manager.get_matchday_article(championship_id, matchday)
        return {
            "championship_id": championship_id,
            "matchday": matchday,
            "article": stored["article"],
            "summary": stored["summary"],
            "generated_at": stored["generated_at"],
            "updated_at": stored["updated_at"],
            "dataset": dataset,
            "debug_stats": internal_snapshot,
            "source": "generated"
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_with_openai(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls OpenAI with a carefully crafted prompt to produce
        a 400-500 word humorous article plus structured highlights.
        """
        prompt = self._build_prompt(dataset)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un periodista deportivo español con un tono humorístico y mordaz. "
                        "Tu misión es escribir crónicas semanales sobre una liga fantasy, "
                        "destacando giros dramáticos y comparaciones creativas sin perder el dato estadístico."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=1200
        )

        message = response.choices[0].message
        content = message.content if hasattr(message, "content") else None
        if not content:
            raise RuntimeError("OpenAI response did not contain content.")

        # Try parsing JSON first; fallback to heuristic extraction
        payload = self._parse_json_response(content)
        if payload:
            return payload

        return {
            "article": content.strip(),
            "summary": None,
            "generated_at": dataset.get("generated_at")
        }

    def _build_prompt(self, dataset: Dict[str, Any]) -> str:
        serialized = json.dumps(dataset, ensure_ascii=False, indent=2)
        return (
            "Dispones de datos de una jornada de liga fantasy. Necesitamos una crónica humorística que capture ese "
            "mundo fantasy, no un partido real. Inspírate en el tono sarcástico, épico y narrativo de los ejemplos "
            "adjuntos (metáforas bélicas/literarias, patrocinadores ficticios, apartados finales), SIN copiar su "
            "contenido literal ni hablar de un partido concreto. Menciona siempre a managers y jugadores del dataset.\n\n"
            "EJEMPLO DE ESTILO 1 (solo tono):\n"
            "Crónica: Gaztelueta 7 - 1, patrocinada por La Redonda ...\n"
            "EJEMPLO DE ESTILO 2 (solo tono):\n"
            "Crónica: Gaztelueta triunfa en el campo de batalla, patrocinada por Titanlux ...\n\n"
            "Directrices para la crónica fantasy:\n"
            "- Longitud entre 600 y 700 palabras.\n"
            "- Titular obligatorio: 'Crónica: <tema fantasy>, patrocinada por <marca ficticia>'.\n"
            "- Todo el texto debe tratar sobre la jornada fantasy: cómo iban los usuarios antes, durante y después, "
            "quién parecía ganador y quién remontó o se hundió, menciones a puntuaciones parciales (ej. \"30 puntos "
            "con 4 jugadores\"), cambios de posición en la clasificación general, jugadores clave y sus aportes.\n"
            "- Diferencia claramente entre 'overall_start_rank'/'overall_end_rank' (posición global antes/después) y "
            "'matchday_rank' (puesto específico en la jornada). Pon ejemplos explícitos si un manager gana la jornada "
            "pero sigue noveno en la general, o viceversa.\n"
            "- Usa metáforas épicas/humorísticas, referencias exageradas, y toca momentos como \"parecía que X iba bien "
            "con 30 puntos y 4 jugadores, pero Z e Y arruinaron su remontada\". Relaciona con la clasificación: "
            "rebases, escaladas, caídas, distancias con rivales. Siempre menciona posición inicial y final de los managers "
            "cuando expliques un sorpasso o una caída, diferenciando si ese cambio ocurre en la general o sólo en la jornada.\n"
            "- Utiliza principalmente el nombre real/preferred_name de cada manager o jugador y, como guiño ocasional, "
            "uno de sus apodos si existen. No abuses de los motes; el nombre real debe ser el protagonista.\n"
            "- Cierra con tres secciones tituladas exactamente 'El Crack', 'El Dandi' y 'Vaya día!' (1-2 frases cada una) "
            "centradas en managers/jugadores fantasy de la jornada.\n"
            "- Devuelve ÚNICAMENTE un JSON con la estructura exacta:\n"
            "  {\n"
            '    "article": "<texto completo>",\n'
            '    "highlights": ["• viñeta 1", "• viñeta 2", "• viñeta 3"]\n'
            "  }\n"
            "- Las viñetas (3-5) deben resumir giros clave de la jornada en tono breve y agudo.\n\n"
            "Datos de la jornada (incluyen puntuaciones, alias, posiciones, timelines, rachas):\n"
            f"{serialized}"
        )

    @staticmethod
    def _parse_json_response(content: str) -> Optional[Dict[str, Any]]:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # Attempt to extract JSON portion if the model wrapped it with text
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = content[start:end + 1]
                try:
                    parsed = json.loads(snippet)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass
        return None

    @staticmethod
    def _build_debug_snapshot(dataset: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = {}
        for team in dataset.get("teams", []):
            snapshot[team["team_name"]] = {
                "total_points_start": team.get("total_points_start"),
                "matchday_points": team.get("matchday_points"),
                "total_points_end": team.get("total_points_end"),
                "overall_start_rank": team.get("overall_start_rank"),
                "overall_end_rank": team.get("overall_end_rank"),
                "matchday_rank": team.get("matchday_rank"),
            }
        return snapshot

    @staticmethod
    def _validate_rank_consistency(dataset: Dict[str, Any]):
        for team in dataset.get("teams", []):
            start_rank = team.get("overall_start_rank")
            end_rank = team.get("overall_end_rank")
            change = team.get("position_change")
            if (
                isinstance(start_rank, int)
                and isinstance(end_rank, int)
                and change is not None
                and start_rank - end_rank != change
            ):
                raise ValueError(
                    f"Inconsistent rank data for {team.get('preferred_name') or team.get('team_name')}: "
                    f"overall_start_rank={start_rank}, overall_end_rank={end_rank}, position_change={change}"
                )

