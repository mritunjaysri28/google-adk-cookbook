import logging
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

try:
    from .logging_config import setup_logger
except ImportError:
    import logging_config
    setup_logger = logging_config.setup_logger

setup_logger()

def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts and llm_request.contents[-1].parts[0].text:
            last_user_message = llm_request.contents[-1].parts[0].text
            logging.info(f"[QUERY to {callback_context.agent_name}]: {last_user_message}")

def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(f"[RESPONSE from {callback_context.agent_name}]: {part.text}")
            elif part.function_call:
                logging.info(f"[FUNCTION CALL from {callback_context.agent_name}]: {part.function_call.name}")

