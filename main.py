"""
Main FastAPI application for Slack Bot.
Runs OAuth endpoints and handles webhook events (compatible with Vercel).
"""

import json
import hmac
import hashlib
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG, SLACK_SIGNING_SECRET
from auth.oauth import router as oauth_router
from bot.slack_app import slack_app
from utils.logger import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Get bot token for sending messages
SLACK_BOT_TOKEN = __import__('os').getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

# Initialize FastAPI app
app = FastAPI(
    title="Slack GPT Bot",
    description="A Slack bot powered by GPT",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include OAuth routes
app.include_router(oauth_router)


def verify_slack_request(request_body: bytes, timestamp: str, signature: str) -> bool:
    """
    Verify that the request came from Slack using the signing secret.
    """
    if not SLACK_SIGNING_SECRET:
        logger.warning("No signing secret configured - skipping verification")
        return True
    
    # Check timestamp to prevent replay attacks
    try:
        request_time = int(timestamp)
    except ValueError:
        return False
    
    current_time = int(time.time())
    if abs(current_time - request_time) > 300:  # 5 minutes
        logger.warning(f"Request timestamp too old: {request_time} vs {current_time}")
        return False
    
    # Verify signature
    sig_basestring = f"v0:{timestamp}:{request_body.decode()}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Slack GPT Bot is running"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "slack-gpt-bot"
    }


@app.post("/slack/events")
async def slack_events(request: Request) -> Response:
    """
    Handle Slack events via webhooks.
    Process app_mention and message.im events directly.
    """
    try:
        # Get headers and body
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        body = await request.body()
        
        logger.info("Received Slack webhook")
        
        # Verify signature
        if not verify_slack_request(body, timestamp, signature):
            logger.warning("Invalid signature")
            return Response("Unauthorized", status_code=401)
        
        # Parse request
        data = json.loads(body)
        logger.info(f"Event type: {data.get('type')}")
        
        # Handle URL verification
        if data.get("type") == "url_verification":
            logger.info("URL verification")
            return Response(data.get("challenge"), media_type="text/plain")
        
        # Handle events
        if data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")
            
            logger.info(f"Processing event: {event_type}")
            
            try:
                # Handle app mentions
                if event_type == "app_mention":
                    user_id = event.get("user")
                    channel_id = event.get("channel")
                    thread_ts = event.get("thread_ts", event.get("ts"))
                    
                    logger.info(f"Mention from {user_id} in {channel_id}")
                    
                    if slack_client:
                        slack_client.chat_postMessage(
                            channel=channel_id,
                            text="hey i am gptbot",
                            thread_ts=thread_ts
                        )
                        logger.info("Reply sent")
                
                # Handle DMs
                elif event_type == "message":
                    if event.get("channel_type") == "im":
                        user_id = event.get("user")
                        channel_id = event.get("channel")
                        
                        logger.info(f"DM from {user_id}")
                        
                        if slack_client:
                            slack_client.chat_postMessage(
                                channel=channel_id,
                                text="hey i am gptbot"
                            )
                            logger.info("DM reply sent")
            
            except SlackApiError as e:
                logger.error(f"Slack API error: {e.response['error']}")
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}", exc_info=True)
        
        # Always return 200 to acknowledge receipt
        return Response("OK", status_code=200)
    
    except Exception as e:
        logger.error(f"Error in /slack/events: {str(e)}", exc_info=True)
        return Response("OK", status_code=200)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Signing Secret configured: {bool(SLACK_SIGNING_SECRET)}")
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG
    )
