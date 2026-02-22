"""
Configuration settings for Slack Bot application.
Load environment variables from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack OAuth Configuration
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI")

# Validate credentials are loaded
if not SLACK_CLIENT_ID:
    raise ValueError("SLACK_CLIENT_ID not found in environment variables")
if not SLACK_CLIENT_SECRET:
    raise ValueError("SLACK_CLIENT_SECRET not found in environment variables")
if not SLACK_REDIRECT_URI:
    raise ValueError("SLACK_REDIRECT_URI not found in environment variables")

# Slack Signing Secret (for webhook verification)
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

# Slack Bot Tokens (for local development with Socket Mode)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Slack Bot Scopes
SLACK_SCOPES = [
    "app_mentions:read",
    "chat:write",
    "im:history",
    "im:read",
    "users:read"
]
