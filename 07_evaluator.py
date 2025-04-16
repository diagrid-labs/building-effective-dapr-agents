#!/usr/bin/env python3
"""
Evaluator-Optimizer Pattern demonstrates:
1. How to use an LLM to generate output
2. How to use another LLM to provide evaluation and feedback in a loop
3. Control execution until quality criteria are met or maximum iterations reached
"""

import logging
from typing import List
import json

from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr_agents.types import DaprWorkflowContext
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Define models for the evaluation process
class Evaluation(BaseModel):
    """Evaluation of a travel plan with feedback for improvement."""
    score: int = Field(..., description="Quality score from 1-10")
    feedback: List[str] = Field(..., description="Specific feedback points for improvement")
    meets_criteria: bool = Field(..., description="Whether the plan meets all criteria")

# Define Workflow logic
@workflow(name="evaluator_optimizer_travel_planner")
def evaluator_optimizer_travel_planner(ctx: DaprWorkflowContext, input_params: dict):
    """Simple Dapr workflow for a travel plan using evaluator-optimizer pattern."""

    # Extract parameters
    travel_request = input_params.get("request")
    max_iterations = input_params.get("max_iterations", 2)
    
    print("Starting travel planner with Evaluator-Optimizer pattern")

    # Generate initial travel plan
    print("Generating initial travel plan...")
    current_plan = yield ctx.call_activity(
        generate_travel_plan,
        input={"request": travel_request, "feedback": None}
    )

    # Evaluation loop - simplified to just two iterations
    iteration = 1
    meets_criteria = False

    while iteration <= max_iterations and not meets_criteria:
        print(f"Evaluating travel plan (iteration {iteration})...")

        # Evaluate the current plan
        evaluation = yield ctx.call_activity(
            evaluate_travel_plan,
            input={"request": travel_request, "plan": current_plan}
        )

        score = evaluation.get("score", 0)
        feedback = evaluation.get("feedback", [])
        meets_criteria = evaluation.get("meets_criteria", False)

        print(f"Score: {score}/10, Meets criteria: {meets_criteria}")
        if feedback:
            print(f"Feedback: {', '.join(feedback)}")
        
        # Stop if we meet criteria or reached max iterations
        if meets_criteria or iteration >= max_iterations:
            break

        # Optimize the plan based on feedback
        print(f"Optimizing plan based on feedback...")
        current_plan = yield ctx.call_activity(
            generate_travel_plan,
            input={"request": travel_request, "feedback": feedback}
        )

        iteration += 1

    return {
        "final_plan": current_plan,
        "iterations": iteration,
        "final_score": score
    }

@task(description="Create a travel plan for: {request}. If provided, incorporate this feedback: {feedback}")
def generate_travel_plan(request: str, feedback: List[str] = None) -> str:
    """Generates or optimizes a travel plan based on the request and feedback."""
    # This will be implemented as an LLM call by the framework
    pass

@task(description="Evaluate this travel plan. Provide a score (1-10), feedback for improvement, and whether it meets criteria. Request: {request} | Plan: {plan}")
def evaluate_travel_plan(request: str, plan: str) -> Evaluation:
    """Evaluates a travel plan and provides feedback for improvement."""
    # This will be implemented as an LLM call by the framework
    pass

def main():
    wfapp = WorkflowApp()

    # Example travel request - simplified
    travel_request = """
    I want a weekend trip to San Francisco. I like museums, good food, 
    and walking tours. My budget is moderate.
    """

    print("=== EVALUATOR-OPTIMIZER PATTERN DEMO ===")
    print("Travel request:")
    print(travel_request)

    workflow_params = {
        "request": travel_request,
        "max_iterations": 2
    }

    result = wfapp.run_and_monitor_workflow(
        evaluator_optimizer_travel_planner,
        input=workflow_params
    )

    if result:
        # Convert string result to dictionary if needed
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except:
                final_plan = result
                print("\nFinal travel plan:")
                print(f"\n{final_plan}")
                print("\nEvaluator-Optimizer Pattern completed!")
                return
                
        # Handle dictionary result
        final_plan = result.get("final_plan", "")
        iterations = result.get("iterations", 0)
        final_score = result.get("final_score", 0)
        
        print(f"\nFinal travel plan after {iterations} iterations (score: {final_score}/10):")
        print(f"\n{final_plan}")

    print("\nEvaluator-Optimizer Pattern completed!")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    main()