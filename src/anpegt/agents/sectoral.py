"""Sectoral agent -- generates a plan for a single thematic cluster."""

import json

from anpegt.agents.base import BaseAgent
from anpegt.schema.plan import SectorPlan


class SectoralAgent(BaseAgent):
    """Generates a :class:`SectorPlan` for a specific thematic cluster.

    Expected *context* keys:

    * ``cluster`` -- :class:`ClusterDef` (or dict equivalent)
    * ``priorities`` -- ``dict[str, float]`` from ANP computation
    * ``party_ideals`` -- :class:`PartyIdeals` (or dict equivalent)
    * ``previous_plan`` -- optional prior :class:`SectorPlan`
    * ``corpus_context`` -- ``list[str]`` relevant text snippets from RAG
    """

    output_schema = SectorPlan
    agent_name = "sectoral"

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        cluster = context["cluster"]
        priorities = context["priorities"]
        party_ideals = context["party_ideals"]
        previous_plan = context.get("previous_plan")
        corpus_context = context.get("corpus_context", [])

        # Serialise complex objects to JSON-friendly dicts
        cluster_json = (
            cluster.model_dump() if hasattr(cluster, "model_dump") else cluster
        )
        ideals_json = (
            party_ideals.model_dump()
            if hasattr(party_ideals, "model_dump")
            else party_ideals
        )

        system_prompt = (
            "Eres un experto en políticas públicas especializado en el sector "
            f"\"{cluster_json.get('name', cluster_json.get('id', 'desconocido'))}\". "
            "Tu tarea es elaborar un plan sectorial concreto y viable.\n\n"
            "INSTRUCCIONES:\n"
            "1. Propón entre 3 y 5 políticas concretas, cada una con título, "
            "descripción, coste estimado (bajo/medio/alto), plazo de ejecución, "
            "impacto esperado y riesgo de implementación.\n"
            "2. Estima el presupuesto total del plan.\n"
            "3. Identifica posibles conflictos con otros sectores.\n"
            "4. Justifica cómo las propuestas se alinean con las prioridades ANP "
            "y los ideales del partido.\n"
            "5. Redacta todo en español.\n\n"
            "Responde EXCLUSIVAMENTE con un JSON válido que cumpla el esquema "
            "de SectorPlan."
        )

        user_content_parts = [
            f"**Cluster/Sector:** {json.dumps(cluster_json, ensure_ascii=False)}",
            f"**Prioridades ANP:** {json.dumps(priorities, ensure_ascii=False)}",
            f"**Ideales del partido:** {json.dumps(ideals_json, ensure_ascii=False)}",
        ]

        if previous_plan:
            prev_json = (
                previous_plan.model_dump(mode="json")
                if hasattr(previous_plan, "model_dump")
                else previous_plan
            )
            user_content_parts.append(
                f"**Plan sectorial previo (para iterar):** "
                f"{json.dumps(prev_json, ensure_ascii=False)}"
            )

        if corpus_context:
            snippets = "\n---\n".join(corpus_context[:10])
            user_content_parts.append(
                f"**Contexto del corpus (RAG):**\n{snippets}"
            )

        user_prompt = "\n\n".join(user_content_parts)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
