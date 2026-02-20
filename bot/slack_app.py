"""
Slack Bolt App initialization with Webhooks (for Vercel compatibility).
Uses the bot token and signing secret for webhook events.
"""

from slack_bolt import App
from config.settings import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, SLACK_SCOPES
from utils.logger import logger

# Initialize Slack App with bot token and signing secret
# For webhooks, we use the bot token directly (not OAuth in the app)
slack_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    token_verification_enabled=True
)

# Import and register handlers
from bot.handlers.mention_handler import register_mention_handler
from bot.handlers.dm_handler import register_dm_handler

# Register all event handlers
register_mention_handler(slack_app)
register_dm_handler(slack_app)

logger.info("Slack App initialized with bot token and signing secret for webhooks")
