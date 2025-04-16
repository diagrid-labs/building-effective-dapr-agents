#!/usr/bin/env python3
"""
Autonomous Agent Pattern demonstrates:
1. How to use ReAct agent that is able to perform reason and action cycles.
"""

import asyncio
import logging
from dapr_agents import tool, ReActAgent
from dotenv import load_dotenv

@tool
def search_weather(city: str) -> str:
    """Get weather information for a city."""
    weather_data = {
        "london": "rainy, 12°C",
        "paris": "sunny, 18°C",
        "tokyo": "cloudy, 16°C"
    }
    return weather_data.get(city.lower(), "Weather data not available")

@tool
def find_activities(city: str) -> str:
    """Find popular activities for a city."""
    activities = {
        "london": "Visit British Museum, See Big Ben, Ride the London Eye",
        "paris": "Visit Eiffel Tower, Explore Louvre Museum, Walk along Seine River",
        "tokyo": "Visit Tokyo Skytree, Explore Senso-ji Temple, Shop in Shibuya"
    }
    return activities.get(city.lower(), "Activity data not available")

async def main():
    # Create the ReAct agent with both tools
    travel_agent = ReActAgent(
        name="TravelHelper",
        role="Travel Assistant",
        instructions=["Help users plan trips by providing weather and activities"],
        tools=[search_weather, find_activities]
    )

    print("=== AUTONOMOUS AGENT EXAMPLE ===")
    print("The agent will decide what information to get first.\n")

    # Example query that requires both tools
    result = await travel_agent.run("I'm planning a trip to Paris. What should I know?")
    print(f"Result: {result}")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())