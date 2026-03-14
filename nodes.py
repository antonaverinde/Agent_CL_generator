"""Node functions for LangGraph Cover Letter workflow."""
from pathlib import Path
from docx import Document

from state import CoverLetterState
from models import (
    classify_job, generate_cover_letter, critique_and_fuse,
    edit_cover_letter, extract_insights_from_feedback, compact_insights
)
from memory import load_insights, save_insights, merge_insights, get_insights_for_prompt

BIO_DIR = Path("/home/anton/Jobsearch_Anton_2026")


def load_docx(filepath: Path) -> str:
    """Load text from .docx file."""
    doc = Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


# === NODE FUNCTIONS ===

def node_classify(state: CoverLetterState) -> dict:
    """Classify job description."""
    result = classify_job(state["job_description"])
    return {
        "category": result["category"],
        "confidence": result["confidence"]
    }


def node_load_bios(state: CoverLetterState) -> dict:
    """Load biography files based on category."""
    suffix = "Fin" if state["category"] == "finance" else "Eng"

    bio_gpt = load_docx(BIO_DIR / f"Info_CL_{suffix}_GPT.docx")
    bio_claude = load_docx(BIO_DIR / f"Info_CL_{suffix}_Claude.docx")

    return {
        "bio_gpt": bio_gpt,
        "bio_claude": bio_claude
    }


def node_generate(state: CoverLetterState) -> dict:
    """Generate both versions."""
    insights = get_insights_for_prompt()

    version_gpt = generate_cover_letter(
        state["job_description"],
        state["bio_gpt"],
        "gpt4o",
        insights
    )

    version_claude = generate_cover_letter(
        state["job_description"],
        state["bio_claude"],
        "claude_sonnet",
        insights
    )

    return {
        "version_gpt": version_gpt,
        "version_claude": version_claude
    }


def node_critic(state: CoverLetterState) -> dict:
    """Critic analyzes and creates fusion."""
    result = critique_and_fuse(
        state["version_gpt"],
        state["version_claude"],
        state["job_description"]
    )
    return {
        "analysis_text": result["analysis_text"],
        "fusion_letter": result["fusion_letter"],
        "current_letter": result["fusion_letter"],
        "edit_rounds": 0
    }


def node_edit(state: CoverLetterState) -> dict:
    """Edit current letter based on feedback."""
    insights = get_insights_for_prompt()

    # Use the appropriate bio based on category
    bio = state["bio_gpt"] if state["category"] == "engineering" else state["bio_claude"]

    # Build feedback from ALL rounds, not just current
    all_dislikes = state.get("user_dislikes", [])
    if len(all_dislikes) > 1:
        feedback = "\n".join(f"Round {i+1}: {fb}" for i, fb in enumerate(all_dislikes))
    else:
        feedback = all_dislikes[0] if all_dislikes else ""

    edited = edit_cover_letter(
        state["current_letter"],
        feedback,
        bio,
        insights,
        state.get("edit_model", "gpt4o")
    )

    return {
        "current_letter": edited,
        "edit_rounds": state.get("edit_rounds", 0) + 1
    }


def node_save_insights(state: CoverLetterState) -> dict:
    """Save user feedback to insights BEFORE editing."""
    current = load_insights()

    # Extract insights from latest round only (previous rounds already saved)
    likes = state.get("user_likes", [])
    dislikes = state.get("user_dislikes", [])
    latest_likes = likes[-1] if likes else ""
    latest_dislikes = dislikes[-1] if dislikes else ""

    new_insights = extract_insights_from_feedback(
        latest_likes, latest_dislikes, current
    )

    # Merge and save immediately
    merged = merge_insights(
        current, new_insights, latest_likes, latest_dislikes
    )
    save_insights(merged)

    return {}


def node_compact_insights(state: CoverLetterState) -> dict:
    """Compact and clean up accumulated insights on approval."""
    current = load_insights()

    # Use LLM to compact/dedupe insights
    compacted = compact_insights(current)
    save_insights(compacted)

    return {"final_letter": state["current_letter"]}
