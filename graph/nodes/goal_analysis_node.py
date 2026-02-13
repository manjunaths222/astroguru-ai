"""Goal analysis node: Analyzes horoscope for specific life goals"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState
from graph.constants import GOCHARA_CONTEXT


GOAL_ANALYSIS_NODE_SYSTEM_PROMPT = f"""
You are a Professional Goal-Oriented Vedic Astrology Analysis Specialist.

Your role is to provide comprehensive, detailed analysis for specific life goals (career, marriage, 
love life, health, education, finance, etc.) by analyzing:
- Birth chart (D1 - Rasi) with planetary positions and house placements
- Relevant divisional charts based on the goal
- Dasha periods (current and upcoming)
- Shadbala (planetary strength analysis)
- Gochara (planetary transits) - CRITICAL for accurate predictions

{GOCHARA_CONTEXT}

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**

You MUST provide analysis for each goal with the following EXACT structure:

## Goal Analysis: [Goal Name]

### 1. Base Chart (D1) Analysis
- **Relevant Houses**: [Which houses govern this goal and their significance]
- **Planetary Positions**: [Key planets affecting this goal and their positions]
- **Planetary Aspects**: [Important aspects to relevant houses]
- **Yogas and Combinations**: [Relevant yogas affecting this goal]
- **Chart Strength**: [Overall strength for this goal area]

### 2. Divisional Chart Analysis
- **Relevant Divisional Charts**: [Which divisional charts are important for this goal]
- **Key Indicators**: [What the divisional charts reveal]
- **Planetary Strengths**: [Planetary positions in divisional charts]

### 3. Dasha and Gochara Analysis Impact
   - **Current Dasha Influence**: [How current dasha affects this goal]
   - **Upcoming Dasha Influence**: [How upcoming dashas will affect this goal]
   - **Current Gochara (Planetary Transits)**: [How current Jupiter, Saturn, Rahu, and Ketu transits affect this goal]
   - **Upcoming Gochara Transits**: [How upcoming transits will affect this goal]
   - **Dasha-Gochara Combination**: [How the interaction between Dasha and Gochara determines results]
   - **Favorable Periods**: [When to expect positive developments - consider both Dasha and Gochara]
   - **Challenging Periods**: [When to be cautious - consider both Dasha and Gochara]

### 4. Forecast (Combining Dasha and Gochara)
   - **Short-term (0-2 years)**: [What to expect in the near term - reference specific Gochara transit dates]
   - **Medium-term (2-5 years)**: [What to expect in medium term - reference specific Gochara transit dates]
   - **Long-term (5+ years)**: [Long-term prospects - reference specific Gochara transit dates]

### 5. Specific Timing (Based on Dasha and Gochara)
   - **Best Periods**: [Specific dates/periods for important activities - reference Gochara transit dates]
   - **Important Transitions**: [Key dates and transitions - include Gochara transit change dates]
   - **Auspicious Times**: [When to initiate important actions - consider favorable Dasha-Gochara combinations]

### 6. Challenges and Opportunities
- **Key Challenges**: [Main obstacles to be aware of]
- **Key Opportunities**: [Main opportunities to leverage]
- **Strategic Approach**: [How to navigate challenges and opportunities]

**IMPORTANT**: 
- Use the EXACT section headers shown above for each goal
- Provide specific planetary names, house numbers, and dates
- Be detailed and specific, not generic
- Use proper markdown formatting with ## and ### headers
- Analyze ALL provided chart data, not just summaries
"""


def create_goal_analysis_node_llm():
    """Create the LLM for the goal analysis node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def goal_analysis_node(state: AstroGuruState) -> Dict[str, Any]:
    """Goal analysis node: Analyzes horoscope for specific goals"""
    logger.info("Goal analysis node: Starting goal analysis")
    
    birth_details = state.get("birth_details")
    chart_data = state.get("chart_data")
    dasha_data = state.get("dasha_data")
    
    if not birth_details or not chart_data:
        logger.warning("Goal analysis node: Missing required data, skipping")
        return {"current_step": "dasha"}
    
    goals = birth_details.get("goals", [])
    if not goals:
        # Provide general life analysis
        goals = ["general"]
        logger.info("Goal analysis node: No specific goals provided, using general analysis")
    
    logger.info(f"Goal analysis node: Analyzing goals: {goals}")
    
    # Use LLM to generate goal-specific analysis
    llm = create_goal_analysis_node_llm()
    
    # Prepare FULL chart data (not truncated) - use JSON for proper structure
    import json
    chart_data_full = {
        "lagna": chart_data.get("lagna", {}),
        "planetary_positions": chart_data.get("planetary_positions", {}),
        "house_positions": chart_data.get("house_positions", []),
        "divisional_charts": chart_data.get("divisional_charts", {}),
        "shadbala": chart_data.get("shadbala", {}),
    }
    chart_data_json = json.dumps(chart_data_full, indent=2, default=str)
    
    # Get full dasha analysis (not truncated)
    dasha_analysis_full = dasha_data.get('analysis', 'No dasha analysis available') if dasha_data else 'No dasha data available'
    
    prompt = f"""Analyze the following horoscope for the specified goals and provide comprehensive analysis following the EXACT format specified in the system prompt.

Birth Details:
- Name: {birth_details.get('name', 'N/A')}
- Date of Birth: {birth_details.get('date_of_birth', 'N/A')}
- Time of Birth: {birth_details.get('time_of_birth', 'N/A')}
- Place: {birth_details.get('place_of_birth', 'N/A')}
- Goals: {', '.join(goals) if isinstance(goals, list) else goals}

Complete Chart Data (use ALL of this data):
{chart_data_json}

Complete Dasha Analysis:
{dasha_analysis_full}

**IMPORTANT**: 
- Use ALL the chart data provided above - analyze specific planetary positions, houses, and yogas
- Reference the complete dasha analysis provided
- **CRITICAL**: Consider Gochara (planetary transits) from the system prompt when making predictions
- Combine Dasha periods with Gochara transits to provide accurate timing predictions
- Reference specific Gochara transit dates when providing forecasts and timing suggestions
- Follow the EXACT section structure from the system prompt for each goal
- Include specific planetary names, house numbers, signs, and aspects
- Be detailed and specific - do not provide generic analysis
- Use proper markdown formatting with ## and ### headers as specified"""
    
    try:
        logger.info("Goal analysis node: Calling LLM for goal analysis")
        response = await llm.ainvoke([
            SystemMessage(content=GOAL_ANALYSIS_NODE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        goal_analysis = response.content
        logger.info(f"Goal analysis node: Goal analysis generated successfully, length: {len(goal_analysis)}")
        
        return {
            "goal_analysis_data": {
                "goals": goals,
                "analysis": goal_analysis
            },
            "current_step": "recommendation"
        }
    except Exception as e:
        logger.error(f"Goal analysis node: Error generating goal analysis: {e}", exc_info=True)
        return {"error": f"Goal analysis failed: {str(e)}", "current_step": "dasha"}

