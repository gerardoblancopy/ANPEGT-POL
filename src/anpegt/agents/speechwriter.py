"""Speech-writer agent -- drafts speeches for political events."""

import json

from anpegt.agents.base import BaseAgent
from anpegt.schema.plan import Speech


class SpeechWriterAgent(BaseAgent):
    """Generates a :class:`Speech` tailored to a specific event, audience,
    and voter segment.

    Expected *context* keys:

    * ``global_plan`` -- :class:`GlobalPlan`
    * ``event_config`` -- ``dict`` with keys: ``event_type``, ``audience``,
      ``duration`` (minutes), ``territory``, ``themes``
    * ``party_ideals`` -- :class:`PartyIdeals`
    * ``segment`` -- :class:`VoterSegmentDef`
    """

    output_schema = Speech
    agent_name = "speechwriter"

    def build_prompt(self, context: dict) -> list[dict[str, str]]:
        global_plan = context["global_plan"]
        event_config = context.get("event_config", {})
        party_ideals = context["party_ideals"]
        segment = context.get("segment")

        def _dump(obj: object) -> object:
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return obj

        plan_json = _dump(global_plan)
        ideals_json = _dump(party_ideals)
        segment_json = _dump(segment) if segment else {}

        event_type = event_config.get("event_type", "acto público")
        audience = event_config.get("audience", "ciudadanía general")
        duration = event_config.get("duration", 20)
        territory = event_config.get("territory", "")
        themes = event_config.get("themes", [])

        system_prompt = (
            "Eres un escritor de discursos políticos de alto nivel. "
            f"Tu tarea es redactar un discurso para un **{event_type}** "
            f"dirigido a **{audience}**, con una duración aproximada de "
            f"**{duration} minutos**.\n\n"
            "INSTRUCCIONES:\n"
            "1. Escribe una apertura potente que conecte emocionalmente.\n"
            "2. Desarrolla secciones temáticas vinculadas a políticas concretas "
            "del plan global. Cada sección debe tener: tema, mensaje clave, "
            "datos de apoyo, ancla emocional y referencia a la política.\n"
            "3. Genera un cierre memorable con llamada a la acción.\n"
            "4. Incluye 3-5 soundbites aptos para titulares de prensa.\n"
            "5. Prepara respuestas para posibles preguntas del público o medios.\n"
            "6. El tono debe ser apropiado para el tipo de evento y la audiencia.\n"
        )

        if territory:
            system_prompt += (
                f"7. Incluye referencias territoriales a **{territory}**.\n"
            )

        if themes:
            themes_str = ", ".join(themes)
            system_prompt += (
                f"8. Enfócate especialmente en estos temas: {themes_str}.\n"
            )

        system_prompt += (
            "\nTodo en español.\n\n"
            "Responde EXCLUSIVAMENTE con un JSON válido que cumpla el esquema "
            "de Speech."
        )

        user_prompt = (
            f"**Tipo de evento:** {event_type}\n"
            f"**Audiencia:** {audience}\n"
            f"**Duración:** {duration} minutos\n"
            f"**Territorio:** {territory or 'General'}\n\n"
            f"**Plan global:**\n"
            f"{json.dumps(plan_json, ensure_ascii=False, indent=2)}\n\n"
            f"**Ideales del partido:** {json.dumps(ideals_json, ensure_ascii=False)}\n\n"
            f"**Segmento electoral:** {json.dumps(segment_json, ensure_ascii=False)}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
