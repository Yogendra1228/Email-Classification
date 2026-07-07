import json
import os
import logging

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

logging.basicConfig(level=logging.ERROR)

logging.getLogger("azure").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("azure.identity").setLevel(logging.ERROR)
logging.getLogger("azure.core").setLevel(logging.ERROR)

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
    allow_preview=True,
)

openai_client = project_client.get_openai_client()


def run_orchestrator(message: str) -> dict:
    """Runs the Orchestrator Agent to determine Query or Complaint."""

    agent = project_client.agents.get(
        agent_name=os.getenv("ORCHESTRATOR_AGENT")
    )

    conversation = openai_client.conversations.create(
        items=[
            {
                "type": "message",
                "role": "user",
                "content": message,
            }
        ]
    )

    try:
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "type": "agent_reference",
                    "name": agent.name,
                }
            },
        )

        return json.loads(response.output_text)

    finally:
        openai_client.conversations.delete(
            conversation_id=conversation.id
        )


def run_query(message: str) -> dict:
    """Runs the Query Agent."""

    agent = project_client.agents.get(
        agent_name=os.getenv("QUERY_AGENT")
    )

    conversation = openai_client.conversations.create(
        items=[
            {
                "type": "message",
                "role": "user",
                "content": message,
            }
        ]
    )

    try:
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "type": "agent_reference",
                    "name": agent.name,
                }
            },
        )

        return json.loads(response.output_text)

    finally:
        openai_client.conversations.delete(
            conversation_id=conversation.id
        )

def run_complaint(message: str) -> dict:
    """Runs the Complaint Agent."""

    agent = project_client.agents.get(
        agent_name=os.getenv("COMPLAINT_AGENT")
    )

    conversation = openai_client.conversations.create(
        items=[
            {
                "type": "message",
                "role": "user",
                "content": message,
            }
        ]
    )

    try:
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "type": "agent_reference",
                    "name": agent.name,
                }
            },
        )

        return json.loads(response.output_text)

    finally:
        openai_client.conversations.delete(
            conversation_id=conversation.id
        )



def main(message: str) -> dict:
    """
    Main entry point called from Azure Function.
    """

    logging.info("Running Orchestrator Agent...")

    orchestrator_result = run_orchestrator(message)

    message_type = orchestrator_result.get("type", "").strip().lower()

    if message_type == "query":
        logging.info("Routing to Query Agent...")
        return run_query(message)

    elif message_type == "complaint":
        logging.info("Routing to Complaint Agent...")
        return run_complaint(message)

    else:
        raise ValueError(
            f"Unknown message type returned by Orchestrator: {message_type}"
        )


if __name__ == "__main__":

    user_message = input("Enter message: ")

    result = main(user_message)

    print(json.dumps(result, indent=4))