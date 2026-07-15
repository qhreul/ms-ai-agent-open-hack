from azure.ai.projects.models import PromptAgentDefinition

def create_agent(project, agent_name: str, model: str, instructions: str):
    """
    Create an agent with a model and instructions
    @param project: AIProjectClient instance
    @param agent_name: name of the agent to create
    @param model: the model to use for the agent
    @param instructions: the instructions for the agent
    @return: created agent instance
    """
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions=instructions,
        ),
    )

    return agent