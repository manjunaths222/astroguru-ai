"""Simplified query workflow for chat/query orders"""

from langgraph.graph import StateGraph, END
from graph.state import AstroGuruState
from graph.nodes.router_node import router_node
from graph.nodes.main_node import main_node
from graph.nodes.location_node import location_node
from graph.nodes.chart_node import chart_node
from graph.nodes.dasha_node import dasha_node
from graph.nodes.query_chat_node import query_chat_node
from config import logger


def create_query_graph():
    """Create and compile the simplified query workflow for chat/query orders"""
    logger.info("Creating simplified query workflow")
    
    # Create state graph
    workflow = StateGraph(AstroGuruState)
    
    # Add nodes (includes dasha for query orders, uses query_chat_node)
    workflow.add_node("router", router_node)
    workflow.add_node("main", main_node)
    workflow.add_node("location", location_node)
    workflow.add_node("chart", chart_node)
    workflow.add_node("dasha", dasha_node)
    workflow.add_node("chat", query_chat_node)  # Use query_chat_node instead of chat_node
    
    # Set entry point to router
    workflow.set_entry_point("router")
    
    # Router routes to either chat or start analysis
    def route_from_router(state: AstroGuruState) -> str:
        """Route from router: go to chat or start analysis"""
        request_type = state.get("request_type", "chat")
        logger.info(f"Query router routing decision: {request_type}")
        return request_type
    
    workflow.add_conditional_edges(
        "router",
        route_from_router,
        {
            "chat": "chat",
            "analysis": "main"
        }
    )
    
    # Main node routes based on whether birth details are collected
    def route_from_main(state: AstroGuruState) -> str:
        """Route from main: continue to location if birth details collected, else end"""
        birth_details = state.get("birth_details")
        user_message = state.get("user_message", "").strip()
        current_step = state.get("current_step")
        
        if birth_details:
            logger.info("Query main node: Birth details collected, routing to location")
            return "location"
        
        if current_step == "end" or not user_message:
            logger.info("Query main node: Ending workflow to wait for user")
            return "end"
        
        logger.info("Query main node: Birth details not complete, ending workflow")
        return "end"
    
    workflow.add_conditional_edges(
        "main",
        route_from_main,
        {
            "location": "location",
            "end": END
        }
    )
    
    # Query workflow: location -> chart -> dasha -> chat -> end
    workflow.add_edge("location", "chart")
    workflow.add_edge("chart", "dasha")
    workflow.add_edge("dasha", "chat")
    
    # After chat, always end (user can send follow-up in next API call)
    def route_after_chat(state: AstroGuruState) -> str:
        """Route after chat: always end for query workflow"""
        logger.info("Query chat: Message processed, ending workflow. Next message will start fresh.")
        return "end"
    
    workflow.add_conditional_edges(
        "chat",
        route_after_chat,
        {
            "end": END
        }
    )
    
    # Compile the graph
    logger.info("Compiling simplified query workflow")
    app = workflow.compile()
    logger.info("Simplified query workflow created successfully")
    
    return app

