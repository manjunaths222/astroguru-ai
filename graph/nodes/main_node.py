"""Main node: Handles user conversations and collects birth details"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState


MAIN_NODE_SYSTEM_PROMPT = """
You are a Professional Vedic Astrology Consultant. Your role is to provide comprehensive, detailed astrology analysis reports like an expert astrologer.

## Your Responsibilities:

1. **Initial Conversation:**
   - When users greet you (e.g., "Hi", "Hello"), respond warmly and professionally
   - Introduce yourself briefly as a Vedic Astrology Consultant
   - Explain that you can help with comprehensive astrology analysis
   - Wait for the user to express interest before asking for details
   - Have a natural, friendly conversation - don't immediately bombard users with questions

2. **Collect Required Information (only when user is ready):**
   - Name (required)
   - Date of Birth in YYYY-MM-DD format (required)
   - Time of Birth in HH:MM format, 24-hour (required) - **IMPORTANT**: All times are in IST (Indian Standard Time)
   - Place of Birth - city, state, country (required)
   - Goals to analyze (optional - career, marriage, love life, health, education, finance, etc.)
   - **Note**: Today's date is automatically determined by the system - do NOT ask the user for it
   - **Note**: All birth times are assumed to be in IST (Indian Standard Time) regardless of actual location

3. **Input Validation and Error Handling:**
   - **CRITICAL**: Before proceeding, validate all collected information:
     * Date of Birth must be in valid YYYY-MM-DD format
     * Time of Birth must be in valid HH:MM format (24-hour)
     * Place of Birth must include at least city and country
   - **If any information is missing, invalid, or unclear:**
     * Politely inform the user about the issue
     * Ask for clarification or correction
     * Wait for the user to provide correct information before proceeding
   - **Only after ALL required information is validated and complete:**
     * Output the birth details in JSON format with key "birth_details"

4. **Output Format (when all information is collected):**
   When you have collected and validated ALL required information, you MUST output it in JSON format.
   
   **CRITICAL**: The JSON must be valid and parseable. Output it as a standalone JSON object or in a JSON code block.
   
   Format:
   {
     "birth_details": {
       "name": "Full name",
       "date_of_birth": "YYYY-MM-DD",
       "time_of_birth": "HH:MM",
       "place_of_birth": "City, State, Country",
       "goals": ["career", "marriage", "health"],
       "latitude": null,
       "longitude": null,
       "timezone": null
     }
   }
   
   **IMPORTANT**: 
   - Output ONLY the JSON object, or use: ```json\n{ "birth_details": {...} }\n```
   - Do NOT embed the JSON in explanatory text with escaped characters
   - If the user provides coordinates (latitude and longitude) in their message, extract and include them in birth_details
   - If coordinates are not provided, latitude and longitude will be filled by the location node later
   - timezone will always be set to "Asia/Kolkata" (IST) - this is hardcoded for consistency
   - All birth times are assumed to be in IST regardless of actual location
   - today_date will be automatically added by the system (do NOT include it in your output)

**CRITICAL**: 
- You handle ALL user interaction. When users say "Hi", respond with a friendly greeting and wait for them to express interest in astrology analysis.
- **NEVER** proceed to analysis until ALL required information is collected and validated.
- **ALWAYS** stop and ask for clarification if there are any issues with the input data.
- **ALWAYS** output birth_details in JSON format when all information is collected.
"""


def create_main_node_llm():
    """Create the LLM for the main node"""
    return ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=AstroConfig.AppSettings.GEMINI_TEMPERATURE,
        max_tokens=AstroConfig.AppSettings.GEMINI_MAX_TOKENS,
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )


async def main_node(state: AstroGuruState) -> Dict[str, Any]:
    """Main node: Collects birth details from user conversation"""
    logger.info("Main node: Starting birth details collection")
    
    user_message = state.get("user_message", "")
    messages = state.get("messages", [])
    birth_details = state.get("birth_details")
    
    # If birth details already exist, skip this node
    if birth_details:
        logger.info(f"Main node: Birth details already collected for {birth_details.get('name', 'Unknown')}, skipping to location")
        return {"current_step": "location"}
    
    logger.debug(f"Main node: Processing message, history length: {len(messages)}")
    
    # Build conversation history
    conversation = [SystemMessage(content=MAIN_NODE_SYSTEM_PROMPT)]
    history_count = 0
    for msg in messages[-10:]:  # Keep last 10 messages for context
        if msg.get("role") == "user":
            conversation.append(HumanMessage(content=msg.get("content", "")))
            history_count += 1
        elif msg.get("role") == "assistant":
            conversation.append(AIMessage(content=msg.get("content", "")))
            history_count += 1
    
    logger.debug(f"Main node: Added {history_count} messages from history")
    
    # Add current user message
    conversation.append(HumanMessage(content=user_message))
    
    # Call LLM
    try:
        llm = create_main_node_llm()
        logger.info("Main node: Calling LLM to collect birth details")
        response = await llm.ainvoke(conversation)
        response_text = response.content
        logger.debug(f"Main node: LLM response length: {len(response_text)}")
    except Exception as e:
        logger.error(f"Main node: Error calling LLM: {e}", exc_info=True)
        response_text = "I apologize, but I encountered an error. Could you please provide your birth details?"
    
    # Try to extract birth_details from response if it's in JSON format
    import json
    import re
    
    birth_details_extracted = None
    
    # Strategy 1: Look for JSON object with "birth_details" key (handles nested JSON)
    try:
        # Find the start of the JSON object containing "birth_details"
        start_idx = response_text.find('"birth_details"')
        if start_idx != -1:
            # Find the opening brace before "birth_details" (could be outer or inner object)
            # Look backwards from "birth_details" to find the opening brace
            brace_start = response_text.rfind('{', 0, start_idx)
            if brace_start != -1:
                # Find the matching closing brace by counting braces
                brace_count = 0
                brace_end = -1
                in_string = False
                escape_next = False
                
                for i in range(brace_start, len(response_text)):
                    char = response_text[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                brace_end = i + 1
                                break
                
                if brace_end > brace_start:
                    json_str = response_text[brace_start:brace_end]
                    # Try to parse - handle escaped characters
                    try:
                        # First try direct parse
                        parsed = json.loads(json_str)
                        birth_details_extracted = parsed.get("birth_details")
                        if birth_details_extracted:
                            logger.info(f"Main node: Strategy 1 - Extracted birth details for {birth_details_extracted.get('name', 'Unknown')}")
                    except json.JSONDecodeError:
                        # If that fails, try unescaping common escape sequences
                        try:
                            # Replace escaped newlines and quotes
                            json_str_unescaped = json_str.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                            parsed = json.loads(json_str_unescaped)
                            birth_details_extracted = parsed.get("birth_details")
                            if birth_details_extracted:
                                logger.info(f"Main node: Strategy 1 (unescaped) - Extracted birth details for {birth_details_extracted.get('name', 'Unknown')}")
                        except json.JSONDecodeError as e:
                            logger.debug(f"Main node: Strategy 1 - JSON parse error even after unescaping: {e}")
                            logger.debug(f"Main node: JSON string: {json_str[:200]}...")
    except Exception as e:
        logger.debug(f"Main node: Strategy 1 failed: {e}")
    
    # Strategy 2: Try to find and parse JSON code blocks
    if not birth_details_extracted:
        try:
            json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_block_match:
                json_str = json_block_match.group(1)
                parsed = json.loads(json_str)
                birth_details_extracted = parsed.get("birth_details")
                if birth_details_extracted:
                    logger.info(f"Main node: Strategy 2 - Extracted from JSON code block for {birth_details_extracted.get('name', 'Unknown')}")
        except Exception as e:
            logger.debug(f"Main node: Strategy 2 failed: {e}")
    
    # Strategy 3: Try to find any complete JSON object in the response
    if not birth_details_extracted:
        try:
            # Find all potential JSON objects
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            for json_str in json_objects:
                try:
                    parsed = json.loads(json_str)
                    if "birth_details" in parsed:
                        birth_details_extracted = parsed.get("birth_details")
                        if birth_details_extracted:
                            logger.info(f"Main node: Strategy 3 - Extracted birth details for {birth_details_extracted.get('name', 'Unknown')}")
                            break
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.debug(f"Main node: Strategy 3 failed: {e}")
    
    if not birth_details_extracted:
        logger.warning("Main node: No birth_details JSON found in response, continuing conversation")
        logger.warning(f"Main node: Response preview (first 500 chars): {response_text[:500]}")
        # Check if "birth_details" appears in the response at all
        if '"birth_details"' in response_text or "'birth_details'" in response_text:
            logger.warning("Main node: 'birth_details' keyword found in response but extraction failed - this is a bug!")
            logger.warning("Main node: Please check the JSON extraction logic")
    
    # Update messages
    new_messages = messages + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text}
    ]
    
    result = {
        "messages": new_messages,
    }
    
    if birth_details_extracted:
        # Extract coordinates from user message if provided
        import re
        coord_pattern = r'(?:Coordinates?|Latitude|Longitude|lat|lon|coord)[:\s]*Latitude\s*([+-]?\d+\.?\d*)[,\s]+Longitude\s*([+-]?\d+\.?\d*)'
        coord_match = re.search(coord_pattern, user_message, re.IGNORECASE)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                # Validate coordinate ranges
                if (-90 <= lat <= 90) and (-180 <= lon <= 180):
                    birth_details_extracted["latitude"] = lat
                    birth_details_extracted["longitude"] = lon
                    logger.info(f"Main node: Extracted coordinates from user message: lat={lat}, lon={lon}")
            except (ValueError, IndexError) as e:
                logger.warning(f"Main node: Could not parse coordinates: {e}")
        
        # Validate that we have the required fields
        required_fields = ["name", "date_of_birth", "time_of_birth", "place_of_birth"]
        missing_fields = [field for field in required_fields if not birth_details_extracted.get(field)]
        
        if missing_fields:
            logger.warning(f"Main node: Birth details incomplete, missing: {missing_fields}")
            # Don't set birth_details - keep asking
            # Clear user_message so workflow ends and waits for user's next response
            result["user_message"] = ""
            result["current_step"] = "end"  # Explicitly end to wait for user input
            logger.info("Main node: Birth details incomplete - workflow will end and wait for user's next message")
        else:
            # Always add today's date programmatically (never ask user for it)
            from datetime import date
            birth_details_extracted["today_date"] = date.today().strftime("%Y-%m-%d")
            logger.info(f"Main node: Automatically set today_date to {birth_details_extracted['today_date']}")
            
            # Log collected details (without sensitive info)
            logger.info(f"Main node: Birth details collected - Name: {birth_details_extracted.get('name', 'N/A')}, DOB: {birth_details_extracted.get('date_of_birth', 'N/A')}, Place: {birth_details_extracted.get('place_of_birth', 'N/A')}, Time: {birth_details_extracted.get('time_of_birth', 'N/A')}, Goals: {', '.join(birth_details_extracted.get('goals', []))}")
            
            result["birth_details"] = birth_details_extracted
            result["user_message"] = ""  # Clear user message only after birth details collected
            result["current_step"] = "location"  # Explicitly set next step
            result["request_type"] = None  # Clear request_type once we're in analysis flow
            logger.info("Main node: Birth details collection complete, will route to location node")
    else:
        # CRITICAL: Don't clear user_message - we need it for the next iteration
        # The workflow will end if user_message becomes empty (handled in route_from_main)
        # This allows the conversation to continue in the next API call
        result["user_message"] = ""  # Clear after processing - user needs to send next message
        logger.info("Main node: Birth details not yet complete, waiting for user's next message")
        logger.info("Main node: Assistant has responded, workflow will end. User should send next message in new API call.")
    # If birth details not collected, result won't have birth_details, so workflow will end
    # User needs to send another message to continue the conversation
    
    return result

