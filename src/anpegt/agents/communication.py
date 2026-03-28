"""Communication agent -- tailors the global plan for a voter segment."""

import json

from anpegt.agents.base import BaseAgent
from anpegt.schema.plan import CommunicationPlan


class CommunicationAgent(BaseAgent):
    """Produces a :class:`CommunicationPlan` that frames the global plan
    for a specific voter segment.

    Expected *context* keys:

    * ``global_plan`` -- :class:`GlobalPlan`
    * ``segment`` -- :class:`VoterSegmentDef`
    * ``segment_priorities`` -- ``dict[str, float]`` priorities for this segment
    """

    output_schema = CommunicationPlan
    agent_name = "communication"

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        global_plan = context["global_plan"]
        segment = context["segment"]
        segment_priorities = context.get("segment_priorities", {})

        def _dump(obj: object) -> object:
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return obj

        plan_json = _dump(global_plan)
        segment_json = _dump(segment)

        system_prompt = (
            "Eres un experto en comunicación política. Tu tarea es adaptar "
            "un plan político global para que conecte con un segmento "
            "específico del electorado.\n\n"
            "INSTRUCCIONES:\n"
            "1. Analiza el perfil del segmento y sus prioridades.\n"
            "2. Selecciona las propuestas del plan global más relevantes "
            "para este segmento.\n"
            "3. Genera entre 3 y 5 mensajes clave, claros y memorables.\n"
            "4. Define el tono apropiado (cercano, técnico, emocional, etc.).\n"
            "5. Identifica las áreas de énfasis y los clusters temáticos a destacar.\n"
            "6. Redacta un texto completo de comunicación adaptado.\n"
            "7. Todo en español.\n\n"
            "Responde EXCLUSIVAMENTE con un JSON válido que cumpla el esquema "
            "de CommunicationPlan."
        )

        user_prompt = (
            f"**Plan global:**\n"
            f"{json.dumps(plan_json, ensure_ascii=False, indent=2)}\n\n"
            f"**Segmento electoral:** {json.dumps(segment_json, ensure_ascii=False)}\n\n"
            f"**Prioridades del segmento:** "
            f"{json.dumps(segment_priorities, ensure_ascii=False)}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
