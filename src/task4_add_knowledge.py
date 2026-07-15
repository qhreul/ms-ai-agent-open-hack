# https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search?view=foundry&pivots=python&tabs=prompt-agents

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential

from utils.agentic_ai_util import create_agent

from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

KNOWLEDGE_FILE_PATH = Path("knowledge_base").resolve()

if __name__ == "__main__":
    agent_name = "pizza-ordering-agent-with-knowledge"
    
    # Create project and openai clients to call Foundry API
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    # Create vector store and upload files
    vector_store = openai.vector_stores.create(name="PizzaInfoStore")
    
    # Upload all markdown files from the knowledge_base directory
    markdown_files = list(KNOWLEDGE_FILE_PATH.glob("*.md"))
    for markdown_file in markdown_files:
        with markdown_file.open("rb") as file_handle:
            vector_store_file = openai.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_handle,
            )
            print(f"Uploaded: {markdown_file.name}")

    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=OPENAI_MODEL,
            instructions=(
                "You are a helpful agent that can search through product information. "
                "Use file search to answer questions from the uploaded files."
            ),
            tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
        ),
        description="File search agent for product information queries.",
    )
    
    # Create conversation and generate response
    conversation = openai.conversations.create()

    response = openai.responses.create(
        conversation=conversation.id,
        input="Tell me about Contoso products",
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(response.output_text)

    # Clean up resources
    project.agents.delete_version(
        agent_name=agent.name,
        agent_version=agent.version,
    )
    openai.vector_stores.delete(vector_store.id)
