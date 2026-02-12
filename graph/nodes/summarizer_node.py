"""Summarizer node: Combines all analysis into a comprehensive report"""

from typing import Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import AstroConfig, logger
from graph.state import AstroGuruState


SUMMARIZER_NODE_SYSTEM_PROMPT = """
You are a Professional Vedic Astrology Report Summarizer.

Your role is to synthesize all the specialized analysis from previous nodes (location, chart, Dasha, goal analysis, and recommendations) into a clear, concise, and user-friendly astrology report that is easy to understand for general users.

**CRITICAL GUIDELINES:**

1. **Simplify Language**: Use plain, everyday language. Avoid excessive astrology jargon. When technical terms are necessary, explain them briefly in simple terms.

2. **Summarize Effectively**: Don't include every detail verbatim. Instead, extract and present the most important insights, key dates, and actionable recommendations.

3. **Preserve Critical Information**: While summarizing, ensure you retain:
   - Important dates and time periods
   - Specific recommendations and remedies
   - Key strengths and areas of concern
   - Actionable advice
   - Current and upcoming planetary periods

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

[Summarize the key points from the chart analysis in simple terms:
- Your Ascendant (Lagna) sign and what it means for your personality (1-2 sentences)
- 3-5 most important planetary positions and their significance
- Overall chart strength - are you generally well-supported or facing challenges? (2-3 sentences)
- Key strengths and areas to focus on (bullet points, simple language)]

#### Key Planetary Positions
- [List key planets with their signs, houses, and significance]
- [Include aspects and conjunctions]

#### House Analysis
- **Strong Houses**: [Which houses are strong and why]
- **Weak Houses**: [Which houses need attention]
- **Key Yogas**: [Important planetary combinations]

### 3. Your Current Life Period (Dasha)

[Summarize the dasha analysis in user-friendly language:
- What period you're currently in (e.g., "You're in a Mercury period" - explain what this means simply)
- How long this period lasts and when it started/ends
- What to expect during this period (3-5 key points)
- When the next significant period begins and what it might bring (1-2 sentences)]

**Include**: Specific dates for period changes, key months/years to watch, general themes.

**Avoid**: Complex dasha calculations, all upcoming periods in detail, technical terminology.

---

### 4. Insights for Your Goals

[For EACH goal, provide a concise summary:
- What your chart says about this area of life (3-5 sentences)
- Best times to take action (specific months/years if available)
- Key challenges and opportunities (bullet points)
- What to focus on (3-5 actionable points)]

**Format**: Use subheadings for each goal (e.g., "### Career", "### Relationships")

**Include**: Specific dates when available, actionable advice, realistic expectations.

**Avoid**: Repetitive technical analysis, all divisional chart details, complex astrological combinations.

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
- **SUMMARIZE** the analysis - extract key insights, important dates, and actionable recommendations
- Use simple, everyday language - avoid excessive astrology jargon
- When technical terms are necessary, explain them briefly
- Focus on what matters most: specific dates, actionable advice, key insights
- Keep it concise but comprehensive (aim for 800-1200 words total)
- Make it personal and warm - use "you" and "your"
- Include specific dates and time periods when available
- Prioritize practical value over technical detail
- Use proper markdown formatting with ##, ###, and bullet points
- Do NOT use placeholders - use actual values from birth details
- Make it feel like a helpful guide, not a technical manual"""
    
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

