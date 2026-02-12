"""Router node: Intelligently routes between normal chat and analysis workflow"""

from typing import Dict, Any, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import AstroConfig, logger
from graph.state import AstroGuruState


ROUTER_SYSTEM_PROMPT = """
You are a routing assistant for a Vedic Astrology consultation system.

Your job is to analyze the user's message and determine their intent:

1. **Analysis Request**: User wants to get their horoscope analyzed
   - Keywords: "horoscope", "birth chart", "natal chart", "astrology analysis", "my chart", "analyze my", "get my horoscope", "I'd like to get", "I want my"
   - Phrases: "I'd like to get my horoscope analyzed", "I want my horoscope", "analyze my chart", "get my analysis"
   - User provides or wants to provide birth details
   - User asks about their specific horoscope/astrology
   - Response: "analysis"

2. **Normal Chat**: User wants general information or conversation
   - General astrology questions (what is, explain, tell me about) WITHOUT "my" or personal requests
   - Questions about astrology concepts, planets, signs, etc. (general knowledge)
   - Casual conversation, greetings, general inquiries
   - Questions about astrology in general (not their specific chart)
   - Response: "chat"

**Critical Rules:**
- If user says "I'd like to get my horoscope analyzed" → MUST route to "analysis"
- If user mentions "my horoscope", "my chart", "analyze my", "get my" → route to "analysis"
- If user asks general questions like "what is astrology" (no "my") → route to "chat"
- If user provides birth details (date, time, place) → route to "analysis"
- If analysis is already complete (analysis_complete=true), always route to "chat"
- When message contains personal requests ("my", "I want", "I'd like") → prefer "analysis"

Respond with ONLY one word: either "analysis" or "chat"
"""


def create_router_llm():
    """Create the LLM for the router node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=0.1,  # Low temperature for consistent routing
        max_tokens=10,  # Only need one word response
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def router_node(state: AstroGuruState) -> Dict[str, Any]:
    """Router node: Determines whether to do normal chat or start analysis
    
    This node is ONLY called at the entry point of each request.
    It should never be called again during the same request flow.
    """
    logger.info("Router node: Analyzing user intent (entry point)")
    
    user_message = state.get("user_message", "").strip()
    analysis_complete = state.get("analysis_complete", False)
    birth_details = state.get("birth_details")
    
    # CRITICAL RULE 1: If analysis is already complete, always route to chat (never re-analyze)
    if analysis_complete:
        logger.info("Router node: Analysis complete, routing to chat")
        return {"request_type": "chat"}
    
    # CRITICAL RULE 2: If birth details exist but analysis not complete, continue analysis workflow
    # This handles the case where user provided details but analysis is still in progress
    if birth_details and not analysis_complete:
        logger.info("Router node: Birth details exist but analysis incomplete, continuing analysis workflow")
        return {"request_type": "analysis"}
    
    # If no user message, default to chat
    if not user_message:
        logger.info("Router node: No user message, routing to chat")
        return {"request_type": "chat"}
    
    # Use LLM to determine intent
    llm = create_router_llm()
    prompt = f"""Analyze this user message and determine if they want:
1. "analysis" - They want their horoscope analyzed (provide birth details, get analysis)
   - Keywords: "horoscope", "analyze", "birth chart", "my chart", "get my", "I want my", "I'd like to get"
   - If message contains "I'd like to get my horoscope analyzed" → "analysis"
2. "chat" - They want general conversation or information about astrology
   - General questions like "what is", "explain", "tell me about" (without "my" or personal requests)

User message: "{user_message}"

**IMPORTANT**: If the user says they want their horoscope analyzed, want analysis, or want to get their chart analyzed, respond with "analysis".

Respond with ONLY one word: "analysis" or "chat" """
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        route_decision = response.content.strip().lower()
        logger.debug(f"Router node: LLM decision: {route_decision}")
        
        # Validate response - be more aggressive about detecting analysis
        if "analysis" in route_decision or any(keyword in user_message.lower() for keyword in ["analyze", "horoscope", "chart", "get my", "i want my", "i'd like"]):
            logger.info(f"Router node: Routing to analysis workflow (decision: {route_decision})")
            return {"request_type": "analysis"}
        else:
            logger.info(f"Router node: Routing to normal chat (decision: {route_decision})")
            return {"request_type": "chat"}
            
    except Exception as e:
        logger.error(f"Router node: Error determining route: {e}", exc_info=True)
        # If error, check for analysis keywords as fallback
        analysis_keywords = ["analyze", "horoscope", "chart", "get my", "i want my", "i'd like"]
        if any(keyword in user_message.lower() for keyword in analysis_keywords):
            logger.info("Router node: Error occurred, but analysis keywords detected, routing to analysis")
            return {"request_type": "analysis"}
        # Default to chat on error
        return {"request_type": "chat"}

