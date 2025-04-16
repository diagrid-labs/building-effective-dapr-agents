#!/usr/bin/env python3
"""
Parallelization Pattern demonstrates:
1. How to run parallel tasks with LLM calls
2. How to wait for all tasks to complete
3. How to merge the results into a single result
"""

import logging
from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr_agents.types import DaprWorkflowContext
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Define models for the travel plan components
class TravelComponent(BaseModel):
    """Base model for travel plan components."""
    title: str = Field(..., description="Title of this travel plan component")
    details: str = Field(..., description="Detailed information about this component")

class TravelPlan(BaseModel):
    """Represents a complete travel plan."""
    destination: str = Field(..., description="The travel destination")
    attractions: TravelComponent = Field(..., description="Tourist attractions information")
    accommodations: TravelComponent = Field(..., description="Accommodation options")
    transportation: TravelComponent = Field(..., description="Transportation details")
    summary: str = Field(..., description="A summary of the travel plan")

# Define Workflow logic
@workflow(name="travel_planning_workflow")
def travel_planning_workflow(ctx: DaprWorkflowContext, input_params: dict):
    """Defines a Dapr workflow for creating a travel plan with parallel components."""

    # Extract parameters from input_params
    destination = input_params.get("destination")
    days = input_params.get("days")
    preferences = input_params.get("preferences")

    logging.info(f"\n=== WORKFLOW START: TRAVEL PLANNING FOR {destination.upper()} ===")

    # Process three aspects of the travel plan in parallel
    parallel_tasks = [
        ctx.call_activity(research_attractions, input={"destination": destination, "preferences": preferences, "days": days}),
        ctx.call_activity(recommend_accommodations, input={"destination": destination, "preferences": preferences, "days": days}),
        ctx.call_activity(suggest_transportation, input={"destination": destination, "preferences": preferences, "days": days})
    ]

    # Wait for all parallel tasks to complete
    logging.info("Waiting for all parallel tasks to complete...")
    results = yield wfapp.when_all(parallel_tasks)
    logging.info("All parallel tasks completed!")

    # Extract the results
    attractions, accommodations, transportation = results

    logging.info("\n=== PARALLEL PROCESSING RESULTS ===")
    logging.info(f"Attractions preview: {str(attractions)[:100]}...")
    logging.info(f"Accommodations preview: {str(accommodations)[:100]}...")
    logging.info(f"Transportation preview: {str(transportation)[:100]}...")

    # Create the final travel plan by combining the results
    final_plan = yield ctx.call_activity(create_travel_plan,
        input={
            "destination": destination,
            "attractions": attractions,
            "accommodations": accommodations,
            "transportation": transportation,
            "days": days
        }
    )

    logging.info("\n=== WORKFLOW COMPLETED SUCCESSFULLY ===")
    return final_plan

@task(description="Research popular attractions and activities in {destination} for {days} days, considering these preferences: {preferences}")
def research_attractions(destination: str, preferences: str, days: int) -> TravelComponent:
    """Researches tourist attractions and activities for the destination."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Recommend accommodations in {destination} for {days} days, considering these preferences: {preferences}")
def recommend_accommodations(destination: str, preferences: str, days: int) -> TravelComponent:
    """Recommends suitable accommodations for the destination."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Suggest transportation options in and to {destination} for {days} days, considering these preferences: {preferences}")
def suggest_transportation(destination: str, preferences: str, days: int) -> TravelComponent:
    """Suggests transportation options for the destination."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Create a comprehensive travel plan for {destination} for {days} days based on the researched attractions, accommodations, and transportation")
def create_travel_plan(destination: str, attractions: TravelComponent, accommodations: TravelComponent, transportation: TravelComponent, days: int) -> str:
    """Creates a final travel plan by combining all the components."""
    # This will be implemented as an LLM call by the framework
    pass

def main():
    wfapp = WorkflowApp()

    destination = "Paris"
    days = 3
    preferences = "I love art museums, historical sites, and trying local food. I prefer budget-friendly options and walking when possible."

    print(f"\n=== PARALLELIZATION PATTERN DEMONSTRATION ===")
    print(f"Planning a {days}-day trip to {destination}")
    print(f"User preferences: {preferences}")
    print("\nWorkflow steps:")
    print("1. Three PARALLEL LLM calls (attractions, accommodations, transportation)")
    print("2. One final LLM call to combine results into a comprehensive plan")

    results = wfapp.run_and_monitor_workflow(
        travel_planning_workflow,
        input={"destination": destination, "days": days, "preferences": preferences}
    )

    if results:
        print("\n=== COMPLETE TRAVEL PLAN ===")
        preview_length = min(500, len(results))
        print(f"\nPreview:\n{results[:preview_length]}...\n")
        print("Parallelization Pattern completed successfully!")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    main()