import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.callback_logging import log_query_to_model, log_model_response

from google.adk import Agent
from google.adk.tools.langchain_tool import LangchainTool # import
from google.adk.agents.callback_context import CallbackContext

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv

load_dotenv()

root_agent = Agent(
    name="lanchgain_tool_agent",
    model=os.getenv("MODEL"),
    description="Answers questions using Wikipedia.",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    instruction="""Research the topic suggested by the user.
    Share the information you have found with the user.""",
    # Add the LangChain Wikipedia tool below
    tools=  [
        LangchainTool(
            tool=WikipediaQueryRun(
              api_wrapper=WikipediaAPIWrapper()
            )
        )
    ]
)