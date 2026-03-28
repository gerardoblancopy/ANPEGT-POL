"""Social content agent -- creates platform-optimised social media posts."""

import json

from anpegt.agents.base import BaseAgent
from anpegt.schema.plan import SocialPost

# Character limits per platform.
PLATFORM_CHAR_LIMITS: dict[str, int] = {
    "twitter": 280,
    "instagram": 2200,
    "facebook": 63206,
    "tiktok": 4000,
    "linkedin": 3000,
}


class SocialContentAgent(BaseAgent):
    """Generates a :class:`SocialPost` optimised for a given social-media
    platform and voter segment.

    Expected *context* keys:

    * ``global_plan`` -- :class:`GlobalPlan`
    * ``segment`` -- :class:`VoterSegmentDef`
    * ``platform`` -- ``str`` (twitter, instagram, facebook, tiktok, linkedin)
    * ``communication_plan`` -- :class:`CommunicationPlan`
    """

    output_schema = SocialPost
    agent_name = "social_content"

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        global_plan = context["global_plan"]
        segment = context["segment"]
        platform = context.get("platform", "twitter")
        communication_plan = context.get("communication_plan")

        def _dump(obj: object) -> object:
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return obj

        plan_json = _dump(global_plan)
        segment_json = _dump(segment)
        comm_json = _dump(communication_plan) if communication_plan else {}

        char_limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 2000)

        system_prompt = (
            "Eres un experto en marketing político digital y redes sociales. "
            f"Tu tarea es crear contenido optimizado para **{platform}**.\n\n"
            "INSTRUCCIONES:\n"
            f"1. El texto principal NO debe superar los {char_limit} caracteres "
            f"(límite de {platform}).\n"
            "2. Genera hashtags relevantes y palabras clave SEO.\n"
            "3. Incluye un call-to-action (CTA) claro.\n"
            "4. Propón ganchos de engagement (preguntas, datos impactantes, etc.).\n"
            "5. Si la plataforma lo permite, sugiere un hilo (thread_pieces) para "
            "desarrollar el mensaje.\n"
            "6. Sugiere el mejor horario de publicación.\n"
            "7. Sugiere un visual o recurso gráfico.\n"
            "8. Adapta el tono al segmento y a la plataforma.\n"
            "9. Todo en español.\n\n"
            "Responde EXCLUSIVAMENTE con un JSON válido que cumpla el esquema "
            "de SocialPost."
        )

        user_prompt = (
            f"**Plataforma:** {platform} (límite: {char_limit} caracteres)\n\n"
            f"**Plan global:**\n"
            f"{json.dumps(plan_json, ensure_ascii=False, indent=2)}\n\n"
            f"**Segmento electoral:** {json.dumps(segment_json, ensure_ascii=False)}\n\n"
            f"**Plan de comunicación:** {json.dumps(comm_json, ensure_ascii=False)}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
