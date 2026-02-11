"""Long-term memory management for Cover Letter Agent."""
import json
from pathlib import Path
from datetime import datetime

INSIGHTS_FILE = Path("/home/anton/CV_agent/insights.json")


def load_insights() -> dict:
    """Load accumulated insights from file."""
    if INSIGHTS_FILE.exists():
        with open(INSIGHTS_FILE, "r") as f:
            return json.load(f)
    return {
        "tone": [],
        "content": [],
        "structure": [],
        "avoid": [],
        "history": []
    }


def save_insights(insights: dict):
    """Save insights to file."""
    with open(INSIGHTS_FILE, "w") as f:
        json.dump(insights, f, indent=2)


def extract_insights_prompt(user_likes: str, user_dislikes: str, current_insights: dict) -> str:
    """Create prompt for insight extraction from new feedback."""
    existing = f"""
Current saved insights:
- Tone preferences: {', '.join(current_insights.get('tone', [])) or 'none yet'}
- Content preferences: {', '.join(current_insights.get('content', [])) or 'none yet'}
- Structure preferences: {', '.join(current_insights.get('structure', [])) or 'none yet'}
- Things to avoid: {', '.join(current_insights.get('avoid', [])) or 'none yet'}
"""

    return f"""Extract actionable insights from user feedback for future cover letters.

USER SAID THEY LIKE:
{user_likes}

USER SAID THEY DISLIKE:
{user_dislikes}

{existing}

Extract NEW insights (don't repeat existing ones). Output JSON only:
{{
    "tone": ["new tone preferences if any"],
    "content": ["new content preferences if any"],
    "structure": ["new structure preferences if any"],
    "avoid": ["new things to avoid if any"]
}}

If no new insights in a category, use empty list []. Output ONLY valid JSON."""


def compact_insights_prompt(current_insights: dict) -> str:
    """Create prompt to compact and clean up insights."""
    return f"""Clean up and compact these accumulated writing preferences. Remove duplicates, merge similar items, make concise and clear.

Current insights:
- Tone preferences: {current_insights.get('tone', [])}
- Content preferences: {current_insights.get('content', [])}
- Structure preferences: {current_insights.get('structure', [])}
- Things to avoid: {current_insights.get('avoid', [])}

Output a cleaned, non-redundant version. Each item should be unique and actionable. Output JSON only:
{{
    "tone": ["concise unique tone preferences"],
    "content": ["concise unique content preferences"],
    "structure": ["concise unique structure preferences"],
    "avoid": ["concise unique things to avoid"]
}}

Output ONLY valid JSON."""


def merge_insights(current: dict, new_insights: dict, user_likes: str, user_dislikes: str) -> dict:
    """Merge new insights into current, avoiding duplicates."""
    for key in ["tone", "content", "structure", "avoid"]:
        if key in new_insights and new_insights[key]:
            for item in new_insights[key]:
                if item and item not in current.get(key, []):
                    current.setdefault(key, []).append(item)

    # Add to history
    current.setdefault("history", []).append({
        "date": datetime.now().isoformat(),
        "likes": user_likes,
        "dislikes": user_dislikes
    })

    # Keep history manageable (last 20)
    current["history"] = current["history"][-20:]

    return current


def get_insights_for_prompt() -> str:
    """Get formatted insights for use in prompts."""
    insights = load_insights()

    parts = []
    if insights.get("tone"):
        parts.append(f"Tone: {', '.join(insights['tone'])}")
    if insights.get("content"):
        parts.append(f"Content focus: {', '.join(insights['content'])}")
    if insights.get("structure"):
        parts.append(f"Structure: {', '.join(insights['structure'])}")
    if insights.get("avoid"):
        parts.append(f"AVOID: {', '.join(insights['avoid'])}")

    return "\n".join(parts) if parts else "No accumulated preferences yet."
