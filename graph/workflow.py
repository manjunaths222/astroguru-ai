"""LangGraph workflow definition for AstroGuru AI"""

from langgraph.graph import StateGraph, END
from graph.state import AstroGuruState
from graph.nodes.router_node import router_node
from graph.nodes.main_node import main_node
from graph.nodes.location_node import location_node
from graph.nodes.chart_node import chart_node
from graph.nodes.dasha_node import dasha_node
from graph.nodes.goal_analysis_node import goal_analysis_node
from graph.nodes.recommendation_node import recommendation_node
from graph.nodes.summarizer_node import summarizer_node
from graph.nodes.chat_node import chat_node
from config import logger


def create_astroguru_graph():
    """Create and compile the AstroGuru LangGraph workflow"""
    logger.info("Creating AstroGuru LangGraph workflow")
    
    # Create state graph
    workflow = StateGraph(AstroGuruState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("main", main_node)
    workflow.add_node("location", location_node)
    workflow.add_node("chart", chart_node)
    workflow.add_node("dasha", dasha_node)
    workflow.add_node("goal_analysis", goal_analysis_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("chat", chat_node)
    
    # Set entry point to router
    workflow.set_entry_point("router")
    
    # Router routes to either chat or analysis workflow
    def route_from_router(state: AstroGuruState) -> str:
        """Route from router: go to chat or start analysis"""
        request_type = state.get("request_type", "chat")
        logger.info(f"Router routing decision: {request_type}")
        # Clear request_type after routing to prevent loops
        # The router node will set it, we use it, then clear it
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
        """Route from main: continue to location if birth details collected, else end and wait for user"""
        birth_details = state.get("birth_details")
        user_message = state.get("user_message", "").strip()
        current_step = state.get("current_step")
        
        if birth_details:
            logger.info("Main node: Birth details collected, routing to location")
            return "location"
        
        # If current_step is explicitly set to "end", respect it
        if current_step == "end":
            logger.info("Main node: current_step is 'end', ending workflow to wait for user")
            return "end"
        
        # If no user message, we can't continue - end the workflow and wait for user's next message
        if not user_message:
            logger.info("Main node: No user message and no birth details, ending workflow to wait for user input")
            return "end"
        
        # If we have a user message but no birth details, we've already processed it
        # End the workflow so the user can send their next message
        logger.info("Main node: Birth details not complete after processing user message, ending workflow to wait for user's next response")
        return "end"  # End and wait for user's next message
    
    workflow.add_conditional_edges(
        "main",
        route_from_main,
        {
            "location": "location",
            "main": "main",  # Loop back to collect more info
            "end": END  # End if no user message (prevents infinite loop)
        }
    )
    
    # Analysis workflow edges
    workflow.add_edge("location", "chart")
    workflow.add_edge("chart", "dasha")
    workflow.add_edge("dasha", "goal_analysis")
    workflow.add_edge("goal_analysis", "recommendation")
    workflow.add_edge("recommendation", "summarizer")
    
    # After summarizer, always end - user can ask questions in next API call
    def route_after_summary(state: AstroGuruState) -> str:
        """Route after summary: always end to prevent loops"""
        analysis_complete = state.get("analysis_complete")
        logger.info(f"After summary: Analysis complete={analysis_complete}, ending workflow. User can ask questions in next request.")
        return "end"
    
    workflow.add_conditional_edges(
        "summarizer",
        route_after_summary,
        {
            "chat": "chat",
            "end": END
        }
    )
    
    # Chat node can loop back to itself, route to analysis, or end
    def route_after_chat(state: AstroGuruState) -> str:
        """Route after chat: continue chatting, start analysis, or end"""
        request_type = state.get("request_type")
        user_message = state.get("user_message", "").strip()
        analysis_complete = state.get("analysis_complete", False)
        
        # If user wants analysis and it's not complete, route directly to main (skip router to avoid loop)
        if request_type == "analysis" and not analysis_complete:
            logger.info("After chat: User requested analysis, routing directly to main node (clearing request_type)")
            # Clear request_type to prevent loops - we're going to main now
            return "main"
        
        # If there's a user message and we're not starting analysis, continue chatting
        if user_message and request_type != "analysis":
            logger.info("After chat: User has message, continuing chat")
            return "chat"
        
        # Otherwise end
        logger.info("After chat: No user message or analysis requested, ending")
        return "end"
    
    workflow.add_conditional_edges(
        "chat",
        route_after_chat,
        {
            "chat": "chat",
            "main": "main",  # Route directly to main if analysis requested (skip router to avoid loop)
            "end": END
        }
    )
    
    # Compile the graph
    logger.info("Compiling AstroGuru LangGraph workflow")
    app = workflow.compile()
    logger.info("AstroGuru LangGraph workflow created successfully")
    
    return app

