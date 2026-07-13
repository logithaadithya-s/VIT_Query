import json
import os
from typing import Any

import httpx

from app.services.field_analyzer import RESEARCH_FIELDS, analyze_field_landscape


AGENT_PROMPT = """You are a research intelligence agent for a college. Analyze the institution's research paper repository and provide strategic insights.

Based on the data below, respond ONLY with valid JSON in this exact structure:
{
  "active_research_areas": [
    {"field": "...", "paper_count": 0, "summary": "What's being researched and why it matters", "key_themes": ["theme1", "theme2"]}
  ],
  "underexplored_areas": [
    {"field": "...", "paper_count": 0, "gap_analysis": "Why this is under-represented", "research_scope": "Specific directions faculty could pursue"}
  ],
  "emerging_opportunities": [
    {"field": "...", "rationale": "Why this is emerging", "suggested_projects": ["project idea 1", "project idea 2"]}
  ],
  "strategic_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "executive_summary": "2-3 sentence overview for college leadership"
}

Repository data:
{context}
"""


def _build_context(papers: list[dict], landscape: dict) -> str:
    paper_summaries = []
    for paper in papers[:20]:
        paper_summaries.append(
            f"- {paper.get('title')} | Field: {paper.get('primary_field')} | "
            f"Dept: {paper.get('department')} | Keywords: {', '.join(paper.get('keywords', [])[:5])}"
        )

    top_fields = landscape.get("top_researched_fields", [])
    underexplored = landscape.get("underexplored_fields", [])[:8]
    opportunities = landscape.get("opportunity_fields", [])[:6]

    return json.dumps(
        {
            "total_papers": landscape.get("total_papers", 0),
            "top_researched_fields": top_fields,
            "underexplored_fields": underexplored,
            "opportunity_signals": opportunities,
            "trending_keywords": landscape.get("trending_keywords", [])[:10],
            "sample_papers": paper_summaries,
            "all_field_taxonomy": list(RESEARCH_FIELDS.keys()),
        },
        indent=2,
    )


def _rules_based_insights(papers: list[dict], landscape: dict) -> dict[str, Any]:
    top = landscape.get("top_researched_fields", [])
    under = landscape.get("underexplored_fields", [])
    opportunities = landscape.get("opportunity_fields", [])

    active = []
    for item in top[:5]:
        if item["count"] > 0:
            related = [
                p["title"]
                for p in papers
                if p.get("primary_field") == item["field"]
            ][:3]
            active.append(
                {
                    "field": item["field"],
                    "paper_count": item["count"],
                    "summary": f"Active research hub with {item['count']} paper(s). Faculty are producing work in this domain.",
                    "key_themes": [
                        kw["keyword"]
                        for kw in landscape.get("trending_keywords", [])[:4]
                    ],
                    "sample_papers": related,
                }
            )

    gaps = []
    for item in under[:8]:
        gaps.append(
            {
                "field": item["field"],
                "paper_count": item["count"],
                "gap_analysis": item.get("scope_note", "Limited representation in the repository."),
                "research_scope": f"Faculty can pioneer work in {item['field']} — high potential for publications and grants.",
            }
        )

    emerging = []
    for item in opportunities[:6]:
        emerging.append(
            {
                "field": item["field"],
                "rationale": item.get("reason", ""),
                "suggested_projects": [item.get("suggested_action", "Explore interdisciplinary research")],
            }
        )

    total = landscape.get("total_papers", 0)
    top_field = top[0]["field"] if top and top[0]["count"] > 0 else "None yet"

    return {
        "agent_used": "rules_engine",
        "agent_label": "Built-in Research Advisor (no API key required)",
        "active_research_areas": active,
        "underexplored_areas": gaps,
        "emerging_opportunities": emerging,
        "strategic_recommendations": [
            f"Double down on {top_field} while diversifying into underrepresented fields.",
            "Encourage cross-department collaboration on emerging opportunity areas.",
            "Set up a monthly research gap review using this agent dashboard.",
        ],
        "executive_summary": (
            f"The repository contains {total} papers across "
            f"{len([f for f in top if f['count'] > 0])} active fields. "
            f"Significant gaps exist in {len(under)} domains — ideal targets for new faculty projects and student theses."
        ),
        "integration_suggestions": get_agent_integration_suggestions(),
    }


def get_agent_integration_suggestions() -> list[dict]:
    return [
        {
            "name": "OpenAI GPT-4o",
            "type": "cloud_llm",
            "env_var": "OPENAI_API_KEY",
            "best_for": "Rich narrative gap analysis, project ideation, executive summaries",
            "setup": "Set OPENAI_API_KEY in .env — agent auto-activates on next insights request",
        },
        {
            "name": "Anthropic Claude",
            "type": "cloud_llm",
            "env_var": "ANTHROPIC_API_KEY",
            "best_for": "Long-context analysis of full paper corpora, nuanced field mapping",
            "setup": "Set ANTHROPIC_API_KEY — extend research_agent.py with Claude API call",
        },
        {
            "name": "Ollama (Local)",
            "type": "local_llm",
            "env_var": "OLLAMA_BASE_URL",
            "best_for": "Privacy-sensitive institutions, offline deployment, zero API cost",
            "setup": "Run `ollama run llama3.2` and set OLLAMA_BASE_URL=http://localhost:11434",
        },
        {
            "name": "LangGraph Research Agent",
            "type": "agent_framework",
            "env_var": None,
            "best_for": "Multi-step workflows: retrieve papers → classify → compare → recommend",
            "setup": "Build a LangGraph agent that calls this API and adds web search for trend validation",
        },
        {
            "name": "Cursor / Custom MCP Agent",
            "type": "dev_agent",
            "env_var": None,
            "best_for": "Automated repo analysis, PR reviews on research submissions",
            "setup": "Connect via MCP tools to /api/analytics/agent-insights endpoint",
        },
    ]


async def _call_openai(context: str) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = AGENT_PROMPT.format(context=context)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": "You are a research intelligence agent. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        parsed["agent_used"] = "openai"
        parsed["agent_label"] = f"OpenAI {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}"
        parsed["integration_suggestions"] = get_agent_integration_suggestions()
        return parsed


async def _call_ollama(context: str) -> dict[str, Any] | None:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    if not os.getenv("OLLAMA_BASE_URL") and not _ollama_is_reachable(base_url):
        return None

    prompt = AGENT_PROMPT.format(context=context)
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt + "\n\nRespond with JSON only.",
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
        content = response.json()["response"]
        parsed = json.loads(content)
        parsed["agent_used"] = "ollama"
        parsed["agent_label"] = f"Ollama {model} (local)"
        parsed["integration_suggestions"] = get_agent_integration_suggestions()
        return parsed


def _ollama_is_reachable(base_url: str) -> bool:
    try:
        with httpx.Client(timeout=2.0) as client:
            client.get(f"{base_url}/api/tags")
        return True
    except Exception:
        return False


async def generate_research_insights(papers: list[dict]) -> dict[str, Any]:
    landscape = analyze_field_landscape(papers)
    context = _build_context(papers, landscape)

    for caller in (_call_openai, _call_ollama):
        try:
            result = await caller(context)
            if result:
                return result
        except Exception:
            continue

    return _rules_based_insights(papers, landscape)
