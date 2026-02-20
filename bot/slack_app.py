"""
Slack Bolt App initialization with Webhooks (for Vercel compatibility).
Uses OAuth with file-based installation store to handle multiple workspaces.
"""

from slack_bolt import App
from config.settings import SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_SIGNING_SECRET, SLACK_SCOPES
from utils.logger import logger

# Initialize Slack App with OAuth support
slack_app = App(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=SLACK_SCOPES,
    signing_secret=SLACK_SIGNING_SECRET,
    installation_store_enabled=True,
    token_verification_enabled=True
)

# Import and register handlers
from bot.handlers.mention_handler import register_mention_handler
from bot.handlers.dm_handler import register_dm_handler

# Register all event handlers
register_mention_handler(slack_app)
register_dm_handler(slack_app)

logger.info("Slack App initialized with OAuth and Webhook support")
