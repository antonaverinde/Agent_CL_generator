---
name: cv-agent-context
description: This skill should be used when working in the CV_agent directory, modifying CV_agent code, discussing cover letter agent architecture, debugging LangGraph workflows, or when the user mentions "cover letter", "CV agent", "insights", "orchestrator", or references files in CV_agent/. Provides architectural context from architecture.md to enhance understanding before coding.
---

# CV Agent Context Loader

When this skill activates, read `/home/anton/CV_agent/architecture.md` to understand the full system before taking action.

## Quick Reference

**File → Responsibility mapping:**
| File | What it does |
|------|-------------|
| `state.py` | `CoverLetterState(TypedDict)` - 15 fields |
| `models.py` | OpenRouter API calls (`call_llm`, `classify_job`, `generate_cover_letter`, `critique_and_fuse`, `edit_cover_letter`, `extract_insights_from_feedback`, `compact_insights`) |
| `nodes.py` | LangGraph node wrappers that call models.py + memory.py |
| `graph.py` | `build_graph()`, `create_graph_with_memory()`, visualization |
| `memory.py` | `insights.json` I/O: load, save, merge, format for prompts |
| `utils.py` | `.docx` export (`save_cover_letter`) + CLI feedback (`get_feedback`) |
| `compact_insights.py` | Standalone CLI tool to consolidate insights history |
| `orchestrator.ipynb` | Full interactive notebook (V1 - step by step) |
| `orchestrator_V2.ipynb` | Streamlined notebook (V2 - all-in-one) |

**Graph flow:**
```
START → classify → load_bios → generate → critic → review
    approved? → YES → compact_insights → END
              → NO  → save_insights → edit → review (loop)
```

**Interrupt checkpoints:** `load_bios` (confirm category), `review` (provide feedback)

**Models (OpenRouter):** Gemini 3 Flash (classify), GPT-5.2 (generate/edit), Claude Sonnet 4.5 (generate), Claude Opus 4.5 (critic/fusion)

**Bio files:** `/home/anton/Jobsearch_Anton_2026/Info_CL_{Fin|Eng}_{GPT|Claude}.docx`

**Output:** `/home/anton/CV_agent/CLs_docx/{company}_{position}_{date}/cover_letter_{company}.docx`

## When to Consult architecture.md

- Before modifying any Python file in CV_agent
- When debugging graph flow or state transitions
- When adding new nodes or state fields
- When the user asks about system design or costs
- When insights/preferences behavior is unclear

## Delegate to langgraph-specialist Agent

For implementation tasks in CV_agent, prefer delegating to the `langgraph-specialist` agent which has deep context about LangGraph patterns and this project's conventions.
