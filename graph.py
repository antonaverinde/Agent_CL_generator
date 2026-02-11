"""LangGraph workflow definition with checkpointing."""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import CoverLetterState
from nodes import (
    node_classify, node_load_bios, node_generate,
    node_critic, node_edit, node_save_insights, node_compact_insights
)


def route_after_review(state: CoverLetterState) -> str:
    """Route based on approval status."""
    if state.get("approved", False):
        return "compact_insights"
    return "save_insights"


def build_graph():
    """Build the cover letter generation graph."""
    builder = StateGraph(CoverLetterState)

    # Add nodes
    builder.add_node("classify", node_classify)
    builder.add_node("load_bios", node_load_bios)
    builder.add_node("generate", node_generate)
    builder.add_node("critic", node_critic)
    builder.add_node("review", lambda x: x)  # Pass-through for human review
    builder.add_node("save_insights", node_save_insights)
    builder.add_node("edit", node_edit)
    builder.add_node("compact_insights", node_compact_insights)

    # Linear flow until review
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "load_bios")
    builder.add_edge("load_bios", "generate")
    builder.add_edge("generate", "critic")
    builder.add_edge("critic", "review")

    # After review: route based on approval
    builder.add_conditional_edges(
        "review",
        route_after_review,
        {"save_insights": "save_insights", "compact_insights": "compact_insights"}
    )

    # Edit path: save insights -> edit -> back to review
    builder.add_edge("save_insights", "edit")
    builder.add_edge("edit", "review")

    # Approve path: compact insights -> end
    builder.add_edge("compact_insights", END)

    return builder


def create_graph_with_memory():
    """Create compiled graph with memory checkpointing."""
    builder = build_graph()
    memory = MemorySaver()

    # Compile with interrupts for human-in-the-loop
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["load_bios", "review"]  # Pause before load_bios (confirm category) and before review (provide feedback)
    )

    return graph, memory


def get_graph_visualization(graph):
    """Display visual graph in Jupyter notebook."""
    from IPython.display import Image, display, HTML
    import base64

    g = graph.get_graph()

    # Try draw_png (requires graphviz + pygraphviz)
    try:
        png_bytes = g.draw_png()
        display(Image(png_bytes))
        return
    except Exception:
        pass

    # Try draw_mermaid_png (requires internet)
    try:
        png_bytes = g.draw_mermaid_png()
        display(Image(png_bytes))
        return
    except Exception:
        pass

    # Fallback: render mermaid in browser using mermaid.js
    mermaid_code = g.draw_mermaid()
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    <div class="mermaid">
    {mermaid_code}
    </div>
    """
    display(HTML(html))
