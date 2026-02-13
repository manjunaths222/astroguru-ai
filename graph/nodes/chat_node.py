"""Chat node: Handles normal chat with context after analysis"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState


CHAT_NODE_SYSTEM_PROMPT = """
You are a Professional Vedic Astrology Consultant helping users with astrology questions.

**Two Modes of Operation:**

1. **With Analysis Context (after analysis is complete):**
   - You have access to a comprehensive astrology analysis that has already been completed
   - Use this context to answer questions about the user's specific horoscope
   - Provide specific details from the analysis when relevant
   - If asked to re-analyze or start over, explain that a new analysis would need to be initiated
   - **CRITICAL**: You have access to the full conversation history - use it to understand context
   - When answering follow-up questions, refer back to previous parts of the conversation
   - Maintain continuity with previous responses

2. **General Chat Mode (no analysis yet):**
   - Answer general questions about Vedic astrology
   - Explain astrology concepts, planets, signs, houses, nakshatras, etc.
   - Provide educational information about astrology
   - If user wants their horoscope analyzed, guide them to provide birth details
   - Be friendly, professional, and helpful
   - **CRITICAL**: You have access to the full conversation history - use it to understand context
   - When answering follow-up questions, refer back to previous parts of the conversation

**Important Guidelines:**
- Be friendly, professional, and helpful
- Use clear, accessible language
- Provide accurate information about Vedic astrology
- If you don't know something, admit it rather than making it up
- **Always consider the conversation history** - follow-up questions should be answered in context
- Maintain continuity and coherence across the conversation
"""


def create_chat_node_llm():
    """Create the LLM for the chat node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def chat_node(state: AstroGuruState) -> Dict[str, Any]:
    """Chat node: Handles normal chat with analysis context"""
    logger.info("Chat node: Processing chat message")
    
    user_message = state.get("user_message", "")
    messages = state.get("messages", [])
    analysis_context = state.get("analysis_context")
    analysis_complete = state.get("analysis_complete", False)
    
    if not user_message:
        logger.warning("Chat node: No user message, skipping")
        return {}
    
    logger.debug(f"Chat node: Message length: {len(user_message)}, analysis_complete: {analysis_complete}, message history: {len(messages)}")
    
    # Build system message - Gemini requires only ONE system message at position 0
    # Combine the base prompt with context-specific instructions
    if analysis_context and analysis_complete:
        logger.info("Chat node: Using analysis context for response")
        system_content = f"""{CHAT_NODE_SYSTEM_PROMPT}

Analysis Context (User's Horoscope Analysis):
{analysis_context}

Use this context to answer questions about the user's specific horoscope. For general astrology questions, use your knowledge."""
    else:
        # No analysis yet - general chat mode
        logger.info("Chat node: General chat mode (no analysis context)")
        system_content = f"""{CHAT_NODE_SYSTEM_PROMPT}

You are in general chat mode. Answer questions about Vedic astrology in general. If the user wants their horoscope analyzed, guide them to provide birth details (name, date of birth, time of birth, place of birth)."""
    
    # Build conversation - SystemMessage must be first (position 0) for Gemini
    conversation = [SystemMessage(content=system_content)]
    
    # Add conversation history (last 20 messages to preserve more context for follow-ups)
    # This ensures follow-up questions have sufficient context
    history_count = 0
    for msg in messages[-20:]:  # Increased from 10 to 20 for better context
        if msg.get("role") == "user":
            conversation.append(HumanMessage(content=msg.get("content", "")))
            history_count += 1
        elif msg.get("role") == "assistant":
            conversation.append(AIMessage(content=msg.get("content", "")))
            history_count += 1
    
    logger.info(f"Chat node: Added {history_count} messages from history (total history: {len(messages)} messages)")
    
    # Add current user message
    conversation.append(HumanMessage(content=user_message))
    
    # Call LLM
    try:
        llm = create_chat_node_llm()
        logger.info("Chat node: Calling LLM for chat response")
        response = await llm.ainvoke(conversation)
        response_text = response.content
        logger.debug(f"Chat node: LLM response length: {len(response_text)}")
    except Exception as e:
        logger.error(f"Chat node: Error calling LLM: {e}", exc_info=True)
        response_text = "I apologize, but I encountered an error while processing your request. Please try again."
    
    # Update messages
    new_messages = messages + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text}
    ]
    
    logger.info(f"Chat node: Response generated successfully, total messages: {len(new_messages)}")
    
    # Default: clear user_message after processing to prevent infinite loops
    result = {
        "messages": new_messages,
        "user_message": ""  # Always clear user_message after processing in chat (prevents loops)
    }
    
    # Check if user wants to start analysis (they might ask after chatting)
    # Only set request_type if analysis is not complete
    if not analysis_complete:
        user_message_lower = user_message.lower()
        analysis_keywords = ["analyze my", "my horoscope", "birth chart", "natal chart", "get my analysis", "i want my", "can you analyze", "i'd like to get", "start analysis", "new analysis"]
        wants_analysis = any(keyword in user_message_lower for keyword in analysis_keywords)
        
        if wants_analysis:
            # Set request_type to trigger analysis, but keep user_message for main node
            # This is the ONLY case where we keep user_message - to pass it to main_node
            result["request_type"] = "analysis"
            result["user_message"] = user_message  # Keep message for main node to process
            logger.info("Chat node: User wants analysis, setting request_type to 'analysis' and keeping user_message for main node")
        else:
            # Ensure user_message is cleared (defensive programming)
            result["user_message"] = ""
    else:
        # Analysis already complete - always clear user_message to prevent loops
        result["user_message"] = ""
    
    # CRITICAL: Always ensure user_message is cleared unless explicitly passing to analysis
    # This prevents infinite loops in the chat node
    if "request_type" not in result or result.get("request_type") != "analysis":
        result["user_message"] = ""
    
    return result

