# pip install google-adk google-generativeai mcp python-dotenv
import asyncio
import os
import json
# Either keep logging if we need it
import logging
from dotenv import load_dotenv
from google.genai import types
# Remove genai import if only used for configuration and that's been removed
# import google.generativeai as genai
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Load environment variables from .env file
load_dotenv()

# Enable debug logging (keep this if you want logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Step 1: Get tools from MCP server ---
async def get_tools_async():
    """Gets tools from the restaurant Search MCP Server."""
    print("Attempting to connect to MCP restaurant Search server...")
    server_params = StdioServerParameters(
        command="python",
        args=["C:\\DEV\\mcp_tool_server_restaurant\\main.py"],
        env=None,
    )
    
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=server_params
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack

# --- Step 2: Define ADK Agent Creation ---
async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""
    tools, exit_stack = await get_tools_async()
    print(f"Fetched {len(tools)} tools from MCP server.")
    
    # Create the LlmAgent matching the example structure
    root_agent = LlmAgent(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17"), 
        name='restaurant_search_assistant',
        instruction='Help user to search for restaurants using available tools based on prompt.',
        tools=tools,
    )
    
    return root_agent, exit_stack

# --- Step 3: Main Execution Logic ---
async def async_main():
    # Create services
    session_service = InMemorySessionService()

    # Create a session
    session = session_service.create_session(
        state={}, app_name='restaurant_search_app', user_id='user_restaurants'
    )

    # Define the user prompt
    query = "Find Restaurant from Paris "
    print(f"User Query: '{query}'")
    
    # Format input as types.Content
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Get agent and exit_stack
    root_agent, exit_stack = await get_agent_async()

    # Create Runner
    runner = Runner(
        app_name='restaurant_search_app',
        agent=root_agent,
        session_service=session_service,
    )

    print("Running agent...")
    events_async = runner.run_async(
        session_id=session.id, 
        user_id=session.user_id, 
        new_message=content
    )

    async for event in events_async:
        print(f"Event received: {event}")

    
    # Always clean up resources
    print("Closing MCP server connection...")
    await exit_stack.aclose()
    print("Cleanup complete.")

# --- Step 4: Run the Main Function ---
if __name__ == "__main__":
    # Ensure the API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    # Run the main async function
    asyncio.run(async_main())
