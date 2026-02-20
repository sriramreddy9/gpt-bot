"""
Handler for Direct Messages (DMs) to the bot.
"""

from utils.logger import logger


def register_dm_handler(app):
    """
    Register message event handler for DMs.
    Triggered when user sends a DM to the bot.
    """
    
    @app.event("message")
    def handle_dm(event, say, client):
        try:
            # Only handle DM messages (channel_type == "im")
            if event.get("channel_type") != "im":
                return
            
            logger.info(f"DM event received: {event}")
            
            user_id = event.get("user")
            channel_id = event.get("channel")
            
            logger.info(f"DM received from user {user_id}")
            
            # Send reply
            say(text="hey i am gptbot")
            
        except Exception as e:
            logger.error(f"Error handling DM: {str(e)}")
            say(f"Sorry, an error occurred: {str(e)}")
