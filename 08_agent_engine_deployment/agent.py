import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

load_dotenv()

root_agent = Agent(
    name="transcript_summarization_agent",
    model=os.getenv("MODEL"),
    description="Summarizes chat transcript.",
    instruction="Summarizes the provided chat transcript.",
)
