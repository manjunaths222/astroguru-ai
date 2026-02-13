"""Recommendation node: Provides recommendations and remedies"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState
from graph.constants import GOCHARA_CONTEXT


RECOMMENDATION_NODE_SYSTEM_PROMPT = f"""
You are a Professional Vedic Astrology Remedies and Recommendations Specialist.

Your role is to provide detailed, actionable recommendations, remedies, and guidance based on 
comprehensive horoscope analysis, Dasha periods, Gochara (planetary transits), and goal-specific insights.

{GOCHARA_CONTEXT}

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**

You MUST provide recommendations with the following EXACT structure:

## Recommendations and Remedies

### A. General Recommendations
- **Actionable Advice**: [Specific actions to take]
- **Lifestyle Changes**: [Lifestyle modifications]
- **Behavioral Adjustments**: [How to adjust behavior]

### B. Remedies by Category

#### 1. Gemstones (Ratna)
- **Recommended Gemstones**: [Specific gemstones with their benefits]
- **How to Wear**: [Wearing instructions]
- **When to Wear**: [Best times/days]
- **Alternative Options**: [If primary gemstone is not available]

#### 2. Mantras (Chanting)
- **Primary Mantras**: [Main mantras to chant]
- **Chanting Schedule**: [How many times, when, for how long]
- **Pronunciation Guide**: [How to pronounce correctly]
- **Best Times**: [Auspicious times for chanting]

#### 3. Yantras and Poojas
- **Recommended Yantras**: [Which yantras to use]
- **Poojas to Perform**: [Specific poojas and their benefits]
- **Frequency**: [How often to perform]

#### 4. Charity and Donations (Dana)
- **What to Donate**: [Specific items to donate]
- **To Whom**: [Who should receive donations]
- **Best Days**: [Auspicious days for charity]
- **Frequency**: [How often]

#### 5. Fasting (Vrata)
- **Recommended Fasts**: [Which days to fast]
- **Fasting Guidelines**: [How to observe the fast]
- **Benefits**: [What benefits to expect]

#### 6. Color Therapy
- **Favorable Colors**: [Colors to wear/use]
- **Colors to Avoid**: [Colors to minimize]
- **Best Days**: [When to use specific colors]

#### 7. Directional Remedies
- **Favorable Directions**: [Directions to face/work towards]
- **Sleep Direction**: [Which direction to sleep]
- **Work Direction**: [Office/workplace orientation]

### C. Timing Suggestions (Based on Dasha and Gochara)
- **Best Dates/Times**: [Specific auspicious dates and times - reference favorable Gochara transit periods]
- **Auspicious Periods**: [Favorable time periods - consider both Dasha and Gochara combinations]
- **Dates to Avoid**: [Inauspicious dates - reference challenging Gochara transit periods]
- **Important Transitions**: [Key dates for major decisions - include Gochara transit change dates]
- **Gochara-Based Timing**: [Specific recommendations based on Jupiter, Saturn, Rahu, and Ketu transits]

### D. Precautions
- **Things to Avoid**: [Specific things to avoid]
- **Challenging Periods**: [When to be extra cautious]
- **Warning Signs**: [What to watch out for]

### E. Priority Remedies
- **Most Important**: [Top priority remedies with urgency]
- **Secondary**: [Important but less urgent]
- **Long-term**: [Remedies for long-term benefit]

**IMPORTANT**: 
- Use the EXACT section headers shown above
- Provide specific, actionable recommendations - not generic advice
- Include specific mantras, gemstones, dates, and instructions
- Be detailed and specific
- Use proper markdown formatting with ##, ###, and #### headers
"""


def create_recommendation_node_llm():
    """Create the LLM for the recommendation node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def recommendation_node(state: AstroGuruState) -> Dict[str, Any]:
    """Recommendation node: Generates recommendations and remedies"""
    logger.info("Recommendation node: Starting recommendation generation")
    
    birth_details = state.get("birth_details")
    chart_data = state.get("chart_data")
    dasha_data = state.get("dasha_data")
    goal_analysis_data = state.get("goal_analysis_data")
    
    if not birth_details:
        logger.warning("Recommendation node: Missing birth details, skipping")
        return {"current_step": "goal_analysis"}
    
    logger.debug(f"Recommendation node: Processing recommendations for {birth_details.get('name', 'Unknown')}, goals: {birth_details.get('goals', [])}")
    
    # Use LLM to generate recommendations
    llm = create_recommendation_node_llm()
    
    # Get full analysis data (not truncated)
    import json
    dasha_analysis_full = dasha_data.get('analysis', 'No dasha analysis available') if dasha_data else 'No dasha data available'
    goal_analysis_full = goal_analysis_data.get('analysis', 'No goal analysis available') if goal_analysis_data else 'No goal analysis available'
    
    # Get key chart info
    lagna_sign = chart_data.get('lagna', {}).get('sign', 'N/A') if chart_data else 'N/A'
    lagna_lord = chart_data.get('lagna', {}).get('lord', 'N/A') if chart_data else 'N/A'
    
    prompt = f"""Based on the following horoscope analysis, provide comprehensive recommendations and remedies following the EXACT format specified in the system prompt.

Birth Details:
- Name: {birth_details.get('name', 'N/A')}
- Goals: {', '.join(birth_details.get('goals', [])) if isinstance(birth_details.get('goals'), list) else birth_details.get('goals', 'N/A')}

Chart Information:
- Lagna: {lagna_sign}
- Lagna Lord: {lagna_lord}

Complete Dasha Analysis:
{dasha_analysis_full}

Complete Goal Analysis:
{goal_analysis_full}

**IMPORTANT**: 
- Use ALL the analysis provided above to create specific, personalized recommendations
- **CRITICAL**: Consider Gochara (planetary transits) from the system prompt when providing timing suggestions
- Reference specific Gochara transit dates when recommending best times for remedies and actions
- Combine Dasha periods with Gochara transits to provide accurate timing recommendations
- Follow the EXACT section structure from the system prompt
- Provide specific mantras, gemstones, dates, and detailed instructions
- Reference specific planetary positions, dashas, Gochara transits, and chart elements from the analysis
- Be detailed and specific - do not provide generic remedies
- Use proper markdown formatting with ##, ###, and #### headers as specified"""
    
    try:
        logger.info("Recommendation node: Calling LLM for recommendations")
        response = await llm.ainvoke([
            SystemMessage(content=RECOMMENDATION_NODE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        recommendations = response.content
        logger.info(f"Recommendation node: Recommendations generated successfully, length: {len(recommendations)}")
        
        return {
            "recommendation_data": {
                "recommendations": recommendations
            },
            "current_step": "summarizer"
        }
    except Exception as e:
        logger.error(f"Recommendation node: Error generating recommendations: {e}", exc_info=True)
        return {"error": f"Recommendation generation failed: {str(e)}", "current_step": "goal_analysis"}

