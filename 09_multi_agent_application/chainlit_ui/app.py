import chainlit as cl
import os
import sys
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load local and root environment configuration
load_dotenv()
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env"))
if os.path.exists(root_env):
    load_dotenv(root_env)

# Determine whether to use remote Vertex AI Reasoning Engine or local ADK Multi-Agent
use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper() == "TRUE"
cloud_agent = None

if use_vertexai and os.getenv("GOOGLE_CLOUD_PROJECT"):
    try:
        import vertexai
        from vertexai import agent_engines

        project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        bucket_name = f"gs://{project_id}-bucket"

        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=bucket_name,
        )

        engine_id = os.environ.get(
            "REASONING_ENGINE_ID",
            "projects/1095543277514/locations/us-central1/reasoningEngines/712696840054636544",
        )
        cloud_agent = agent_engines.get(engine_id)
        print(f"[INFO] Successfully connected to Vertex AI Reasoning Engine: {engine_id}")
    except Exception as e:
        print(f"[INFO] Vertex AI Agent Engine not reachable ({e}). Falling back to local paint_agent multi-agent.")
        cloud_agent = None

if not cloud_agent:
    # Ensure parent directory is in sys.path to import local paint_agent
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from paint_agent.agent import root_agent

    local_runner = InMemoryRunner(agent=root_agent, app_name="cymbal_shops_paint")
    print("[INFO] Initialized local paint_agent multi-agent system via ADK InMemoryRunner.")


def convert_img_tags_to_chainlit_images(msg):
    img_list = []
    soup = BeautifulSoup(msg.content, "html.parser")
    for img_tag in soup.find_all("img"):
        if img_tag.has_attr("src"):
            img = cl.Image(url=img_tag["src"], name="swatch", display="inline")
            img_list.append(img)
    msg.elements = img_list
    msg.content = soup.get_text()
    return msg


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Painting Project Help",
            message="Tell me about Cymbal Shops' interior paints.",
            icon="/public/swatches.svg",
        )
    ]


@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    user_id = "user"
    cl.user_session.set("user_id", user_id)
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

    if cloud_agent:
        session_details = cloud_agent.create_session(user_id=user_id)
        cl.user_session.set("session_id", session_details["id"])
    else:
        local_session = await local_runner.session_service.create_session(
            app_name="cymbal_shops_paint", user_id=user_id
        )
        cl.user_session.set("session_id", local_session.id)


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")

    msg = cl.Message(content="")

    if cloud_agent:
        events = cloud_agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message.content,
        )
        for event in events:
            if isinstance(event, dict) and "content" in event:
                for part in event["content"].get("parts", []):
                    if "text" in part:
                        await msg.stream_token(part["text"])
    else:
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message.content)],
        )
        async for event in local_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        await msg.stream_token(part.text)

    msg = convert_img_tags_to_chainlit_images(msg)
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
