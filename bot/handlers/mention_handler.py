"""
Handler for @bot mentions in channels.
"""

from utils.logger import logger


def register_mention_handler(app):
    """
    Register app_mention event handler.
    Triggered when the bot is mentioned with @gptbot
    """
    
    @app.event("app_mention")
    def handle_mention(event, say, client):
        try:
            logger.info(f"Mention event received: {event}")
            
            user_id = event.get("user")
            channel_id = event.get("channel")
            thread_ts = event.get("thread_ts", event.get("ts"))
            
            logger.info(f"Bot mentioned by user {user_id} in channel {channel_id}")
            
            # Send reply
            say(
                text="hey i am gptbot",
                thread_ts=thread_ts
            )
            
        except Exception as e:
            logger.error(f"Error handling mention: {str(e)}")
            say(f"Sorry, an error occurred: {str(e)}")
