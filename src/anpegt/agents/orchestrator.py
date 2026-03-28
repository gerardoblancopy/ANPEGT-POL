"""Orchestrator agent -- consolidates sector plans into a global plan."""

import json

from anpegt.agents.base import BaseAgent
from anpegt.schema.plan import GlobalPlan


class OrchestratorAgent(BaseAgent):
    """Consolidates multiple :class:`SectorPlan` objects into a single
    :class:`GlobalPlan`, resolving cross-sector conflicts and enforcing
    budget and coherence constraints.

    Expected *context* keys:

    * ``sector_plans`` -- ``list[SectorPlan]`` (or list of dicts)
    * ``party_ideals`` -- :class:`PartyIdeals`
    * ``priorities`` -- ``dict[str, float]``
    * ``fiscal_ceiling`` -- ``float`` maximum budget
    """

    output_schema = GlobalPlan
    agent_name = "orchestrator"

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        sector_plans = context["sector_plans"]
        party_ideals = context["party_ideals"]
        priorities = context["priorities"]
        fiscal_ceiling = context.get("fiscal_ceiling", 0.0)

        def _dump(obj: object) -> object:
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return obj

        plans_json = [_dump(sp) for sp in sector_plans]
        ideals_json = _dump(party_ideals)

        system_prompt = (
            "Eres el orquestador estratégico de un partido político. "
            "Tu función es consolidar los planes sectoriales en un plan "
            "global coherente.\n\n"
            "INSTRUCCIONES:\n"
            "1. Detecta conflictos entre los planes sectoriales y resuélvelos "
            "priorizando según las prioridades ANP y los principios innegociables "
            "del partido.\n"
            "2. Verifica que el plan global sea coherente con los ideales del partido.\n"
            f"3. El presupuesto total NO debe superar el techo fiscal de "
            f"{fiscal_ceiling:,.2f} €.\n"
            "4. Si es necesario, recorta o ajusta propuestas para encajar en el "
            "presupuesto.\n"
            "5. Genera una puntuación de coherencia global (0.0 a 1.0).\n"
            "6. Redacta todo en español.\n\n"
            "Responde EXCLUSIVAMENTE con un JSON válido que cumpla el esquema "
            "de GlobalPlan."
        )

        user_prompt = (
            f"**Planes sectoriales:**\n"
            f"{json.dumps(plans_json, ensure_ascii=False, indent=2)}\n\n"
            f"**Prioridades ANP:** {json.dumps(priorities, ensure_ascii=False)}\n\n"
            f"**Ideales del partido:** {json.dumps(ideals_json, ensure_ascii=False)}\n\n"
            f"**Techo fiscal:** {fiscal_ceiling:,.2f} €"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
