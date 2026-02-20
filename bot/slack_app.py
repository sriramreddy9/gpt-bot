"""
Slack Bolt App initialization with Socket Mode.
"""

import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from utils.logger import logger

# Initialize Slack App
slack_app = App(token=SLACK_BOT_TOKEN)

# Import and register handlers
from bot.handlers.mention_handler import register_mention_handler
from bot.handlers.dm_handler import register_dm_handler

# Register all event handlers
register_mention_handler(slack_app)
register_dm_handler(slack_app)


def start_socket_mode():
    """
    Start Socket Mode listener in a separate thread.
    """
    try:
        logger.info("Starting Slack Socket Mode...")
        handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"Error starting Socket Mode: {str(e)}")
        raise


def init_socket_mode():
    """
    Initialize Socket Mode in background thread.
    """
    socket_thread = threading.Thread(target=start_socket_mode, daemon=True)
    socket_thread.start()
    logger.info("Socket Mode thread started")
