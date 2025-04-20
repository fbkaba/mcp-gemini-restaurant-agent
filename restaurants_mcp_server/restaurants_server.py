import json
import httpx
import logging
import signal
import sys
import argparse
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("restaurants-mcp-server")

# Initialize FastMCP server
mcp = FastMCP("restaurants")

# Constants
KEY = os.getenv("KEY")
HOST = os.getenv("HOST", "booking-com15.p.rapidapi.com")

# Validate required environment variables
if not KEY:
    logger.error("KEY environment variable is not set. Please create a .env file with your API key.")
    sys.exit(1)

async def call_rapidapi_request(endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Make a request to the RapidAPI with proper error handling."""
    url = f"https://{HOST}{endpoint}"
    
    headers = {
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": HOST
    }
    
    logger.info(f"Calling API request to {endpoint} with params: {params}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            logger.info(f"API request to {endpoint} successful")
            return response.json()
        except Exception as e:
            logger.error(f"API request to {endpoint} failed: {str(e)}")
            return {"error": str(e)}

@mcp.tool()
async def search_locations(query: str) -> str:
    """Search for restaurant locations by name.
    
    Args:
        query: The location to search for example: "Paris", Las Vegas"
    """
    logger.info(f"Searching for locations with query: {query}")
    endpoint = "/api/v1/restaurant/searchLocation"
    params = {"query": query}
    
    result = await call_rapidapi_request(endpoint, params)
    
    if "error" in result:
        logger.error(f"Error in search_locations: {result['error']}")
        return f"Error fetching locations: {result['error']}"
    
    # results
    results = []
    
    if "data" in result and isinstance(result["data"], list):
        locations_count = len(result["data"])
        logger.info(f"Found {locations_count} locations for query: {query}")
        for location in result["data"]:
            location_info = (
                f"Name: {location.get('localizedName', 'Unknown')}\n"
                f"Location Id: {location.get('locationId', 'Unknown')}\n"
                f"Coordinates: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n"
                f"PlaceType: {location.get('placeType', 'Unknown')}\n"
            )
            results.append(location_info)
        
        return "\n---\n".join(results) if results else "No locations found matching your query."
    else:
        logger.warning(f"Unexpected response format from API for query: {query}")
        return "Unexpected response format from the API."

@mcp.tool()
async def get_restaurants(location_id: str) -> str:
    """Get restaurants for a specific location.
    Args:
        location_id: The location ID from the call search_location
    """
    logger.info(f"Getting restaurants for location_id: {location_id}")
    endpoint = "/api/v1/restaurant/searchRestaurants"
    params = {
        "locationId": location_id,

    }

    result = await call_rapidapi_request(endpoint, params)
    
    if "error" in result:
        logger.error(f"Error in get_restaurants: {result['error']}")
        return f"Error fetching restaurants: {result['error']}"
    
    # Format the response
    results = []
    
    if "data" in result and "data" in result["data"] and isinstance(result["data"]["data"], list):
        restaurants_count = len(result["data"]["data"])
        logger.info(f"Found {restaurants_count} restaurants for location: {location_id}")
        restaurants = result["data"]["data"]
        for restaurant in restaurants[:10]:  # Let set the limit to 10 restaurants
            restaurant_info = (
                f"Name: {restaurant.get('name', 'Unknown')}\n"
                f"Average Rating: {restaurant.get('averageRating', 'Unknown')}\n"
                f"User Review Count: {restaurant.get('userReviewCount', 'Unknown')}\n"
                f"Menu Url: {restaurant.get('menuUrl', 'Unknown')}\n"
                f"City Name GeoName: {restaurant.get('parentGeoName', 'Unknown')}\n"
                #f"Award Info: {restaurant.get('year', 'N/A')}, {restaurant.get('awardType', 'N/A')}\n"
                #f"Has Menu: {restaurant.get('hasMenu', 'Unknown')}\n"
                f"Status: {restaurant.get('currentOpenStatusCategory', 'Unknown')}\n"
                f"Premium: {restaurant.get('isPremium', 'Unknown')}\n"
                #f"priceTag: {restaurant.get('priceTag', 'Unknown')}\n"
                )
            # Add room information
            restaurant_info += f"Room: {restaurant_info}\n"
            results.append(restaurant_info)
        
        return "\n---\n".join(results) if results else "No Restaurants found for this location and dates."
    else:
        logger.warning(f"Unexpected response format from API for location: {location_id}")
        return "Unexpected response format from the API."

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the Restaurants MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Restaurants MCP Server')
    args = parser.parse_args()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        # Use STDIO transport - it's the most reliable for Claude for Desktop
        logger.info("Starting Restaurants MCP Server with stdio transport...")
        mcp.run(transport='stdio')
        return 0
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        return 1
    finally:
        logger.info("Restaurants MCP Server shutting down...")

if __name__ == "__main__":
    sys.exit(main()) 