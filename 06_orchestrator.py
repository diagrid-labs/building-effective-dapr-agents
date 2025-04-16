#!/usr/bin/env python3
"""
Orchestrator-Workers Pattern demonstrates:
1. How a central orchestrator dynamically determines subtasks.
2. Delegates dynamic tasks to worker LLMs.
3. Synthesizes results back into a single result.
"""

import logging
from typing import List, Dict, Any

from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr_agents.types import DaprWorkflowContext
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Define models for orchestration
class TravelTask(BaseModel):
    """A task to be performed by a worker LLM."""
    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., description="Detailed description of what the task should accomplish")
    query: str = Field(..., description="The specific query or prompt for the worker LLM")

class OrchestratorPlan(BaseModel):
    """The plan created by the orchestrator."""
    tasks: List[TravelTask] = Field(..., description="List of tasks to be performed by worker LLMs")

# Define Workflow logic
@workflow(name="orchestrator_travel_planner")
def orchestrator_travel_planner(ctx: DaprWorkflowContext, input_params: dict):
    """Defines a Dapr workflow that uses an orchestrator to plan and delegate travel planning tasks."""

    # Extract the travel request
    travel_request = input_params.get("request")
    logging.info(f"Received complex travel request: {travel_request}")

    # Step 1: Orchestrator analyzes the request and determines required tasks
    logging.info("Orchestrator analyzing request and determining subtasks...")
    plan_result = yield ctx.call_activity(
        create_travel_plan,
        input={"request": travel_request}
    )

    tasks = plan_result.get("tasks", [])
    logging.info(f"Orchestrator created {len(tasks)} tasks")

    # Step 2: Execute each task with a worker LLM
    worker_results = []
    for task in tasks:
        logging.info(f"Executing task: {task['task_id']} - {task['description']}")
        task_result = yield ctx.call_activity(
            execute_travel_task,
            input={"task": task}
        )
        worker_results.append({
            "task_id": task["task_id"],
            "result": task_result
        })

    # Step 3: Synthesize the results into a cohesive travel plan
    logging.info("Synthesizing results into a final travel plan...")
    final_plan = yield ctx.call_activity(
        synthesize_travel_plan,
        input={
            "request": travel_request,
            "results": worker_results
        }
    )

    logging.info("Final travel plan created successfully")
    return final_plan

@task(description="Analyze this travel request and create a list of specific tasks needed to create a comprehensive travel plan. For each task, provide a task_id, description, and specific query: {request}")
def create_travel_plan(request: str) -> OrchestratorPlan:
    """Orchestrator LLM that analyzes the request and creates a plan of tasks."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Execute this specific travel planning task: {task}")
def execute_travel_task(task: Dict[str, Any]) -> str:
    """Worker LLM that executes a specific task in the travel planning process."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Synthesize these worker results into a cohesive, well-formatted travel plan that addresses the original request: {request}. Worker results: {results}")
def synthesize_travel_plan(request: str, results: List[Dict[str, Any]]) -> str:
    """Synthesizer LLM that combines all worker results into a cohesive travel plan."""
    # This will be implemented as an LLM call by the framework
    pass

def main():
    wfapp = WorkflowApp()

    # Example complex travel request
    complex_request = """
    I'm planning a 5-day family trip to Japan in October with my spouse and two children (ages 8 and 12). 
    We're interested in experiencing both traditional and modern Japanese culture, family-friendly activities, 
    and want a mix of Tokyo city experiences and at least 2 days in a more natural setting like Hakone or Nikko. 
    Our budget is moderate, and we prefer public transportation. We'd like recommendations for accommodations, 
    must-see attractions, transportation logistics, and a day-by-day itinerary.
    """

    logging.info("=== ORCHESTRATOR-WORKERS PATTERN DEMONSTRATION ===")
    logging.info("This example shows how an orchestrator dynamically plans and delegates tasks to worker LLMs")

    print("\nComplex travel request:")
    print(complex_request)

    print("\nStarting orchestrator workflow...")
    result = wfapp.run_and_monitor_workflow(
        orchestrator_travel_planner,
        input={"request": complex_request}
    )

    if result:
        print("\nFinal Travel Plan:")
        print(f"{result}")

    print("\nOrchestrator-Workers Pattern completed successfully!")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    main()