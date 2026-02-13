"""Router node: Intelligently routes between normal chat and analysis workflow"""

from typing import Dict, Any, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
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
    messages = state.get("messages", [])
    
    # CRITICAL RULE 1: If analysis is already complete, always route to chat (never re-analyze)
    # This ensures follow-up questions after analysis go to chat
    if analysis_complete:
        logger.info("Router node: Analysis complete, routing to chat (follow-up questions will have context)")
        return {"request_type": "chat"}
    
    # CRITICAL RULE 2: If birth details exist but analysis not complete, continue analysis workflow
    # This handles the case where user provided details but analysis is still in progress
    if birth_details and not analysis_complete:
        logger.info("Router node: Birth details exist but analysis incomplete, continuing analysis workflow")
        return {"request_type": "analysis"}
    
    # CRITICAL RULE 3: If there's existing conversation history, check if user wants new analysis
    # or is asking a follow-up question
    if messages and len(messages) > 0:
        logger.info(f"Router node: Found {len(messages)} messages in conversation history")
        
        # First, check if user explicitly wants a NEW analysis (not a follow-up)
        # This takes priority over follow-up detection
        new_analysis_keywords = ["new analysis", "start over", "analyze again", "new horoscope", "different chart", "reset"]
        if any(keyword in user_message.lower() for keyword in new_analysis_keywords):
            logger.info("Router node: User explicitly requested new analysis, routing to analysis")
            return {"request_type": "analysis"}
        
        # Check if user is requesting analysis (even with conversation history)
        # This handles cases where user might have chatted first, then decided to get analysis
        analysis_request_keywords = ["i want my horoscope", "analyze my", "get my horoscope", "i'd like to get my", "birth chart", "natal chart"]
        if any(keyword in user_message.lower() for keyword in analysis_request_keywords):
            logger.info("Router node: User requesting analysis (despite conversation history), routing to analysis")
            return {"request_type": "analysis"}
        
        # If there's conversation history and user is asking follow-up questions (not requesting analysis),
        # route to chat to preserve context
        logger.info("Router node: Follow-up question detected (conversation history exists, no analysis request), routing to chat")
        return {"request_type": "chat"}
    
    # If no user message, default to chat
    if not user_message:
        logger.info("Router node: No user message, routing to chat")
        return {"request_type": "chat"}
    
    # Use LLM to determine intent (only for new conversations without history)
    llm = create_router_llm()
    
    # Build context from recent messages if available
    conversation_context = ""
    if messages:
        recent_messages = messages[-4:]  # Last 2 exchanges (4 messages)
        conversation_context = "\n\nRecent conversation context:\n"
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]  # Truncate long messages
            conversation_context += f"{role}: {content}\n"
    
    prompt = f"""Analyze this user message and determine if they want:
1. "analysis" - They want their horoscope analyzed (provide birth details, get analysis)
   - Keywords: "horoscope", "analyze", "birth chart", "my chart", "get my", "I want my", "I'd like to get"
   - If message contains "I'd like to get my horoscope analyzed" → "analysis"
   - User provides or wants to provide birth details (date, time, place)
2. "chat" - They want general conversation or information about astrology
   - General questions like "what is", "explain", "tell me about" (without "my" or personal requests)
   - Follow-up questions about previous conversation
   - Questions about astrology concepts

{conversation_context}

Current user message: "{user_message}"

**IMPORTANT**: 
- If the user says they want their horoscope analyzed, want analysis, or want to get their chart analyzed, respond with "analysis".
- If there's conversation history and the user is asking a follow-up question, respond with "chat".

Respond with ONLY one word: "analysis" or "chat" """
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        route_decision = response.content.strip().lower()
        logger.debug(f"Router node: LLM decision: {route_decision}")
        
        # Validate response - be more aggressive about detecting analysis
        # But only if there's no conversation history (to avoid misrouting follow-ups)
        if not messages:
            if "analysis" in route_decision or any(keyword in user_message.lower() for keyword in ["analyze", "horoscope", "chart", "get my", "i want my", "i'd like"]):
                logger.info(f"Router node: Routing to analysis workflow (decision: {route_decision})")
                return {"request_type": "analysis"}
        
        logger.info(f"Router node: Routing to normal chat (decision: {route_decision})")
        return {"request_type": "chat"}
            
    except Exception as e:
        logger.error(f"Router node: Error determining route: {e}", exc_info=True)
        # If error and there's conversation history, default to chat to preserve context
        if messages:
            logger.info("Router node: Error occurred, but conversation history exists, routing to chat")
            return {"request_type": "chat"}
        # If error, check for analysis keywords as fallback
        analysis_keywords = ["analyze", "horoscope", "chart", "get my", "i want my", "i'd like"]
        if any(keyword in user_message.lower() for keyword in analysis_keywords):
            logger.info("Router node: Error occurred, but analysis keywords detected, routing to analysis")
            return {"request_type": "analysis"}
        # Default to chat on error
        return {"request_type": "chat"}

