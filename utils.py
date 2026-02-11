"""Utility functions for cover letter generation."""
import re
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt


def clean_filename(text):
    """Clean text for use in filename."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '_', text)
    return text[:50].strip('_')


def save_cover_letter(text, company, position, base_path="/home/anton/CV_agent/CLs_docx"):
    """Save cover letter to organized folder structure."""
    date_str = datetime.now().strftime('%Y%m%d_%H%M')
    company_clean = clean_filename(company)
    position_clean = clean_filename(position)

    folder_name = f"{company_clean}_{position_clean}_{date_str}"
    folder_path = Path(base_path) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    doc = Document()
    style = doc.styles['Normal']
    style.font.size = Pt(12)
    style.font.name = 'Calibri'

    for para in text.split('\n\n'):
        if para.strip():
            doc.add_paragraph(para.strip())

    filename = f"cover_letter_{company_clean}.docx"
    filepath = folder_path / filename
    doc.save(filepath)

    print(f"Saved: {filepath}")
    return filepath


def get_feedback():
    """Get user feedback interactively."""
    score = input("Score (1-10) or 'approve': ").strip().lower()

    if score in ('approve', 'a', ''):
        return {"approved": True, "user_score": 10, "user_likes": "Approved", "user_dislikes": ""}

    try:
        score_int = int(score)
    except ValueError:
        score_int = 5

    likes = input("Likes: ").strip()
    dislikes = input("Needs improvement: ").strip()
    #model = input("Edit with (1=GPT, 2=Claude): ").strip()

    return {
        "approved": False,
        "user_score": score_int,
        "user_likes": likes,
        "user_dislikes": dislikes,
        "edit_model":  "gpt4o"#"claude_opus" if model == "2" else
    }
