"""OpenRouter API integration for Cover Letter Agent."""
import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

OPENROUTER_API_KEY = os.getenv("OpenRouterApi")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "gemini_flash": "google/gemini-3-flash-preview",#"google/gemini-2.0-flash-001",
    "gpt4o": "openai/gpt-5.2",
    "claude_sonnet": "anthropic/claude-sonnet-4.5",
    "claude_opus": "anthropic/claude-opus-4.5",
}


def call_llm(model_key: str, prompt: str, system_prompt: str = "", max_tokens: int = 800) -> str:
    """Call LLM via OpenRouter API."""
    model = MODELS.get(model_key, model_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def classify_job(job_description: str) -> dict:
    """Classify job as engineering or finance."""
    prompt = f"""Classify this job into EXACTLY one category.

Job Description:
{job_description}

Response format (nothing else):
CATEGORY: engineering OR finance
CONFIDENCE: percentage"""

    response = call_llm("gemini_flash", prompt, max_tokens=50)

    category = "engineering"
    confidence = 80
    for line in response.strip().split("\n"):
        if "CATEGORY:" in line.upper():
            cat = line.split(":")[-1].strip().lower()
            category = "finance" if "finance" in cat else "engineering"
        elif "CONFIDENCE:" in line.upper():
            try:
                confidence = int(line.split(":")[-1].strip().replace("%", ""))
            except:
                pass
    return {"category": category, "confidence": confidence}


def generate_cover_letter(job_description: str, bio: str, model_key: str, insights: str = "") -> str:
    """Generate cover letter with improved prompts."""

    insights_section = f"\nUSER'S PREFERENCES:\n{insights}\n" if insights else ""

    system_prompt = """You write professional cover letters. Be concise and specific.
IMPORTANT RULES:
- Do NOT draw parallels between physics/academia and finance/business
- Focus on: data processing skills, independent research ability, full project ownership, ML/AI expertise
- Candidate's motivation: inspiration of working with data, career growth, competitive environment, clear goals
- Do not try to make 100% match between candidate background and job description. Instead, highlight strengths as a data-driven problem solver with strong independent work ethic and passion for ML/AI.
- Maximum 300 words, 3 paragraphs
- No generic phrases, no "I am excited", no "team player"
- No closing signature needed"""

    prompt = f"""Write a cover letter for this job.

JOB:
{job_description}

CANDIDATE:
{bio}
{insights_section}
Requirements:
- 250-300 words, 3 paragraphs
- Strong opening with specific achievement
- Highlight great potential as a data-driven problem solver with strong independent work ethic and passion for ML/AI.
- Show relevant skills (on basic level, and only if really relevant. I dint want to match 100%), NO background similarities
- End with genuine interest in the role

Output ONLY the letter text."""

    return call_llm(model_key, prompt, system_prompt, max_tokens=600)


def critique_and_fuse(version_a: str, version_b: str, job_description: str) -> dict:
    """Critic analyzes both versions (~300 words analysis) and creates fusion (~300 words)."""

    prompt = f"""You are an expert cover letter critic.

JOB:
{job_description}

VERSION A (GPT):
{version_a}

VERSION B (Claude):
{version_b}

TASK:
Write a detailed analysis (~300 words total for analysis) covering:
1. VERSION A - Strengths (2-3 points with explanation)
2. VERSION A - Weaknesses (2-3 points with explanation)
3. VERSION B - Strengths (2-3 points with explanation)
4. VERSION B - Weaknesses (2-3 points with explanation)

Then create a FUSION letter (~300 words, 3 paragraphs) taking the best from both.

IMPORTANT: Do NOT create false parallels between physics/academia and business.
Focus on great potential as researcher and independent solver who learning fast and already have prominent achievements, and really relevant skills: data processing, independent research, project ownership, ML/AI.

Format:
===ANALYSIS===
[Your detailed ~300 word analysis here]

===FUSION===
[Your ~300 word fused cover letter here]"""

    response = call_llm("claude_opus", prompt, max_tokens=1200)

    analysis = ""
    fusion = ""

    if "===ANALYSIS===" in response and "===FUSION===" in response:
        parts = response.split("===FUSION===")
        analysis = parts[0].replace("===ANALYSIS===", "").strip()
        fusion = parts[1].strip() if len(parts) > 1 else ""
    else:
        # Fallback parsing
        fusion = response

    return {"analysis_text": analysis, "fusion_letter": fusion}


def edit_cover_letter(current_letter: str, feedback: str, bio: str, insights: str, model_key: str) -> str:
    """Edit cover letter with bio context and insights."""

    prompt = f"""Edit this cover letter based on feedback.

CURRENT LETTER:
{current_letter}

CANDIDATE BACKGROUND (for reference):
{bio}

USER'S ACCUMULATED PREFERENCES:
{insights}

USER'S FEEDBACK THIS ROUND:
{feedback}

RULES:
- Implement ALL requested changes
- Keep 250-300 words, 3 paragraphs
- Do NOT draw physics-business parallels
- Focus on data skills, independent work, ML/AI expertise
- No signature needed

Output ONLY the edited letter."""

    return call_llm(model_key, prompt, max_tokens=600)


def extract_insights_from_feedback(user_likes: str, user_dislikes: str, current_insights: dict) -> dict:
    """Use LLM to extract structured insights from user feedback."""
    from memory import extract_insights_prompt

    prompt = extract_insights_prompt(user_likes, user_dislikes, current_insights)
    response = call_llm("gemini_flash", prompt, max_tokens=300)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass

    return {"tone": [], "content": [], "structure": [], "avoid": []}


def compact_insights(current_insights: dict) -> dict:
    """Use LLM to compact and clean up accumulated insights."""
    from memory import compact_insights_prompt

    # Skip if insights are empty
    if not any(current_insights.get(k) for k in ["tone", "content", "structure", "avoid"]):
        return current_insights

    prompt = compact_insights_prompt(current_insights)
    response = call_llm("gemini_flash", prompt, max_tokens=400)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            result["history"] = current_insights.get("history", [])
            return result
    except:
        pass

    return current_insights
