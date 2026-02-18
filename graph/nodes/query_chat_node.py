"""Query Chat node: Handles chat for query orders with chart and dasha analysis context"""

from typing import Dict, Any
from datetime import datetime, date, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState
from graph.constants import GOCHARA_CONTEXT


QUERY_CHAT_NODE_SYSTEM_PROMPT = f"""
You are a friendly and approachable Vedic Astrology Consultant helping users understand their horoscope in simple, everyday language.

**WHAT YOU HAVE ACCESS TO:**
- The user's birth chart analysis
- Current and upcoming planetary periods (dasha cycles)
- Current planetary gochara transits (gochara)
- Today's date YYYY-MM-DD: {date.today().strftime("%Y-%m-%d")}
- Full conversation history

Gochara transits context:
{GOCHARA_CONTEXT}

**HOW TO RESPOND:**
- Use simple, everyday language - avoid complex astrology terms.
- Divide into logical sections - avoid long paragraphs
- Focus only on the user's specific question - answer their specific question without overwhelming them with technical details
- Keep answers concise and practical.
- Always start predictions **from today's date forward only**.  
  Never explain past periods unless the user explicitly asks.
- When discussing timing, mention only **2-3 key upcoming periods**.
- **Use the analysis data** - base your answers on the actual chart and dasha information provided, but explain it simply
- **Maintain conversation flow** - remember what was discussed earlier and build on previous answers
- **Be honest** - if you don't have specific information, say so clearly

**INTEGRATED TIMING RULE (VERY IMPORTANT):**
- Always combine **Dasha + Gochara Transits** together and give **one clear summarized interpretation**.
- Do NOT explain dasha and gochara transit separately unless the user explicitly asks.
- Provide a short **clear summary first**, then optional brief explanation.

**WHAT TO AVOID:**
- Do not analyze time periods before today's date unless explicitly requested.
- Do not say that information is unavailable for earlier periods.
- Do not list many planetary movements or long date ranges.
- Do not provide long technical astrological explanations.

**RESPONSE STRUCTURE (MANDATORY):**
1. **Clear 4-6 sentence summary** of what the user can expect (combined dasha + gochara transits effect)
2. **Brief explanation** (accurately based on the analysis data, simple language)
3. **2-3 key timing windows only** if required


**Goal:** Give a clear, confident, forward-looking interpretation that is easy to understand and directly useful.
"""



def create_query_chat_node_llm():
    """Create the LLM for the query chat node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def query_chat_node(state: AstroGuruState) -> Dict[str, Any]:
    """Query Chat node: Handles chat for query orders with chart and dasha context"""
    logger.info("Query Chat node: Processing chat message for query order")
    
    user_message = state.get("user_message", "")
    messages = state.get("messages", [])
    chart_data = state.get("chart_data")
    dasha_data = state.get("dasha_data")
    
    if not user_message:
        logger.warning("Query Chat node: No user message, skipping")
        return {}
    
    logger.debug(f"Query Chat node: Message length: {len(user_message)}, message history: {len(messages)}")
    logger.debug(f"Query Chat node: Chart data available: {chart_data is not None}, Dasha data available: {dasha_data is not None}")
    
    # Extract chart analysis
    chart_analysis = ""
    if chart_data:
        chart_analysis = chart_data.get("analysis", "") or chart_data.get("chart_data_analysis", "")
        if not chart_analysis and isinstance(chart_data, dict):
            # Try to get any analysis text from chart_data
            for key in ["analysis", "chart_analysis", "chart_data_analysis", "summary"]:
                if key in chart_data and chart_data[key]:
                    chart_analysis = str(chart_data[key])
                    break
    
    # Extract dasha analysis
    dasha_analysis = ""
    if dasha_data:
        dasha_analysis = dasha_data.get("analysis", "")
        if not dasha_analysis and isinstance(dasha_data, dict):
            # Try to get analysis from nested structure
            if "dasha_data" in dasha_data and isinstance(dasha_data["dasha_data"], dict):
                dasha_analysis = dasha_data["dasha_data"].get("analysis", "")
    
    logger.info(f"Query Chat node: Chart analysis length: {len(chart_analysis)}, Dasha analysis length: {len(dasha_analysis)}")
    
    # Build system message with chart and dasha context
    context_parts = []
    
    if chart_analysis:
        context_parts.append(f"""
**CHART ANALYSIS DATA:**
{chart_analysis}
""")
    else:
        logger.warning("Query Chat node: No chart analysis available - responses may be limited")
        context_parts.append("**CHART ANALYSIS DATA:** Not available")
    
    if dasha_analysis:
        context_parts.append(f"""
**DASHA ANALYSIS DATA:**
{dasha_analysis}
""")
    else:
        logger.warning("Query Chat node: No dasha analysis available - responses may be limited")
        context_parts.append("**DASHA ANALYSIS DATA:** Not available")
    
    analysis_context = "\n".join(context_parts)
    
    system_content = f"""{QUERY_CHAT_NODE_SYSTEM_PROMPT}

{analysis_context}

**CRITICAL**: Use the chart and dasha analysis data above to answer questions. DO NOT make up or hallucinate information. If the data doesn't contain information about what the user is asking, clearly state that."""
    
    # Build conversation - SystemMessage must be first (position 0) for Gemini
    conversation = [SystemMessage(content=system_content)]
    
    # Add conversation history (all messages to maintain full context)
    # This ensures follow-up questions have complete context including initial query
    history_count = 0
    logger.info(f"Query Chat node: Adding {len(messages)} messages from conversation history")
    for msg in messages[-20:]:  # Last 20 messages for context
        if msg.get("role") == "user":
            conversation.append(HumanMessage(content=msg.get("content", "")))
            history_count += 1
        elif msg.get("role") == "assistant":
            conversation.append(AIMessage(content=msg.get("content", "")))
            history_count += 1
    
    logger.info(f"Query Chat node: Added {history_count} messages from history (total history: {len(messages)} messages)")
    
    # Add current user message
    conversation.append(HumanMessage(content=user_message))
    
    # Call LLM
    try:
        llm = create_query_chat_node_llm()
        logger.info("Query Chat node: Calling LLM for chat response with chart and dasha context")
        response = await llm.ainvoke(conversation)
        response_text = response.content
        logger.debug(f"Query Chat node: LLM response length: {len(response_text)}")
    except Exception as e:
        logger.error(f"Query Chat node: Error calling LLM: {e}", exc_info=True)
        response_text = "I apologize, but I encountered an error while processing your request. Please try again."
    
    # Update messages
    new_messages = messages + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text}
    ]
    
    logger.info(f"Query Chat node: Response generated successfully, total messages: {len(new_messages)}")
    
    # Clear user_message after processing to prevent infinite loops
    result = {
        "messages": new_messages,
        "user_message": ""  # Always clear user_message after processing
    }
    
    return result

