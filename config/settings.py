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

# Slack Bot Tokens
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Slack Bot Scopes
SLACK_SCOPES = [
    "app_mentions:read",
    "assistant:write",
    "bookmarks:read",
    "bookmarks:write",
    "calls:read",
    "calls:write",
    "canvases:read",
    "canvases:write",
    "channels:history",
    "channels:join",
    "channels:manage",
    "channels:read",
    "channels:write.invites",
    "channels:write.topic",
    "chat:write",
    "chat:write.customize",
    "chat:write.public",
    "commands",
    "conversations.connect:manage",
    "emoji:read",
    "im:history",
    "im:read",
    "im:write",
    "mpim:history",
    "users:read",
    "users:write"
]
