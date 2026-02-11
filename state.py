"""LangGraph state definitions for Cover Letter Agent."""
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class CoverLetterState(TypedDict):
    """State for the cover letter generation workflow."""
    # Input
    job_description: str

    # Classification
    category: str  # "engineering" or "finance"
    confidence: int

    # Biographies (kept for editing)
    bio_gpt: str
    bio_claude: str

    # Generated versions
    version_gpt: str
    version_claude: str

    # Critic analysis
    analysis_text: str  # Full analysis ~300 words
    fusion_letter: str  # Fused version ~300 words

    # Current working version
    current_letter: str

    # Human feedback
    user_score: int
    user_likes: str
    user_dislikes: str
    approved: bool

    # Edit control
    edit_model: str  # "claude_opus" or "gpt4o"
    edit_rounds: int

    # Final
    final_letter: str
