"""Compact insights.json - unify history entries and clean up preferences."""
import sys
sys.path.insert(0, '/home/anton/CV_agent')

import json
from datetime import datetime
from memory import load_insights, save_insights
from models import call_llm

def compact_all():
    insights = load_insights()
    history = insights.get("history", [])

    if len(history) <= 1:
        print("Nothing to compact.")
        return

    # Combine all history feedback
    all_likes = "\n".join(f"- {h['likes']}" for h in history if h.get('likes') and h['likes'] != 'Approved')
    all_dislikes = "\n".join(f"- {h['dislikes']}" for h in history if h.get('dislikes'))

    prompt = f"""Consolidate these cover letter preferences into clean, actionable insights.

ALL USER LIKES (across sessions):
{all_likes or 'none'}

ALL USER DISLIKES (across sessions):
{all_dislikes or 'none'}

CURRENT INSIGHTS:
- Tone: {insights.get('tone', [])}
- Content: {insights.get('content', [])}
- Structure: {insights.get('structure', [])}
- Avoid: {insights.get('avoid', [])}

Create a unified, non-redundant set of preferences. Be specific and actionable. Output JSON only:
{{
    "tone": ["specific tone preferences"],
    "content": ["specific content preferences"],
    "structure": ["specific structure preferences"],
    "avoid": ["specific things to avoid"]
}}

Output ONLY valid JSON."""

    print("Compacting with LLM...")
    response = call_llm("gemini_flash", prompt, max_tokens=500)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        compacted = json.loads(response[start:end])

        # Keep single history entry with latest date
        compacted["history"] = [{
            "date": datetime.now().isoformat(),
            "likes": f"Compacted from {len(history)} sessions",
            "dislikes": ""
        }]

        save_insights(compacted)
        print("\nCOMPACTED INSIGHTS:")
        print(json.dumps(compacted, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print(f"Raw response: {response}")

if __name__ == "__main__":
    compact_all()
