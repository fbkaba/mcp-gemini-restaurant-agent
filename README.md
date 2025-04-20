# Restaurants MCP Server

A Model Context Protocol (MCP) server that allows LLMs to search for hotels and destinations using the Booking.com API.

## Features

- Search for locations by name
- Get top restaurants for a given location

## API Integration

This MCP server uses the [Tripadvisor.com API] via RapidAPI. You'll need:

1. A RapidAPI account
2. Subscribe to the Tripadvisor.com API
3. Get your API key

The current implementation uses two endpoints:
- `//api/v1/restaurant/searchLocation`: Search for locations
- `"/api/v1/restaurant/searchRestaurants`: Get restaurants for a location

## Setup and Installation

### Prerequisites

- Python 3.11+
- MCP SDK (`pip install mcp`)
- httpx (`pip install httpx`)
- python-dotenv (`pip install python-dotenv`)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/username/hotels_mcp_server.git
   cd hotels_mcp_server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your RapidAPI credentials:
   - Copy `.env.example` to `.env`
   - Add your RapidAPI key from [Tripadvisor.com API on RapidAPI] to the `.env` file

### Running the Server

Run the server with:

```bash
python main.py
```

The server uses stdio transport by default for compatibility with MCP clients like Cursor.

## Using with MCP Clients



### Gemini Model

Test your server with Gemini Model gemini-2.5-flash-preview-04-17:

```bash
  python agent_gemini.py
```

This will send a prompt to finds restaurants for a given city using the mcp tools
- View available tools
- Send requests 
- See gemini using the search_location followed by get_restaurants
- Display restaurants list for a given city, example Paris

### Claude

1. Edit `claude_desktop_config.json`:
   ```json
   {
     "restaurants": {
       "command": "python",
       "args": [
         "/path/to/mcp_tool_server_restaurantr/main.py"
       ]
     }
   }
   ```

2. Restart Claude

3. Use natural language to search for restaurants in Claude:
   - "Find restaurants in Paris"

### MCP Inspector

Test your server with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python main.py
```

This opens an interactive UI where you can:
- View available tools
- Send test requests
- See server responses

## Available Tools

1. `search_locations`: Search for destinationslocations by name
   - Parameter: `query` - Location name (Example =: "PARIS")

2. `get_restaurants`: Get get_restaurants for a given location
   - Parameters:
     - `location_id`: Location ID from search_locations

## Code Structure

- `main.py`: The entry point for the server
- `restaurants_mcp_server/`: The core MCP implementation
  - `__init__.py`: Package initialization
  - `restaurants_server.py`: MCP server implementation with tool definitions
"# mcp-gemini-restaurant-agent" 
