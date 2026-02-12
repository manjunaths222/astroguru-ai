"""Router node: Routes between analysis workflow and chat"""

from typing import Literal
from graph.state import AstroGuruState


def route_decision(state: AstroGuruState) -> Literal["location", "chat"]:
    """Route decision: Determine if we should continue analysis or handle chat"""
    analysis_complete = state.get("analysis_complete", False)
    birth_details = state.get("birth_details")
    
    # If analysis is complete, route to chat
    if analysis_complete:
        return "chat"
    
    # If birth details are collected, continue with analysis (go to location)
    if birth_details:
        return "location"
    
    # If no birth details yet, stay in main (this shouldn't happen as main handles it)
    # But if it does, go to location which will check and route back
    return "location"

