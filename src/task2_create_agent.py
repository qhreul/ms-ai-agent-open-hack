from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


from utils.agentic_ai_util import create_agent

import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")


if __name__ == "__main__":
    agent_name = "pizza-ordering-agent"
    
    # Create project and openai clients to call Foundry API
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    # Check if the agent already exists, if not create it
    try:
        agent = project.agents.get(agent_name)
        print(f"Agent already exists (id: {agent.id}, name: {agent.name})")
    except ResourceNotFoundError:
        agent = create_agent(project, agent_name, OPENAI_MODEL, "You are a pizza ordering agent. You will help the user order a pizza.") 
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
    
    # Get an OpenAI client pre-bound to the specified agent
    openai = project.get_openai_client(agent_name=agent_name)

    # Create a conversation for multi-turn chat
    conversation = openai.conversations.create()

    # Chat with the agent to answer questions
    response = openai.responses.create(
        conversation=conversation.id,
        input="What is the size of France in square miles?",
    )
    print(response.output_text)

    # Ask a follow-up question in the same conversation
    response = openai.responses.create(
        conversation=conversation.id,
        input="And what is the capital city?",
    )
    print(response.output_text)