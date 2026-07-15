from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, Tool, FunctionTool
from azure.identity import DefaultAzureCredential

from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from dotenv import load_dotenv
import json
from pathlib import Path
import os

load_dotenv()
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")


def suggest_pizza_order(num_guests: int) -> int:
    """
    Suggest the number of pizzas to order based on the number of guests.
    @param num_guests: number of guests attending the event
    @return: number of pizzas to order
    """
    # Assume each pizza serves 3 people
    pizzas_needed = (num_guests + 2) // 3  # Round up to the nearest whole number
    return pizzas_needed


if __name__ == "__main__":
    agent_name = "pizza-ordering-agent-with-function-calling"

    # Create project and openai clients to call Foundry API
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    # Create a conversation for multi-turn interaction
    conversation = openai.conversations.create()

    # Define a function tool for the model to use
    func_tool = FunctionTool(
        name="suggest_pizza_order",
        parameters={
            "type": "object",
            "properties": {
                "num_guests": {
                    "type": "integer",
                    "description": "The number of guests attending the event.",
                },
            },
            "required": ["num_guests"],
            "additionalProperties": False,
        },
        description="Suggest the number of pizzas to order based on the number of guests.",
        strict=True,
    )
    tools: list[Tool] = [func_tool]

    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=OPENAI_MODEL,
            instructions="You are a helpful assistant that can use function tools.",
            tools=tools,
        ),
    )

    # Prompt the model with tools defined
    response = openai.responses.create(
        input="We are having a party with 10 guests. How many pizzas should we order?",
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    input_list: ResponseInputParam = []
    # Process function calls
    for item in response.output:
        if item.type == "function_call":
            if item.name == "suggest_pizza_order":
                # Execute the function logic for suggest_pizza_order
                pizzas = suggest_pizza_order(**json.loads(item.arguments))

                # Provide function call results to the model
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"pizzas": pizzas}),
                    )
                )

    # Submit function results and get the final response
    response = openai.responses.create(
        input=input_list,
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Agent response: {response.output_text}")

    # Clean up resources
    project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    openai.conversations.delete(conversation_id=conversation.id)