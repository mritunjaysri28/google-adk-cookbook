from dotenv import load_dotenv
import google.auth
from google.adk.agents import Agent
from google.adk.tools import AgentTool
import google.cloud.logging
import os

from .callback_logging import log_query_to_model, log_model_response

from .sub_agents.room_planner.agent import room_planner_agent
from .sub_agents.search_agent.agent import search_agent

from .tools import set_session_value

# Load env
load_dotenv()

# Configure logging to the Cloud (with graceful local fallback if ADC is not present)
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)

search_agent_tool = Agent(
    name="search_agent_tool",
    model=os.getenv("MODEL"),
    instruction="Use your search tool to look up facts.",
    sub_agents=[search_agent],
)

root_agent = Agent(
    name="product_selector",
    model=os.getenv("MODEL"),
    instruction="""
    You represent the paint department of Cymbal Shops.

    Information about Cymbal Shops paint, including prices, is available to you
    through the 'search_agent_tool' tool.

    - At the start of a conversation, let the user know you're here to help them
      find the right paint for their project. Ask them if they'd like to learn more
      about the different paint products offered by Cymbal Shops.
    - If they say yes, include information about all paint products including coverage rate and price.
    - If price and coverage rate aren't returned for some products, look them up individually.
    - After they have selected a paint product, store their selection in the session
      dictionary with the key 'SELECTED_PAINT', its coverage rate in 'COVERAGE_RATE',
      and its price per 2.5L container in 'PRICE'.
    - Transfer to the 'room_planner_agent'
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    sub_agents=[room_planner_agent],
    tools=[
        AgentTool(search_agent_tool, skip_summarization=False),
        set_session_value,
    ],
)
