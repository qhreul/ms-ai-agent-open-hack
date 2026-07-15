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

    instructions = """
You are an agent that helps customers order pizzas from Contoso pizza.
You have a Gen-alpha personality, so you are friendly and helpful, but also a bit cheeky.
You can provide information about Contoso Pizza and its retail stores.
You help customers order a pizza of their chosen size, crust, and toppings.
You don't like pineapple on pizzas, but you will help a customer a pizza with pineapple ... with some snark.
Make sure you know the customer's name before placing an order on their behalf.
You can't do anything except help customers order pizzas and give information about Contoso Pizza. You will gently deflect any other questions.
    """

    # Check if the agent already exists, if not create it
    try:
        agent = project.agents.get(agent_name)
        print(f"Agent already exists (id: {agent.id}, name: {agent.name})")
    except ResourceNotFoundError:
        agent = create_agent(project, agent_name, OPENAI_MODEL, instructions)
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
    
    # Get an OpenAI client pre-bound to the specified agent
    openai = project.get_openai_client(agent_name=agent_name)

    # Create a conversation with an initial user message
    conversation = openai.conversations.create(
        items=[
            {
                "type": "message",
                "role": "user",
                "content": "What is your name? I need to know your name before I can help you order a pizza.",
            }
        ],
    )
    print(f"Conversation ID: {conversation.id}")

    response = openai.responses.create(
        conversation=conversation.id,
        input="My name is Quentin. I want to order a pizza with pepperoni on it.",
    )
    print(response.output_text)
