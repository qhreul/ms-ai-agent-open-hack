from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool

from openai.types.responses.response_input_param import ResponseInputParam

from dotenv import load_dotenv
import json
import os

load_dotenv()
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
MCP_ENDPOINT = os.getenv("MCP_PIZZA_ENDPOINT")

if __name__ == "__main__":
    agent_name = "pizza-ordering-agent-with-mcp-integration"

    # Create project and openai clients to call Foundry API
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    # Create an MCP connection to the pizza ordering service
    toolset : list[Tool] = []
    mcpTool = MCPTool(
        server_label="contoso-pizza-mcp",
        server_url=MCP_ENDPOINT,
        require_approval="never"
    )
    toolset.append(mcpTool)

    # Create a prompt agent with MCP tool capabilities
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=OPENAI_MODEL,
            instructions="",
            tools=toolset,
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    ## Create a conversation for the agent interaction
    conversation = openai.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    ## Chat with the agent

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
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )

        # Print the agent response
        print(f"Assistant: {response.output_text}")

    # Clean up resources by deleting the agent version
    project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")