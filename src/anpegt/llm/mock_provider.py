"""Mock LLM provider for testing -- returns structurally valid JSON responses."""

import hashlib
import json
from typing import Optional

from pydantic import BaseModel


class MockLLMProvider:
    """Deterministic mock provider that generates plausible Spanish-language responses.

    Uses the system prompt hash for deterministic variation and inspects the
    ``response_format`` schema to produce structurally valid output for every
    ANPEGT-POL model.
    """

    def __init__(self, default_temperature: float = 0.7):
        self.default_temperature = default_temperature

    # ------------------------------------------------------------------
    # Protocol-required method
    # ------------------------------------------------------------------

    def complete(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[type[BaseModel]] = None,
        temperature: float = 0.7,
    ) -> str:
        """Return a mock JSON string matching *response_format* if provided."""
        seed = self._seed_from_messages(messages)

        if response_format is not None:
            schema_name = response_format.__name__
            generator = self._GENERATORS.get(schema_name, self._generic_from_schema)
            data = generator(self, seed, response_format)
            return json.dumps(data, ensure_ascii=False)

        # No structured format requested -- return a simple Spanish text
        return json.dumps(
            {"respuesta": f"Respuesta mock generada (seed={seed[:8]})"},
            ensure_ascii=False,
        )

    # ------------------------------------------------------------------
    # Deterministic seed helper
    # ------------------------------------------------------------------

    @staticmethod
    def _seed_from_messages(messages: list[dict[str, str]]) -> str:
        combined = "".join(m.get("content", "") for m in messages)
        return hashlib.sha256(combined.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Per-schema generators
    # ------------------------------------------------------------------

    def _generate_sector_plan(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        idx = int(seed[:4], 16) % 1000
        policies = []
        for i in range(3):
            policies.append(
                {
                    "id": f"pol-{idx}-{i}",
                    "title": f"Política sectorial {i + 1}: mejora del sector",
                    "description": (
                        f"Propuesta concreta {i + 1} para avanzar en los objetivos "
                        "del cluster asignado, con impacto directo en la ciudadanía."
                    ),
                    "estimated_cost": ["bajo", "medio", "alto"][i % 3],
                    "timeframe": ["corto plazo", "medio plazo", "largo plazo"][i % 3],
                    "expected_impact": "Impacto positivo en indicadores clave del sector.",
                    "implementation_risk": "medio",
                }
            )
        return {
            "cycle_id": f"cycle-mock-{idx}",
            "cluster_id": f"cluster-{seed[:6]}",
            "priorities_used": {
                "economía": 0.35,
                "bienestar_social": 0.40,
                "medio_ambiente": 0.25,
            },
            "objectives": [
                "Mejorar la calidad de vida de los ciudadanos",
                "Reducir la desigualdad territorial",
                "Impulsar la innovación en el sector",
            ],
            "policies": policies,
            "intercluster_conflicts": [
                {
                    "with_cluster": "medio_ambiente",
                    "description": (
                        "Posible tensión entre crecimiento económico propuesto "
                        "y objetivos de sostenibilidad ambiental."
                    ),
                    "severity": "medium",
                }
            ],
            "rationale": (
                "Las propuestas se alinean con las prioridades ANP del ciclo actual "
                "y respetan los principios innegociables del partido."
            ),
            "budget_estimate": 15_000_000.0,
        }

    def _generate_global_plan(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        idx = int(seed[:4], 16) % 1000
        proposals = []
        for i in range(5):
            proposals.append(
                {
                    "id": f"gpol-{idx}-{i}",
                    "title": f"Propuesta consolidada {i + 1}",
                    "description": (
                        f"Medida global {i + 1} resultante de la integración "
                        "de los planes sectoriales."
                    ),
                    "estimated_cost": ["bajo", "medio", "alto"][i % 3],
                    "timeframe": "medio plazo",
                    "expected_impact": "Alto impacto transversal.",
                    "implementation_risk": "bajo",
                }
            )
        return {
            "cycle_id": f"cycle-mock-{idx}",
            "sector_plan_ids": [
                f"sp-{seed[:4]}-{j}" for j in range(3)
            ],
            "consolidated_proposals": proposals,
            "conflicts_resolved": [
                {
                    "conflict": {
                        "with_cluster": "medio_ambiente",
                        "description": "Tensión entre desarrollo y sostenibilidad.",
                        "severity": "medium",
                    },
                    "resolution": (
                        "Se prioriza la sostenibilidad aplicando condiciones "
                        "ambientales a las medidas de desarrollo económico."
                    ),
                    "priority_used": "medio_ambiente",
                }
            ],
            "conflicts_unresolved": [],
            "global_budget": 45_000_000.0,
            "coherence_score": 0.87,
            "summary": (
                "Plan global consolidado que integra las propuestas sectoriales, "
                "resuelve los conflictos intercluster identificados y se ajusta "
                "al techo fiscal establecido."
            ),
        }

    def _generate_communication_plan(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        idx = int(seed[:4], 16) % 1000
        return {
            "cycle_id": f"cycle-mock-{idx}",
            "segment_id": f"seg-{seed[:6]}",
            "key_messages": [
                "Nuestro compromiso es mejorar tu calidad de vida.",
                "Políticas concretas para tu día a día.",
                "Transparencia y responsabilidad en cada decisión.",
            ],
            "tone": "cercano y empático",
            "emphasis_areas": [
                "empleo",
                "sanidad",
                "educación",
            ],
            "full_text": (
                "Estimados ciudadanos: Presentamos un plan diseñado "
                "específicamente pensando en vosotros. Nuestras propuestas "
                "se centran en empleo de calidad, sanidad accesible y "
                "educación pública reforzada. Cada medida ha sido evaluada "
                "para garantizar su viabilidad y su impacto positivo en "
                "vuestra vida cotidiana."
            ),
            "cluster_focus": ["economía", "bienestar_social"],
        }

    def _generate_social_post(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        idx = int(seed[:4], 16) % 1000
        return {
            "cycle_id": f"cycle-mock-{idx}",
            "segment_id": f"seg-{seed[:6]}",
            "platform": "twitter",
            "main_text": (
                "🗳️ Nuestro plan pone a las personas en el centro: "
                "empleo digno, sanidad de calidad y educación para todos. "
                "¡Tu voz importa!"
            ),
            "hashtags": [
                "#PlanParaTodos",
                "#PolíticaCercana",
                "#FuturoJusto",
            ],
            "keywords_seo": ["plan político", "empleo", "sanidad", "educación"],
            "call_to_action": "Comparte si crees en un futuro mejor. 🔄",
            "suggested_visual": (
                "Infografía con los tres pilares del plan: empleo, sanidad, educación."
            ),
            "tone": "motivador y directo",
            "engagement_hooks": [
                "¿Sabías que nuestro plan ya tiene respaldo técnico?",
                "Desliza para ver los datos →",
            ],
            "thread_pieces": [
                "1/ Empleo digno: creación de 50.000 puestos en sectores estratégicos.",
                "2/ Sanidad: reducción de listas de espera en un 30%.",
                "3/ Educación: becas universales para FP y universidad.",
            ],
            "best_posting_time": "martes 10:00",
            "cluster_tags": ["economía", "bienestar_social"],
        }

    def _generate_speech(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        idx = int(seed[:4], 16) % 1000
        return {
            "cycle_id": f"cycle-mock-{idx}",
            "event_type": "mitin",
            "target_audience": "ciudadanía general",
            "duration_minutes": 20,
            "opening": (
                "Buenas tardes. Hoy estamos aquí porque creemos en un futuro "
                "mejor para todos. Un futuro construido con propuestas serias, "
                "datos contrastados y el compromiso firme de no dejar a nadie atrás."
            ),
            "body_sections": [
                {
                    "topic": "Empleo y economía",
                    "key_message": (
                        "Crearemos las condiciones para un empleo digno y estable."
                    ),
                    "supporting_data": "Tasa de desempleo actual: 12%. Objetivo: 8% en 4 años.",
                    "emotional_anchor": (
                        "Cada familia merece la seguridad de llegar a fin de mes."
                    ),
                    "policy_reference": "Plan de empleo sectorial POL-ECO-001",
                },
                {
                    "topic": "Sanidad pública",
                    "key_message": (
                        "Una sanidad pública fuerte es un derecho, no un privilegio."
                    ),
                    "supporting_data": "Inversión prevista: 2.000 M€ en infraestructura sanitaria.",
                    "emotional_anchor": "Que nadie tenga que elegir entre su salud y su bolsillo.",
                    "policy_reference": "Plan sanitario POL-SAN-003",
                },
                {
                    "topic": "Educación",
                    "key_message": (
                        "Invertir en educación es invertir en el futuro de nuestros hijos."
                    ),
                    "supporting_data": "Becas para el 100% de estudiantes de FP.",
                    "emotional_anchor": (
                        "Ningún joven debería renunciar a formarse por falta de recursos."
                    ),
                    "policy_reference": "Plan educativo POL-EDU-002",
                },
            ],
            "closing": (
                "El cambio no se promete: se construye. Y lo construimos juntos, "
                "paso a paso, propuesta a propuesta. Contamos con vosotros. ¡Adelante!"
            ),
            "soundbites": [
                "El cambio no se promete, se construye.",
                "Nadie se queda atrás.",
                "Política con datos, no con titulares.",
            ],
            "qa_preparation": [
                {
                    "question": "¿Cómo van a financiar estas medidas?",
                    "answer": (
                        "Con un plan fiscal riguroso que respeta el techo de gasto "
                        "y prioriza la eficiencia en cada euro invertido."
                    ),
                },
                {
                    "question": "¿Qué diferencia su plan del de otros partidos?",
                    "answer": (
                        "Nuestras propuestas están respaldadas por análisis multicriterio "
                        "y validadas por datos reales, no por eslóganes."
                    ),
                },
            ],
            "tone": "inspirador pero riguroso",
            "territorial_references": [
                "Nuestra comunidad",
                "Cada municipio",
                "Los barrios de nuestra ciudad",
            ],
        }

    def _generic_from_schema(
        self, seed: str, schema: type[BaseModel]
    ) -> dict:
        """Fallback: generate a minimal valid instance from the JSON schema."""
        json_schema = schema.model_json_schema()
        return self._fill_schema(json_schema, seed, 0)

    # ------------------------------------------------------------------
    # Recursive schema filler for the generic fallback
    # ------------------------------------------------------------------

    def _fill_schema(self, schema: dict, seed: str, depth: int) -> object:
        """Recursively produce a value conforming to *schema*."""
        if "$defs" in schema and "properties" in schema:
            return self._fill_object(schema, schema.get("$defs", {}), seed, depth)

        ref = schema.get("$ref")
        if ref:
            return self._fill_schema(
                self._resolve_ref(ref, schema), seed, depth
            )

        typ = schema.get("type", "string")
        if typ == "object":
            return self._fill_object(schema, {}, seed, depth)
        if typ == "array":
            items = schema.get("items", {"type": "string"})
            return [self._fill_schema(items, seed, depth + 1)]
        if typ == "integer":
            return int(seed[:4], 16) % 100
        if typ == "number":
            return float(int(seed[:4], 16) % 10000) / 100.0
        if typ == "boolean":
            return int(seed[0], 16) % 2 == 0
        # string
        return f"mock-{seed[:8]}"

    def _fill_object(
        self, schema: dict, defs: dict, seed: str, depth: int
    ) -> dict:
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        result: dict = {}
        for key, prop_schema in props.items():
            if key not in required and depth > 2:
                continue
            resolved = self._resolve_inline(prop_schema, defs)
            result[key] = self._fill_schema(resolved, seed, depth + 1)
        return result

    @staticmethod
    def _resolve_ref(ref: str, root_schema: dict) -> dict:
        parts = ref.lstrip("#/").split("/")
        node = root_schema
        for p in parts:
            node = node[p]
        return node

    @staticmethod
    def _resolve_inline(schema: dict, defs: dict) -> dict:
        ref = schema.get("$ref")
        if ref and defs:
            name = ref.rsplit("/", 1)[-1]
            return defs.get(name, schema)
        # anyOf (Optional fields)
        if "anyOf" in schema:
            for option in schema["anyOf"]:
                if option.get("type") != "null":
                    ref2 = option.get("$ref")
                    if ref2 and defs:
                        name = ref2.rsplit("/", 1)[-1]
                        return defs.get(name, option)
                    return option
        return schema

    # ------------------------------------------------------------------
    # Registry mapping schema names → generator methods
    # ------------------------------------------------------------------

    _GENERATORS: dict = {
        "SectorPlan": _generate_sector_plan,
        "GlobalPlan": _generate_global_plan,
        "CommunicationPlan": _generate_communication_plan,
        "SocialPost": _generate_social_post,
        "Speech": _generate_speech,
    }
