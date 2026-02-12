"""LangGraph state definition for AstroGuru AI"""

from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class AstroGuruState(TypedDict):
    """State for the AstroGuru LangGraph workflow"""
    
    # User input
    user_message: str
    messages: List[Dict[str, str]]  # Conversation history
    
    # Birth details (collected by main agent)
    birth_details: Optional[Dict[str, Any]]
    
    # Analysis results from each node
    location_data: Optional[Dict[str, Any]]
    chart_data: Optional[Dict[str, Any]]
    dasha_data: Optional[Dict[str, Any]]
    goal_analysis_data: Optional[Dict[str, Any]]
    recommendation_data: Optional[Dict[str, Any]]
    summary: Optional[str]
    
    # Context for chat (after analysis)
    analysis_context: Optional[str]  # Combined context from all analyses
    
    # Control flow
    current_step: Optional[str]  # Track which step we're on
    analysis_complete: bool  # Whether full analysis has been completed
    request_type: Optional[str]  # "analysis" or "chat" - determined by router
    
    # Error handling
    error: Optional[str]

