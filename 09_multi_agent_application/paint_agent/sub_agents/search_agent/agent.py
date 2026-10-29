import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import AgentTool

load_dotenv()

CYMBAL_PAINT_CATALOG = """
Cymbal Shops Paint Products Catalog:
1. Project Paint:
   - Price: 30,00 € per 2.5L container
   - Coverage rate: 10 square meters per liter (25 sq meters per 2.5L container)
   - Finishes: Matte, Eggshell, Satin, Semi-Gloss
   - Primary Focus: All-purpose, budget-friendly paint for DIY and light professional projects. Often requires 2 coats.

2. SureCoverage:
   - Price: 33,00 € per 2.5L container
   - Coverage rate: 9 square meters per liter (22.5 sq meters per 2.5L container)
   - Finishes: Matte, Eggshell, Satin, Semi-Gloss, Gloss
   - Primary Focus: Superior hiding power and one-coat coverage for dark colors or challenging surfaces.

3. EcoGreens:
   - Price: 35,00 € per 2.5L container
   - Coverage rate: 10 square meters per liter (25 sq meters per 2.5L container)
   - Finishes: Matte, Eggshell, Satin
   - Primary Focus: Environmentally friendly, low-VOC paint with natural pigments and plant-based binders.

4. Forever Paint:
   - Price: 40,00 € per 2.5L container
   - Coverage rate: 8 square meters per liter (20 sq meters per 2.5L container)
   - Finishes: Eggshell, Satin, Semi-Gloss, Gloss
   - Primary Focus: Premium ultra-durable paint engineered for maximum longevity and stain washability.
"""


def lookup_cymbal_paint_catalog(query: str = "") -> dict:
    """Retrieves product specifications, pricing, and coverage rates for Cymbal Shops paints.

    Args:
        query: Optional search keyword or paint product name (e.g. 'Project Paint', 'SureCoverage', 'prices', 'coverage').

    Returns:
        dict: Catalog details containing pricing and coverage rate per product.
    """
    return {"catalog": CYMBAL_PAINT_CATALOG}


# Determine search tool: VertexAiSearchTool if on Cloud, else local catalog lookup
use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper() == "TRUE"
search_tools = []

if use_vertexai and os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("SEARCH_ENGINE_ID"):
    try:
        from google.adk.tools import VertexAiSearchTool

        search_engine_path = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/engines/{os.getenv('SEARCH_ENGINE_ID')}"
        paint_search_tool = VertexAiSearchTool(search_engine_id=search_engine_path)
        search_tools = [paint_search_tool]
    except Exception:
        search_tools = [lookup_cymbal_paint_catalog]
else:
    search_tools = [lookup_cymbal_paint_catalog]

search_document = Agent(
    name="search_document",
    model=os.getenv("MODEL"),
    instruction="Use your search tool to look up facts about Cymbal Shops paint products.",
    tools=search_tools,
)

search_agent = Agent(
    name="search_agent",
    model=os.getenv("MODEL"),
    instruction="""
    If the user asked for specific paints, look up information on requested paints.
    Otherwise, provide the user information about all Cymbal Shops paints, including price
    and coverage rate.
    """,
    tools=[AgentTool(search_document, skip_summarization=False)],
)
