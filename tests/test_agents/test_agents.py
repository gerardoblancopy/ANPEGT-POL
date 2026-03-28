"""Tests for LLM agents."""

from anpegt.agents.sectoral import SectoralAgent
from anpegt.agents.orchestrator import OrchestratorAgent
from anpegt.agents.communication import CommunicationAgent
from anpegt.agents.social_content import SocialContentAgent
from anpegt.agents.speechwriter import SpeechWriterAgent
from anpegt.schema.plan import SectorPlan, GlobalPlan, CommunicationPlan, SocialPost, Speech


def test_sectoral_agent(mock_llm):
    agent = SectoralAgent(llm=mock_llm)
    context = {
        "cluster": {"id": "salud", "name": "Salud", "description": "Salud pública", "keywords": ["salud"]},
        "priorities": {"salud_plan": 0.3, "equidad": 0.2},
        "party_ideals": {"name": "Test", "non_negotiable_principles": [], "fiscal_ceiling": 1e9, "ideological_axes": {}},
        "corpus_context": [],
        "cycle_id": "c1",
    }
    result = agent.run(context)
    assert isinstance(result, SectorPlan)
    assert len(result.policies) > 0


def test_orchestrator_agent(mock_llm):
    agent = OrchestratorAgent(llm=mock_llm)
    context = {
        "sector_plans": [{"cluster_id": "salud", "policies": [], "rationale": "Test"}],
        "party_ideals": {"name": "Test", "non_negotiable_principles": [], "fiscal_ceiling": 1e9, "ideological_axes": {}},
        "priorities": {"salud": 0.5},
        "fiscal_ceiling": 1e9,
        "cycle_id": "c1",
    }
    result = agent.run(context)
    assert isinstance(result, GlobalPlan)


def test_communication_agent(mock_llm):
    agent = CommunicationAgent(llm=mock_llm)
    context = {
        "global_plan": {"summary": "Plan de prueba", "consolidated_proposals": []},
        "segment": {"id": "seg_a", "name": "Segmento A", "description": "Test", "priority_issues": ["salud"]},
        "cycle_id": "c1",
    }
    result = agent.run(context)
    assert isinstance(result, CommunicationPlan)
    assert len(result.key_messages) > 0


def test_social_content_agent(mock_llm):
    agent = SocialContentAgent(llm=mock_llm)
    context = {
        "global_plan": {"summary": "Plan de prueba", "consolidated_proposals": []},
        "segment": {"id": "seg_a", "name": "Segmento A"},
        "platform": "twitter",
        "communication_plan": {"key_messages": ["Msg1"], "tone": "informativo"},
        "cycle_id": "c1",
    }
    result = agent.run(context)
    assert isinstance(result, SocialPost)


def test_speechwriter_agent(mock_llm):
    agent = SpeechWriterAgent(llm=mock_llm)
    context = {
        "global_plan": {"summary": "Plan de prueba", "consolidated_proposals": []},
        "event_config": {"event_type": "rally", "audience": "general", "duration": 20},
        "party_ideals": {"name": "Test", "non_negotiable_principles": []},
        "cycle_id": "c1",
    }
    result = agent.run(context)
    assert isinstance(result, Speech)
    assert len(result.soundbites) > 0
