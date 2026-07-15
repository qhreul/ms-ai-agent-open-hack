# TODO to be fixed with my personal coding style and formatting
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, FunctionTool, MCPTool, Tool

from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from utils.agentic_ai_util import create_agent

import json
import os
import glob
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
MCP_ENDPOINT = os.getenv("MCP_PIZZA_ENDPOINT")


def upload_knowledge(file_path: str, client, vector_store) -> str:
    """
    @param file_path: path to the files to be uploaded
    @param client: OpenAI client to use for uploading
    @param vector_store: The vector store to upload the files to
    """
    # gather the list of files to upload
    file_path = Path(file_path).resolve()
    markdown_files = list(file_path.glob("*.md"))

    # iterate through the files and upload them to the vector store
    for markdown_file in markdown_files:
        with markdown_file.open("rb") as file_handle:
            vector_store_file = client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_handle,
            )
            print(f"Uploaded: {markdown_file.name}")

def get_pizza_quantity(people: int) -> str:
    """
    Calculate the number of pizzas to order based on the number of people.
    @param people: The number of people to order pizza for.
    @return: A message indicating the number of pizzas to order.
    """
    print(f"[FUNCTION CALL:get_pizza_quantity] Calculating pizza quantity for {people} people.")
    return f"For {people} you need to order {people // 2 + people % 2} pizzas."


if __name__ == "__main__":
    agent_name = "pizza-ordering-agent"

    # Create project and openai clients to call Foundry API
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    # Create the vector store for file search
    vector_store = openai.vector_stores.create(name="ContosoPizzaInfoStore")
    print(f"Vector store created (id: {vector_store.id})")
    # Upload files to the vector store
    upload_knowledge("knowledge_base", openai, vector_store)

    # Create the Function Calling Tool for calculating pizza quantity
    func_tool = FunctionTool(
        name="get_pizza_quantity",
        parameters={
            "type": "object",
            "properties": {
                "people": {
                    "type": "integer",
                    "description": "The number of people to order pizza for",
                },
            },
            "required": ["people"],
            "additionalProperties": False,
        },
        description="Suggest the number of pizzas to order based on the number of guests.",
        strict=True,
    )

    # Create the information retrieval tool for the agent to use
    mcpTool = MCPTool(
        server_label="contoso-pizza-mcp",
        server_url=MCP_ENDPOINT,
        require_approval="never"
    )

    ## Define the toolset for the agent
    toolset: list[Tool] = []
    toolset.append(FileSearchTool(vector_store_ids=[vector_store.id]))
    toolset.append(func_tool)
    toolset.append(mcpTool)

    # Create a Foundry Agent
    agent = create_agent(
        project=project,
        agent_name=agent_name,
        model=OPENAI_MODEL,
        instructions=open("prompts/instructions.txt").read(),
        tools=toolset
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Create a conversation for the agent interaction
    conversation = openai.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Chat with the agent
    while True:
        # Get the user input
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat.")
            break

        # Get the agent response
        response = openai.responses.create(
            conversation=conversation.id,
            input=user_input,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        # Handle function calls in the response
        input_list: ResponseInputParam = []
        for item in response.output:
            if item.type == "function_call":
                if item.name == "get_pizza_quantity":
                    # Execute the function logic for get_pizza_quantity
                    pizza_quantity = get_pizza_quantity(**json.loads(item.arguments))
                    # Provide function call results to the model
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps({"pizza_quantity": pizza_quantity}),
                        )
                    )

        if input_list:
            response = openai.responses.create(
                previous_response_id=response.id,
                input=input_list,
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )    

        # Print the agent response
        print(f"Assistant: {response.output_text}")