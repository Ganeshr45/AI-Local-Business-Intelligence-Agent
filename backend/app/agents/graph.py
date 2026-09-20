from langgraph.graph import StateGraph, END
from app.agents.state import BusinessIntelState
from app.agents.query_planner import query_planner_node
from app.agents.local_business_research import local_business_research_node
from app.agents.competitor_analysis import competitor_analysis_node
from app.agents.review_intelligence import review_intelligence_node
from app.agents.website_analyzer import website_analyzer_node
from app.agents.market_gap import market_gap_node
from app.agents.insight_generator import insight_generator_node
from app.agents.recommendation_agent import recommendation_node
from app.agents.report_generator import report_generator_node


def build_graph():
    graph = StateGraph(BusinessIntelState)

    graph.add_node("query_planner", query_planner_node)
    graph.add_node("local_business_research", local_business_research_node)
    graph.add_node("competitor_analysis", competitor_analysis_node)
    graph.add_node("review_intelligence", review_intelligence_node)
    graph.add_node("website_analyzer", website_analyzer_node)
    graph.add_node("market_gap", market_gap_node)
    graph.add_node("insight_generator", insight_generator_node)
    graph.add_node("recommendation_agent", recommendation_node)
    graph.add_node("report_generator", report_generator_node)

    graph.set_entry_point("query_planner")
    graph.add_edge("query_planner", "local_business_research")
    graph.add_edge("local_business_research", "competitor_analysis")
    graph.add_edge("competitor_analysis", "review_intelligence")
    graph.add_edge("review_intelligence", "website_analyzer")
    graph.add_edge("website_analyzer", "market_gap")
    graph.add_edge("market_gap", "insight_generator")
    graph.add_edge("insight_generator", "recommendation_agent")
    graph.add_edge("recommendation_agent", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()


compiled_graph = build_graph()


def run_pipeline(run_id: str, query: str) -> BusinessIntelState:
    initial_state: BusinessIntelState = {
        "run_id": run_id,
        "query": query,
        "location": None,
        "category": None,
        "target_business": None,
        "competitors": [],
        "reviews": [],
        "website_audit": None,
        "evidence": [],
        "insights": [],
        "recommendations": [],
        "errors": [],
        "events": [],
    }
    final_state = compiled_graph.invoke(initial_state)
    return final_state
