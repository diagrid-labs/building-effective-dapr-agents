#!/usr/bin/env python3
"""
Prompt Chaining Pattern demonstrates:
1. Agent-based tasks with tools
2. Agent-based tasks without tools
3. Simple prompt-based tasks
4. Chaining tasks sequentially using durable workflow steps
"""

import logging
from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr_agents.agent.patterns.toolcall.base import ToolCallAgent
from dapr_agents.types import DaprWorkflowContext
from dotenv import load_dotenv
from dapr_agents import tool
from pydantic import BaseModel, Field

class SearchAttractionsSchema(BaseModel):
    city: str = Field(description="City to search for attractions")
    type: str = Field(description="Type of attraction (museums, restaurants, etc.)")

@tool(args_model=SearchAttractionsSchema)
def search_attractions(city: str, type: str) -> str:
    """Search for attractions in a city based on type."""
    attractions = {
        "paris": {
            "museums": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou"],
            "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Comptoir du Relais"],
            "historical sites": ["Eiffel Tower", "Notre-Dame Cathedral", "Arc de Triomphe"]
        }
    }

    city = city.lower()
    if city not in attractions:
        return f"No information available for {city}"

    if type.lower() not in attractions[city]:
        return f"No {type} information available for {city}"

    return ", ".join(attractions[city][type.lower()])

# Agent configurations
planning_agent = ToolCallAgent(
    name="TravelPlanner",
    role="Travel Outline Developer",
    goal="Create structured travel outlines based on destination information",
    instructions=["Create day-by-day structure for trips",
                  "Use tools to search for key attractions based on user preferences"],
    tools=[search_attractions]
)

itinerary_agent = ToolCallAgent(
    name="ItineraryCreator",
    role="Detailed Itinerary Developer",
    goal="Expand travel outlines into comprehensive itineraries",
    instructions=["Add specific timing and logistics details",
                  "Include dining recommendations and local tips"]
)

@workflow(name='travel_planning_workflow')
def travel_planning_workflow(ctx: DaprWorkflowContext, user_input: str):
    # Step 1: Extract destination using a simple prompt (no agent)
    destination_text = yield ctx.call_activity(extract_destination, input=user_input)
    print(f"\n--- Step 1 Output (Extract Destination) ---")
    print(f"{destination_text[:300]}...")

    # Gate: Check if destination is valid
    print(f"\n--- Gate: Validating Destination ---")
    if "paris" not in destination_text.lower():
        return "Unable to create itinerary: Destination not recognized or supported."
    print(f"Destination valid! Proceeding to outline generation.")

    # Step 2: Generate outline with planning agent (has tools)
    travel_outline = yield ctx.call_activity(create_travel_outline, input=destination_text)
    print(f"\n--- Step 2 Output (Create Travel Outline) ---")
    print(f"{travel_outline[:300]}...")

    # Step 3: Expand into detailed plan with itinerary agent (no tools)
    detailed_itinerary = yield ctx.call_activity(expand_itinerary, input=travel_outline)
    print(f"\n--- Step 3 Output (Expand to Detailed Itinerary) ---")
    print(f"Detailed itinerary generated. Length: {len(detailed_itinerary)} characters")

    return detailed_itinerary

# Simple prompt task (no agent)
@task(description="""
    Extract the main destination, trip duration, and user preferences from: {user_input}
    
    Include information about:
    - Main destination city/location
    - Number of days for the trip
    - Specific interests (museums, food, activities)
    
    Format your response as a structured summary.
    """)
def extract_destination(user_input: str) -> str:
    pass  # Implementation handled by the prompt

# Task with an Agent and tools
@task(agent=planning_agent,
      description="""
      Create a day-by-day travel outline for a trip based on this information: {destination_text}
      
      1. First, identify the city and duration from the input
      2. Use the search_attractions tool to find relevant attractions
      3. Create a balanced itinerary that includes variety each day
      
      Provide a comprehensive travel outline with a day-by-day structure.
      """)
def create_travel_outline(destination_text: str) -> str:
    pass  # Implementation handled by the agent

# Agent task WITHOUT tools
@task(agent=itinerary_agent,
      description="""
      This is a two-step task:
      1. First, add specific timing, transportation details, and logistics to this travel outline: {outline}
      2. Then, enhance this schedule with local tips, dining recommendations, and cultural insights.
      
      Provide a detailed, comprehensive itinerary with both logistics and local recommendations.
      """)
def expand_itinerary(outline: str) -> str:
    pass  # Implementation handled by the agent

def main():
    wfapp = WorkflowApp()
    user_input = "I want to visit Paris for 3 days. I love art museums, historical sites, and trying local food."

    print("\n=== Prompt Chaining Pattern Demonstration ===")
    print(f"\nUser request: \"{user_input}\"")
    print("\nStarting workflow chain:")

    # Run the workflow
    results = wfapp.run_and_monitor_workflow(
        travel_planning_workflow,
        input=user_input
    )

    print("\n=== Final Detailed Itinerary ===")
    print("============================================")
    print(results)
    print("============================================")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    main()