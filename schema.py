from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from node_func import State, inquiry, FAQ, EC_info, McE_info, CMD, Recommender, Navigator, not_found, route_app

workflow = StateGraph(State)

workflow.add_node("inquiry", inquiry)
workflow.add_node("FAQ", FAQ)
workflow.add_node("EC_info", EC_info)
workflow.add_node("McE_info", McE_info)
workflow.add_node("Recommender", Recommender)
workflow.add_node("Navigator", Navigator)
workflow.add_node("CMD", CMD)
workflow.add_node("not_found", not_found)

workflow.add_edge(START, "inquiry")
workflow.add_conditional_edges("inquiry", route_app)
workflow.add_edge("FAQ", END)
workflow.add_edge("EC_info", END)
workflow.add_edge("McE_info", END)
workflow.add_edge("Recommender", END)
workflow.add_edge("Navigator", END)
workflow.add_edge("CMD", END)
workflow.add_edge("not_found", END)

chatbot = workflow.compile()