from workflows.internship_workflow import build_internship_workflow

graph = build_internship_workflow()

png = graph.get_graph().draw_mermaid_png()

with open("workflow.png", "wb") as f:
    f.write(png)