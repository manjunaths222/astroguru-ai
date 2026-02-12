"""Chart node: Generates Vedic astrology charts"""

from typing import Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import AstroConfig, logger
from graph.state import AstroGuruState

# Import tools
from tools.vedastro_tools import get_comprehensive_chart


CHART_NODE_SYSTEM_PROMPT = """
You are a Professional Vedic Astrology Chart Analyst.

Your role is to format raw chart data from jyotishganit into a comprehensive, readable markdown format.

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**

You MUST create a chart analysis with the following EXACT structure:

# Birth Chart Analysis

## Personal Information
- **Name**: [Full Name]
- **Date of Birth**: [YYYY-MM-DD]
- **Time of Birth**: [HH:MM] (IST)
- **Place of Birth**: [Location Name]

## Lagna (Ascendant)
- **Sign**: [Sign Name] (e.g., Scorpio)
- **Degree**: [X]° [Y]′ [Z]″ (e.g., 04° 33′ 21″)
- **Lord**: [Planet Name] (e.g., Mars for Scorpio)
- **Nakshatra**: [Nakshatra Name] [Pada] (e.g., Anuradha 1)

## Rashi (Moon Sign)
- **Sign**: [Sign Name]
- **Nakshatra**: [Nakshatra Name] [Pada]

## Planetary Positions

### Sun
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Degree**: [X]° [Y]′ [Z]″
- **Nakshatra**: [Nakshatra Name] [Pada]

### Moon
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Mars
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Mercury
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Jupiter
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Venus
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Saturn
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Rahu
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

### Ketu
- **Sign**: [Sign Name]
- **House**: [House Number]
- **Nakshatra**: [Nakshatra Name] [Pada]

## House Positions

[For each house (1-12), list the sign, lord, and occupants]

### House 1 (Lagna)
- **Sign**: [Sign Name]
- **Lord**: [Planet Name]
- **Occupants**: [List of planets]

[Repeat for all 12 houses]

## Chart Summary
[Overall interpretation and key highlights]

**IMPORTANT**: 
- Use the EXACT section headers shown above
- Calculate house positions using whole-sign house system based on Lagna sign
- Convert degrees from decimal to degrees/minutes/seconds format (e.g., 4.555833° = 4° 33′ 21″)
- Include ALL planets and ALL houses
- Make it professional, clear, and well-organized
"""


def create_chart_node_llm():
    """Create the LLM for the chart node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def chart_node(state: AstroGuruState) -> Dict[str, Any]:
    """Chart node: Generates comprehensive astrology charts"""
    logger.info("Chart node: Starting chart generation")
    
    birth_details = state.get("birth_details")
    if not birth_details:
        logger.warning("Chart node: No birth details found, skipping")
        return {"current_step": "main"}
    
    # Extract required fields
    date_of_birth = birth_details.get("date_of_birth")
    time_of_birth = birth_details.get("time_of_birth")
    latitude = birth_details.get("latitude")
    longitude = birth_details.get("longitude")
    place_of_birth = birth_details.get("place_of_birth", "")
    name = birth_details.get("name", "Unknown")
    
    logger.debug(f"Chart node: Processing chart for {name} - DOB: {date_of_birth}, TOB: {time_of_birth} (IST), Location: {place_of_birth}")
    
    # Validate required fields
    if not all([date_of_birth, time_of_birth, latitude, longitude]):
        missing = [k for k, v in {
            "date_of_birth": date_of_birth,
            "time_of_birth": time_of_birth,
            "latitude": latitude,
            "longitude": longitude
        }.items() if not v]
        logger.error(f"Chart node: Missing required birth details: {missing}")
        return {"error": f"Missing required birth details: {missing}"}
    
    try:
        logger.info(f"Chart node: Calling get_comprehensive_chart with coordinates ({latitude}, {longitude}) - all times in IST")
        # Call the comprehensive chart tool (always uses IST)
        chart_result = await get_comprehensive_chart(
            date_of_birth=date_of_birth,
            time_of_birth=time_of_birth,
            latitude=float(latitude),
            longitude=float(longitude),
            location_name=place_of_birth,
            years_ahead=10
        )
        
        if not chart_result.get("success"):
            error_msg = chart_result.get("error", "Unknown error")
            logger.error(f"Chart node: Chart generation failed: {error_msg}")
            return {"error": f"Chart generation failed: {error_msg}"}
        
        logger.info(f"Chart node: Chart generated successfully - Lagna: {chart_result.get('lagna', {}).get('sign', 'N/A')}, Planets: {len(chart_result.get('planetary_positions', {}))}")
        
        # Use LLM to format chart data into readable markdown
        try:
            logger.info("Chart node: Formatting chart data with LLM")
            llm = create_chart_node_llm()
            
            # Build prompt with chart data
            chart_data_json = json.dumps(chart_result, indent=2, default=str)
            prompt = f"""Format the following chart data into a comprehensive markdown report following the EXACT format specified in the system prompt.

Birth Details:
- Name: {name}
- Date of Birth: {date_of_birth}
- Time of Birth: {time_of_birth} (IST)
- Place of Birth: {place_of_birth}

Chart Data:
{chart_data_json}

**CRITICAL INSTRUCTIONS**:
- Follow the EXACT section structure from the system prompt
- Calculate house positions using whole-sign house system based on Lagna sign
- Convert decimal degrees to degrees/minutes/seconds format
- Include ALL planets and ALL houses
- Use actual values from the chart data - do NOT use placeholders
- Make it professional, clear, and well-organized"""
            
            response = await llm.ainvoke([
                SystemMessage(content=CHART_NODE_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            
            chart_analysis = response.content
            logger.info(f"Chart node: Chart analysis generated successfully, length: {len(chart_analysis)}")
            
            return {
                "chart_data": chart_result,
                "chart_data_analysis": chart_analysis,
                "current_step": "dasha"
            }
        except Exception as e:
            logger.error(f"Chart node: Error formatting chart with LLM: {e}", exc_info=True)
            # Return chart data even if LLM formatting fails
            return {
                "chart_data": chart_result,
                "chart_data_analysis": None,
                "current_step": "dasha"
            }
    except ValueError as e:
        logger.error(f"Chart node: Validation error during chart generation: {e}", exc_info=True)
        return {"error": f"Chart generation validation error: {str(e)}"}
    except Exception as e:
        logger.error(f"Chart node: Unexpected exception during chart generation: {e}", exc_info=True)
        return {"error": f"Chart generation exception: {str(e)}"}

