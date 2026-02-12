"""Location node: Resolves geographic coordinates using agent and geocoding tools"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_core.caches import BaseCache  # Import to resolve Pydantic v2 forward reference
from config import AstroConfig, logger
from graph.state import AstroGuruState
from tools.geocoding_tools import geocode_address, reverse_geocode


LOCATION_NODE_SYSTEM_PROMPT = """
You are a Professional Location Resolution Specialist for Vedic Astrology.

Your task is to accurately resolve geographic coordinates (latitude, longitude) for place names.
This is critical for accurate horoscope calculations.

**IMPORTANT**: All birth times are assumed to be in IST (Indian Standard Time, Asia/Kolkata).
The timezone field in the output will always be "Asia/Kolkata" - this is hardcoded for consistency.
The actual location's timezone does not affect chart calculations.

## Your Responsibilities:

1. **Use the geocoding tools provided** to get accurate location coordinates
2. **Handle errors gracefully** - If geocoding tool returns an error (e.g., rate limiting, service unavailable):
   - Use your knowledge of geography to estimate coordinates for the place
   - For common cities, use known coordinates (e.g., Bengaluru, India: ~12.97°N, 77.59°E)
   - DO NOT return an error - always provide valid coordinates
3. **Return proper JSON format** with all required fields

## Error Handling:

If geocoding tool returns an error (rate limit, service unavailable, etc.):
- Use your geographic knowledge to provide reasonable coordinate estimates
- For India: Major cities coordinates you know:
  - Bengaluru: 12.9716°N, 77.5946°E
  - Mumbai: 19.0760°N, 72.8777°E
  - Delhi: 28.6139°N, 77.2090°E
  - Chennai: 13.0827°N, 80.2707°E
- Always provide valid coordinates even if geocoding service fails
- DO NOT return an error - always provide a valid JSON response with coordinates

## Output Format:

After using tools (or handling errors), you MUST return ONLY a valid JSON object with this exact structure:
{
  "place_name": "Full Location Name",
  "city": "City Name",
  "state": "State/Province Name",
  "country": "Country Name",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "timezone": "Asia/Kolkata"
}

**CRITICAL**: 
- Return ONLY the JSON object, no other text
- Ensure all fields are present
- timezone MUST always be "Asia/Kolkata" (IST) - this is hardcoded for consistency
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- If geocoding fails, use your knowledge to provide reasonable estimates - DO NOT return an error
- Always provide valid coordinates - the analysis cannot proceed without them
"""


# Create tools for the agent
def create_geocoding_tools():
    """Create geocoding tools for the agent"""
    from langchain_core.tools import tool
    
    @tool
    async def geocode_address_tool(address: str) -> str:
        """Geocode an address to get coordinates and location details. 
        
        Args:
            address: Place name (e.g., "Mumbai, Maharashtra, India")
        
        Returns:
            JSON string with location data including latitude, longitude, timezone
        """
        result = await geocode_address(address)
        import json
        return json.dumps(result, indent=2)
    
    @tool
    async def reverse_geocode_tool(latitude: float, longitude: float) -> str:
        """Reverse geocode coordinates to get location details.
        
        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)
        
        Returns:
            JSON string with location data including place_name, city, state, country, timezone
        """
        result = await reverse_geocode(latitude, longitude)
        import json
        return json.dumps(result, indent=2)
    
    return [geocode_address_tool, reverse_geocode_tool]


def create_location_node_llm():
    """Create the LLM for the location node with tools"""
    llm = ChatGoogleGenerativeAI(
        model=AstroConfig.AppSettings.GEMINI_MODEL,
        temperature=0.1,  # Low temperature for accurate location resolution
        max_tokens=500,  # JSON response doesn't need many tokens
        google_api_key=AstroConfig.AppSettings.GOOGLE_AI_API_KEY,
    )
    # Bind tools to the LLM
    tools = create_geocoding_tools()
    return llm.bind_tools(tools)


async def location_node(state: AstroGuruState) -> Dict[str, Any]:
    """Location node: Resolves geographic coordinates using agent with geocoding tools"""
    logger.info("Location node: Resolving location coordinates")
    
    birth_details = state.get("birth_details")
    if not birth_details:
        logger.warning("Location node: No birth details found, routing back to main")
        return {"current_step": "main", "user_message": ""}
    
    # Prepare input for agent
    place_name = birth_details.get("place_of_birth", "")
    existing_latitude = birth_details.get("latitude")
    existing_longitude = birth_details.get("longitude")
    existing_timezone = birth_details.get("timezone")
    
    # Build prompt for agent
    if existing_latitude and existing_longitude:
        # Coordinates provided - verify and get timezone
        prompt = f"""I have coordinates: latitude={existing_latitude}, longitude={existing_longitude}
Place name: {place_name or 'Not provided'}

Please:
1. Use reverse_geocode_tool to get location details from these coordinates
2. Return a JSON object with: place_name, city, state, country, latitude, longitude, timezone
3. **IMPORTANT**: Always set timezone to "Asia/Kolkata" (IST) - this is hardcoded for consistency

Return ONLY the JSON object."""
    else:
        # Need to geocode from place name
        if not place_name:
            logger.warning("Location node: No place name found, skipping")
            return {"current_step": "main", "error": "Place of birth is required"}
        
        prompt = f"""I need to geocode this place: {place_name}

Please:
1. Use geocode_address_tool to get coordinates for: {place_name}
2. Return a JSON object with: place_name, city, state, country, latitude, longitude, timezone
3. **IMPORTANT**: Always set timezone to "Asia/Kolkata" (IST) - this is hardcoded for consistency

Return ONLY the JSON object."""
    
    # Create agent with tools
    llm = create_location_node_llm()
    tools = create_geocoding_tools()
    tool_map = {tool.name: tool for tool in tools}
    
    # Call agent with tool support
    try:
        messages = [
            SystemMessage(content=LOCATION_NODE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        # Agent execution loop (max 3 iterations to handle tool calls)
        max_iterations = 3
        for iteration in range(max_iterations):
            response = await llm.ainvoke(messages)
            messages.append(response)
            
            # Check if agent wants to call tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Location node: Agent calling {len(response.tool_calls)} tool(s)")
                
                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "")
                    
                    if tool_name in tool_map:
                        try:
                            # Execute the tool
                            tool_result = await tool_map[tool_name].ainvoke(tool_args)
                            
                            # Check if tool returned an error (rate limit, etc.)
                            if isinstance(tool_result, str):
                                try:
                                    import json
                                    tool_result_dict = json.loads(tool_result)
                                    if not tool_result_dict.get("success", True):
                                        error_msg = tool_result_dict.get("error", "Unknown error")
                                        logger.warning(f"Location node: Geocoding tool returned error: {error_msg}")
                                        # Pass error to agent so it can handle it
                                        messages.append(ToolMessage(
                                            content=tool_result,  # Pass full JSON error response
                                            tool_call_id=tool_id
                                        ))
                                    else:
                                        messages.append(ToolMessage(
                                            content=tool_result,
                                            tool_call_id=tool_id
                                        ))
                                except (json.JSONDecodeError, AttributeError):
                                    # Not JSON, pass as-is
                                    messages.append(ToolMessage(
                                        content=tool_result,
                                        tool_call_id=tool_id
                                    ))
                            else:
                                messages.append(ToolMessage(
                                    content=str(tool_result),
                                    tool_call_id=tool_id
                                ))
                        except Exception as e:
                            logger.error(f"Location node: Tool execution error: {e}", exc_info=True)
                            messages.append(ToolMessage(
                                content=json.dumps({"success": False, "error": str(e)}),
                                tool_call_id=tool_id
                            ))
                    else:
                        logger.warning(f"Location node: Unknown tool: {tool_name}")
                        messages.append(ToolMessage(
                            content=f"Unknown tool: {tool_name}",
                            tool_call_id=tool_id
                        ))
                
                # Continue loop to let agent process tool results
                continue
            else:
                # Agent returned final response (no more tool calls)
                response_text = response.content
                break
        else:
            # Max iterations reached
            logger.warning("Location node: Max iterations reached, using last response")
            response_text = response.content
        
        # Extract JSON from response
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        if not json_match:
            logger.error("Location node: No JSON found in agent response")
            return {"error": "Agent did not return valid JSON", "current_step": "main"}
        
        try:
            location_data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Location node: Failed to parse JSON: {e}")
            return {"error": "Failed to parse location data", "current_step": "main"}
        
        # Validate required fields
        required_fields = ["latitude", "longitude"]
        missing_fields = [field for field in required_fields if field not in location_data]
        if missing_fields:
            logger.error(f"Location node: Missing required fields: {missing_fields}")
            return {"error": f"Invalid location data: missing {missing_fields}", "current_step": "main"}
        
        # Always use IST (Asia/Kolkata) for chart calculations to avoid confusion
        # The actual location timezone is not used - all birth times are assumed to be in IST
        location_data["timezone"] = "Asia/Kolkata"
        logger.info(f"Location node: Using IST (Asia/Kolkata) for all chart calculations (hardcoded)")
        
        # Validate coordinate ranges
        lat = float(location_data.get("latitude", 0))
        lon = float(location_data.get("longitude", 0))
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.error(f"Location node: Invalid coordinates: lat={lat}, lon={lon}")
            return {"error": "Invalid coordinates", "current_step": "main"}
        
        logger.info(f"Location node: Successfully resolved location: {location_data.get('place_name')} ({lat}, {lon}) with timezone {location_data.get('timezone')}")
        
    except Exception as e:
        logger.error(f"Location node: Error in agent execution: {e}", exc_info=True)
        return {"error": f"Location resolution failed: {str(e)}", "current_step": "main"}
    
    # Ensure location_data was successfully extracted
    if 'location_data' not in locals():
        logger.error("Location node: location_data not defined after agent execution")
        return {"error": "Failed to extract location data", "current_step": "main"}
    
    # Update birth_details with location data
    updated_birth_details = {**birth_details}
    updated_birth_details.update({
        "latitude": float(location_data.get("latitude")),
        "longitude": float(location_data.get("longitude")),
        "timezone": location_data.get("timezone"),
    })
    
    return {
        "birth_details": updated_birth_details,
        "location_data": location_data,
        "current_step": "chart"
    }

