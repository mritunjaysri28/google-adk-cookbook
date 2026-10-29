import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.callback_logging import log_query_to_model, log_model_response

from dotenv import load_dotenv

from google.genai import types
from google.adk import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import ScrapeWebsiteTool

load_dotenv()

root_agent = Agent(
    name="crewai_tool_agent",
    model=os.getenv("MODEL"),
    description="Agent that scrapes and summarizes web content using CrewAI tools.",
    instruction="""
    You are a research assistant capable of scraping and reading website content using CrewAI tools.
    - Use your web scraping tool to retrieve content from the requested website.
    - If the user asks for news, scrape a reliable news source and summarize the top headlines.
    - Provide concise, accurate summaries of the scraped text.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[
        CrewaiTool(
            name="scrape_website",
            description="Scrapes and extracts readable text from any website URL provided in website_url.",
            tool=ScrapeWebsiteTool(),
        )
    ],
)
