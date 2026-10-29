import os
import sys
import logging

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types
from typing import Optional, List, Dict

from google.adk.tools.tool_context import ToolContext

load_dotenv()


# Tools (add the tool here when instructed)
def save_attractions_to_state(tool_context: ToolContext, attraction: List[str]) -> dict[str, str]:
    """Save the attractions to the state["attractions"]

    Args:
        attractions [str]: a list of string to add to the attractions

    Return:
        None
    """

    # Load the existing attractions from state, If none exists, state an empty list
    existing_attractions = tool_context.state.get("attractions", [])

    # Update the attractions with key combo of old and new list
    # When tool is run ADK will create an event make the corresponding update in the session state
    tool_context.state["attractions"] = existing_attractions + attraction

    return { "state": "Success" }


# Agents

attractions_planner = Agent(
    name="attractions_planner",
    model=os.getenv("MODEL"),
    description="Build a list of attractions to visit in a country.",
    instruction="""
        - Provide the user options for attractions to visit within their selected country.
        - When they reply, use your tool to save thier selected attraction and then provide more attractions.
        - if they ask to view the list. provide a list of { attractions? } and then suggest more.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # When instructed to do so, paste the tools parameter below this line
    tools=[save_attractions_to_state]
    )

travel_brainstormer = Agent(
    name="travel_brainstormer",
    model=os.getenv("MODEL"),
    description="Help a user decide what country to visit.",
    instruction="""
        Provide a few suggestions of popular countries for travelers.

        Help a user identify their primary goals of travel:
        adventure, leisure, learning, shopping, or viewing art

        Identify countries that would make great destinations
        based on their priorities.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

root_agent = Agent(
    name="steering",
    model=os.getenv("MODEL"),
    description="Start a user on a travel adventure.",
    instruction="""
        Ask the user if they know where they'd like to travel
        or if they need some help deciding.
        If they need help deciding, send them to 'travel_brainstormer'.
        If they know what country they'd like to visit,
        send them to the 'attractions_planner'.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    # Add the sub_agents parameter when instructed below this line
    sub_agents=[travel_brainstormer, attractions_planner]
)
