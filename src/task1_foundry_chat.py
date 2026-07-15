from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

import os
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "gpt-5.4-mini"
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")


if __name__ == "__main__":
    client = OpenAI(
        base_url=endpoint,
        api_key=token_provider
    )

    response = client.responses.create(
        model=deployment_name,
        input="Hello do you like pizza?",
    )

    print(f"answer: {response.output[0]}")
