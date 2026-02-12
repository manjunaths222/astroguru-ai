"""Dasha node: Generates Vimshottari Dasha reports"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState


DASHA_NODE_SYSTEM_PROMPT = """
You are a Professional Vimshottari Dasha Analysis Specialist.

Your role is to calculate and analyze Vimshottari Dasha periods (120-year cycle) with detailed 
explanations of current and upcoming periods, their effects, and timing of significant events.

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**

You MUST provide a comprehensive markdown-formatted Dasha analysis with the following EXACT structure:

## Current Dasha Period

### Mahadasha: [Planet Name] (Start Date - End Date)
- **Current Bhukthi**: [Sub-period planet and dates]
- **Period Characteristics**: [Detailed explanation of what this period represents]
- **Effects on Life Areas**: [How this period affects different aspects of life]
- **Key Opportunities**: [What opportunities this period brings]
- **Challenges**: [What challenges to be aware of]

## Upcoming Dasha Periods

### Next Mahadasha: [Planet Name] (Start Date - End Date)
- **Period Overview**: [What to expect in this period]
- **Preparation Required**: [How to prepare for this period]
- **Key Transitions**: [Important dates and transitions]

[Continue for next 2-3 major periods]

## Timing of Significant Events

- **Favorable Periods**: [Dates and periods for important activities]
- **Challenging Periods**: [Dates to be cautious]
- **Major Transitions**: [Important dasha transitions and their significance]

## Overall Dasha Summary

[Comprehensive summary of the dasha cycle and its overall impact]

**IMPORTANT**: 
- Use the EXACT section headers shown above
- Provide specific dates and periods from the dasha data
- Be detailed and specific, not generic
- Use proper markdown formatting with headers (##, ###)
"""


def create_dasha_node_llm():
    """Create the LLM for the dasha node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def dasha_node(state: AstroGuruState) -> Dict[str, Any]:
    """Dasha node: Generates Dasha analysis"""
    logger.info("Dasha node: Starting Dasha analysis generation")
    
    birth_details = state.get("birth_details")
    chart_data = state.get("chart_data")
    
    if not birth_details or not chart_data:
        logger.warning("Dasha node: Missing birth details or chart data, skipping")
        return {"current_step": "chart"}
    
    # Extract dasha information from chart_data - get full dasha data
    dasha_info = chart_data.get("dasha", {})
    current_dasha = dasha_info.get("current_dasha")
    upcoming_dashas = dasha_info.get("upcoming_dashas", [])
    
    # Get full dasha details if available
    import json
    dasha_data_full = json.dumps(dasha_info, indent=2, default=str) if dasha_info else "No dasha data available"
    
    logger.debug(f"Dasha node: Current dasha: {current_dasha}, Upcoming dashas count: {len(upcoming_dashas)}")
    
    # Use LLM to generate comprehensive Dasha analysis
    llm = create_dasha_node_llm()
    
    prompt = f"""Analyze the following Dasha information and provide a comprehensive Vimshottari Dasha analysis following the EXACT format specified in the system prompt.

Birth Details:
- Name: {birth_details.get('name', 'N/A')}
- Date of Birth: {birth_details.get('date_of_birth', 'N/A')}
- Time of Birth: {birth_details.get('time_of_birth', 'N/A')}
- Place: {birth_details.get('place_of_birth', 'N/A')}
- Today's Date: {birth_details.get('today_date', 'N/A')}

Complete Dasha Data:
{dasha_data_full}

**IMPORTANT**: 
- Use ALL the dasha data provided above
- Follow the EXACT section structure from the system prompt
- Include specific dates, periods, and planetary names from the data
- Be detailed and specific - do not provide generic analysis
- Use proper markdown formatting with ## and ### headers as specified"""
    
    try:
        logger.info("Dasha node: Calling LLM for Dasha analysis")
        response = await llm.ainvoke([
            SystemMessage(content=DASHA_NODE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        dasha_analysis = response.content
        logger.info(f"Dasha node: Dasha analysis generated successfully, length: {len(dasha_analysis)}")
        
        return {
            "dasha_data": {
                "current_dasha": current_dasha,
                "upcoming_dashas": upcoming_dashas,
                "analysis": dasha_analysis
            },
            "current_step": "goal_analysis"
        }
    except Exception as e:
        logger.error(f"Dasha node: Error generating Dasha analysis: {e}", exc_info=True)
        return {"error": f"Dasha analysis failed: {str(e)}", "current_step": "chart"}

