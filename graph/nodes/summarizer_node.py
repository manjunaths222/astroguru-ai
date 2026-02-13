"""Summarizer node: Combines all analysis into a comprehensive report"""

from typing import Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState
from graph.constants import GOCHARA_CONTEXT


SUMMARIZER_NODE_SYSTEM_PROMPT = f"""
You are a Professional Vedic Astrology Report Summarizer.

Your role is to synthesize all the specialized analysis from previous nodes (location, chart, Dasha, Gochara transits, goal analysis, and recommendations) into a clear, concise, and user-friendly astrology report that is easy to understand for general users.

{GOCHARA_CONTEXT}

**CRITICAL GUIDELINES:**

1. **Simplify Language**: Use plain, everyday language. Avoid astrology jargon entirely. Instead of technical terms like "Dasha", "Gochara", "Lagna", "house", "transit", use simple descriptions like "life period", "current phase", "planetary influences", "your personality", "areas of life". When you must reference astrological concepts, explain them in everyday terms.

2. **Summarize Effectively**: Don't include every detail verbatim. Instead, extract and present the most important insights, general timeframes (not excessive specific dates), and actionable recommendations.

3. **Preserve Critical Information**: While summarizing, ensure you retain:
   - General timeframes and key milestones (limit to 2-3 important dates per section, not exhaustive lists)
   - Specific recommendations and remedies
   - Key strengths and areas of concern
   - Actionable advice
   - Current and upcoming life phases (described simply, not with technical terms)

4. **Make it Personal and Warm**: Write as if speaking directly to the person, using "you" and "your" rather than third person.

5. **Focus on Practical Value**: Emphasize what the person can do, when to take action, and what to expect.

**OUTPUT FORMAT:**

## Your Astrology Report

**Name:** [Full Name]  
**Date of Birth:** [DOB]  
**Time of Birth:** [TOB]  
**Place of Birth:** [Place]  
**Your Goals:** [List goals]

---

### 1. Introduction

[Greet the person warmly, acknowledge their birth details, provide a brief overview of what the report contains, and set expectations]

---

### 2. Birth Chart Overview

[Summarize the key points from the chart analysis in simple, everyday language:
- Your core personality traits and natural inclinations (1-2 sentences - avoid using "Ascendant" or "Lagna", just describe what it means)
- 3-5 most important influences in your life and what they mean for you (describe in plain language, not technical positions)
- Overall life support - are you generally well-supported or facing challenges? (2-3 sentences)
- Key strengths and areas to focus on (bullet points, simple language)]

#### Key Influences in Your Life
- [List key influences with their meaning in everyday terms - avoid technical terms like "house", "sign", "aspect", "conjunction"]
- [Focus on what these mean for the person, not the astrological mechanics]

#### Areas of Life
- **Strong Areas**: [Which areas of life are well-supported and why - use simple descriptions]
- **Areas to Focus On**: [Which areas need attention - describe in practical terms]
- **Important Combinations**: [Key strengths or patterns in simple language - avoid technical terms like "Yogas"]

### 3. Your Current Life Period

[Summarize your current life phase in simple, everyday language:
- What phase you're currently in (e.g., "You're in a period focused on communication and learning" - explain what this means for daily life)
- General timeframe (e.g., "This phase started recently and will continue for the next few years")
- Current influences affecting you (describe in plain language - e.g., "strong support for career growth" instead of "Jupiter in 10th house")
- What to expect during this period (3-5 key points in simple language)
- When the next significant phase begins and what it might bring (1-2 sentences, general timeframe only)]

**Language Guidelines**:
- Use everyday language - avoid terms like "Dasha", "Gochara", "transit", "house", "Lagna"
- Instead of technical terms, describe the effects and what they mean for the person
- Focus on general timeframes (e.g., "next year", "in a few years") rather than specific dates

**Include**: General timeframes, key themes, what to expect, encouraging guidance.

**Avoid**: 
- Excessive specific dates (limit to 1-2 key milestones)
- Technical astrology terminology
- Complex calculations or explanations
- Listing every planetary movement

---

### 4. Insights for Your Goals

[For EACH goal, provide a concise summary in simple, everyday language:
- What your chart reveals about this area of life (3-5 sentences in plain language - avoid technical terms like "Dasha", "Gochara", "house", "Lagna" unless briefly explained)
- What to expect:
  - Short-term (next 1-2 years): [General trends and themes - describe what's happening now and in the near future, what opportunities or challenges are emerging, use simple language like "upcoming months" or "next year" rather than specific dates. Include 2-3 key points about immediate focus areas.]
  - Medium-term (2-5 years): [Broader patterns and opportunities - describe evolving situations, potential growth areas, and how things might develop. Focus on general timeframes like "in the next few years" or "around mid-decade", not exact dates. Include 2-3 key developments to watch for.]
  - Long-term (5-10 years): [Overall direction and potential - describe the bigger picture trajectory, major life themes, and where things are heading. Keep it high-level and encouraging, focusing on general direction rather than specifics. Include 1-2 key long-term themes.]
- Best times to take action (mention only 2-3 key periods in general terms like "mid-2026" or "late 2027", not multiple specific dates)
- Key challenges and opportunities (bullet points in simple language - avoid astrology jargon)
- What to focus on (3-5 actionable points in everyday language)]

**Format**: Use subheadings for each goal (e.g., "### Career", "### Relationships")

**Language Guidelines**:
- Use plain, conversational language - write as if explaining to a friend
- Avoid technical terms: Instead of "Dasha", say "life period" or "current phase". Instead of "Gochara transit", say "planetary movement" or just describe the effect
- Instead of "Jupiter in your 10th house", say "favorable career influences" or "strong career support"
- Instead of "Ketu-Ketu Dasha", say "a period of introspection" or "a time for reflection"
- Focus on what it means for the person, not the technical astrological mechanics

**Include**: General timeframes (not excessive dates), actionable advice, realistic expectations, encouraging tone.

**Avoid**: 
- Excessive specific dates (limit to 2-3 key milestones per goal)
- Astrology jargon without explanation (Dasha, Gochara, Lagna, houses, divisional charts, etc.)
- Repetitive technical analysis
- Complex astrological combinations
- Listing every planetary movement or transit date

---

### 5. Recommendations and What You Can Do

[Summarize the most important recommendations:
- Top 3-5 actionable remedies or practices (simple, practical)
- When to start these practices (if timing matters)
- What to be cautious about (2-4 key points)
- General lifestyle suggestions (2-4 points)]

**Format**: Use clear bullet points, simple language, practical actions.

**Include**: Specific mantras or practices (simplified), timing suggestions, priority actions.

**Avoid**: Long lists of all remedies, complex ritual instructions, overwhelming detail.

---

### 6. Summary and Next Steps

[Provide a warm, encouraging conclusion:
- 3-5 key takeaways from the entire analysis
- Most important action items (3-5 points)
- Encouragement and positive outlook
- When to revisit or check in again (if relevant)]

**Tone**: Supportive, realistic, empowering, not overly mystical or dramatic.

---

**CRITICAL REQUIREMENTS**:
- Keep the total report length reasonable (aim for 800-1200 words total)
- Use simple, conversational language
- Explain technical terms when necessary
- Focus on what matters most to the person
- Include specific dates and actionable advice
- Make it feel personal and relevant
- Use proper markdown formatting (##, ###, bullet points)
- Be warm, professional, and encouraging
"""


def create_summarizer_node_llm():
    """Create the LLM for the summarizer node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def summarizer_node(state: AstroGuruState) -> Dict[str, Any]:
    """Summarizer node: Combines all analysis into a comprehensive report"""
    logger.info("Summarizer node: Starting comprehensive summary generation")
    
    birth_details = state.get("birth_details")
    location_data = state.get("location_data")
    chart_data = state.get("chart_data")
    dasha_data = state.get("dasha_data")
    goal_analysis_data = state.get("goal_analysis_data")
    recommendation_data = state.get("recommendation_data")
    
    if not birth_details:
        logger.warning("Summarizer node: Missing birth details, skipping")
        return {"current_step": "recommendation"}
    
    logger.debug(f"Summarizer node: Combining analysis for {birth_details.get('name', 'Unknown')} - has location: {bool(location_data)}, has chart: {bool(chart_data)}, has dasha: {bool(dasha_data)}, has goals: {bool(goal_analysis_data)}, has recommendations: {bool(recommendation_data)}")
    
    # Use LLM to generate comprehensive summary
    llm = create_summarizer_node_llm()
    
    # Build context from all analyses - use FULL data, not truncated
    context_parts = []
    
    if location_data:
        context_parts.append(f"Location: {location_data.get('place_name', 'N/A')} ({location_data.get('latitude', 'N/A')}, {location_data.get('longitude', 'N/A')})")
    
    if chart_data:
        lagna_info = chart_data.get('lagna', {})
        context_parts.append(f"Chart: Lagna {lagna_info.get('sign', 'N/A')}, Lagna Lord: {lagna_info.get('lord', 'N/A')}")
        # Include key planetary positions
        planetary_positions = chart_data.get('planetary_positions', {})
        if planetary_positions:
            context_parts.append(f"Key Planetary Positions: {json.dumps(planetary_positions, indent=2, default=str)}")
    
    # Use FULL analysis data, not truncated
    if dasha_data:
        context_parts.append(f"Complete Dasha Analysis:\n{dasha_data.get('analysis', 'No dasha analysis')}")
    
    if goal_analysis_data:
        context_parts.append(f"Complete Goal Analysis:\n{goal_analysis_data.get('analysis', 'No goal analysis')}")
    
    if recommendation_data:
        context_parts.append(f"Complete Recommendations:\n{recommendation_data.get('recommendations', 'No recommendations')}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""Create a clear, concise, and user-friendly astrology report based on the following analysis. Follow the format and guidelines in the system prompt.

Birth Details:
- Name: {birth_details.get('name', 'N/A')}
- Date of Birth: {birth_details.get('date_of_birth', 'N/A')}
- Time of Birth: {birth_details.get('time_of_birth', 'N/A')}
- Place: {birth_details.get('place_of_birth', 'N/A')}
- Goals: {', '.join(birth_details.get('goals', [])) if isinstance(birth_details.get('goals'), list) else birth_details.get('goals', 'N/A')}

Analysis Data Available:
{context}

**CRITICAL INSTRUCTIONS**:
- Follow the section structure from the system prompt
- **SUMMARIZE** the analysis - extract key insights, general timeframes (NOT excessive specific dates), and actionable recommendations
- **CRITICAL**: Avoid astrology jargon - use everyday language instead:
  - Instead of "Dasha" → "life period" or "current phase"
  - Instead of "Gochara" or "transit" → "planetary influences" or just describe the effect
  - Instead of "house" → "area of life" or describe what it means
  - Instead of "Lagna" → "your personality" or "your chart"
  - Instead of technical planetary positions → describe what they mean for the person
- Limit specific dates to 2-3 key milestones per section - focus on general timeframes (e.g., "next year", "in a few years", "mid-2026")
- Use simple, conversational language throughout - write as if explaining to a friend
- Focus on what matters most: general timeframes, actionable advice, key insights in plain language
- Keep it concise but comprehensive (aim for 800-1200 words total)
- Make it personal and warm - use "you" and "your"
- Prioritize practical value and understanding over technical detail
- Use proper markdown formatting with ##, ###, and bullet points
- Do NOT use placeholders - use actual values from birth details
- Make it feel like a helpful, friendly guide, not a technical astrological manual"""
    
    try:
        logger.info("Summarizer node: Calling LLM for comprehensive summary")
        response = await llm.ainvoke([
            SystemMessage(content=SUMMARIZER_NODE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        summary = response.content
        logger.info(f"Summarizer node: Summary generated successfully, length: {len(summary)}")
        
        # Create analysis context for chat
        analysis_context = f"""Birth Details:
- Name: {birth_details.get('name', 'N/A')}
- Date of Birth: {birth_details.get('date_of_birth', 'N/A')}
- Time of Birth: {birth_details.get('time_of_birth', 'N/A')}
- Place: {birth_details.get('place_of_birth', 'N/A')}

{summary}"""
        
        logger.info(f"Summarizer node: Analysis complete for {birth_details.get('name', 'Unknown')}, context length: {len(analysis_context)}")
        return {
            "summary": summary,
            "analysis_context": analysis_context,
            "analysis_complete": True,
            "current_step": "end",
            "request_type": None  # Clear request_type after analysis is complete
        }
    except Exception as e:
        logger.error(f"Summarizer node: Error generating summary: {e}", exc_info=True)
        return {"error": f"Summary generation failed: {str(e)}", "current_step": "recommendation"}

