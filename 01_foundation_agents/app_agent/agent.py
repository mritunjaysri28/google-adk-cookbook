import asyncio
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types

import os
from dotenv import load_dotenv

import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.callback_logging import log_query_to_model, log_model_response

# 1. Load environment variables from the agent directory's .env file
load_dotenv()
# google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
# google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
google_genai_use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
model_name = os.getenv("MODEL")


# Create an async main function
async def main():

    # 2. Set or load other variables
    app_name = 'my_agent_app'
    user_id_1 = 'user1'

    # 3. Define Your Agent
    root_agent = Agent(
        model=model_name,
        name="trivia_agent",
        instruction="Answer questions.",
        before_model_callback=log_query_to_model,
        after_model_callback=log_model_response,

    )

    # 3. Create a Runner
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )

    # 4. Create a session
    my_session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id_1
    )

    # 5. Prepare a function to package a user's message as
    # genai.types.Content, run it asynchronously, and iterate
    # through the response
    async def run_prompt(session: Session, new_message: str):
        content = types.Content(
                role='user', parts=[types.Part.from_text(text=new_message)]
            )
        print('** User says:', content.model_dump(exclude_none=True))
        async for event in runner.run_async(
            user_id=user_id_1,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    # 6. Use this function on a new query
    query = "What is the capital of France?"
    await run_prompt(my_session, query)

if __name__ == "__main__":
    asyncio.run(main())