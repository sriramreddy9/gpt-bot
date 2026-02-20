"""
Utility to call Lyzr AI Agent API
"""

import requests
import json
import os
from utils.logger import logger

# Load config from environment
LYZR_API_KEY = os.getenv("LYZR_API_KEY")
LYZR_USER_ID = os.getenv("LYZR_USER_ID")
LYZR_AGENT_ID = os.getenv("LYZR_AGENT_ID")
LYZR_SESSION_ID = os.getenv("LYZR_SESSION_ID")
LYZR_CHAT_URL = os.getenv("LYZR_CHAT_URL")


def extract_clean_response(api_json):
    """
    Extract the clean response from the Lyzr AI API response.
    
    The API returns a nested JSON structure:
    {
        "response": "{\"response\": \"actual message\"}"
    }
    """
    try:
        # Step 1: Get outer "response"
        outer_response = api_json.get("response", "")

        # Step 2: Parse the inner JSON string
        parsed_inner = json.loads(outer_response)

        # Step 3: Extract actual message
        clean_msg = parsed_inner.get("response", "")
        logger.info(f"Extracted AI response: {clean_msg}")
        return clean_msg

    except Exception as e:
        logger.error(f"Error parsing AI response: {str(e)}")
        return "Unable to parse response"


def call_ai_agent(message: str) -> str:
    """
    Call the Lyzr AI Agent with a message and return the response.
    
    Args:
        message: User message to send to the AI agent
        
    Returns:
        Cleaned response from the AI agent
    """
    if not all([LYZR_API_KEY, LYZR_USER_ID, LYZR_AGENT_ID, LYZR_SESSION_ID, LYZR_CHAT_URL]):
        logger.error("Missing Lyzr AI configuration")
        return "AI agent not configured"
    
    payload = {
        "user_id": LYZR_USER_ID,
        "agent_id": LYZR_AGENT_ID,
        "session_id": LYZR_SESSION_ID,
        "message": message
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LYZR_API_KEY
    }

    try:
        logger.info(f"Calling AI agent with message: {message}")
        response = requests.post(LYZR_CHAT_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            api_json = response.json()
            clean_message = extract_clean_response(api_json)
            logger.info(f"AI agent returned: {clean_message}")
            return clean_message
        else:
            logger.error(f"AI API error: {response.status_code} - {response.text}")
            return f"Error from AI agent: {response.status_code}"

    except requests.exceptions.Timeout:
        logger.error("AI agent request timed out")
        return "Request timed out"
    except Exception as e:
        logger.error(f"Exception calling AI agent: {str(e)}")
        return f"Error: {str(e)}"
