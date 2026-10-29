import os
import fire
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

load_dotenv()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
bucket_name = f"gs://{project_id}-bucket" if project_id else None

if project_id and bucket_name:
    vertexai.init(project=project_id, location=location, staging_bucket=bucket_name)

def list():
    """List Agent Engine agents."""
    for agent in agent_engines.list():
        print(agent.display_name)
        print(agent.resource_name + "\n")

def delete(resource_name):
    """Delete an Agent Engine agent by its resource_name."""
    agent_engines.delete(resource_name, force=True)

if __name__ == "__main__":
    fire.Fire()

