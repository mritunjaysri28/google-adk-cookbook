import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools import AgentTool

from .tools import get_date, search_local_documents

# Add the VertexAiSearchTool import below
# from google.adk.tools import VertexAiSearchTool


load_dotenv()

# Create your vertexai_search_tool and update its path below
# vertexai_search_tool = VertexAiSearchTool(
#     search_engine_id="projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/engines/YOUR_SEARCH_APP_ID"
# )

search_in_local_documents = Agent(
    name="search_in_local_documents",
    model=os.getenv("MODEL"),
    instruction="Use your search tool to look up facts.",
    tools=[search_local_documents]
)

root_agent = Agent(
    # A unique name for the agent.
    name="root_agent",
    # The Large Language Model (LLM) that agent will use.
    model=os.getenv("MODEL"),
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Answer questions using your data store access.",
    # Instructions to set the agent's behavior.
    instruction="You analyze new planet discoveries and engage with the scientific community on them.",
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the tools instructed below
     tools=[
        AgentTool(search_in_local_documents, skip_summarization=False),
        get_date
    ]
)
