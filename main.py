"""
Main FastAPI application for Slack Bot.
Runs OAuth endpoints and handles webhook events (compatible with Vercel).
"""

import json
import hmac
import hashlib
import time
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG, SLACK_SIGNING_SECRET
from auth.oauth import router as oauth_router
from bot.slack_app import slack_app
from utils.logger import logger
from utils.ai_agent import call_ai_agent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from collections import deque
from datetime import datetime, timedelta

# Get bot token for sending messages
SLACK_BOT_TOKEN = __import__('os').getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

# Track processed events to prevent duplicates (Slack retries)
# Store tuples of (event_id, timestamp) - keep last 1000 events
processed_events = deque(maxlen=1000)

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


@app.get("/debug/config")
def debug_config():
    """
    Debug endpoint to check which environment variables are set.
    Only accessible in DEBUG mode.
    """
    if not DEBUG:
        return JSONResponse({
            "status": "error",
            "message": "Debug endpoint only available in DEBUG mode"
        }, status_code=403)
    
    return JSONResponse({
        "status": "debug_info",
        "env_vars": {
            "SLACK_CLIENT_ID": "✓ SET" if os.getenv("SLACK_CLIENT_ID") else "✗ MISSING",
            "SLACK_CLIENT_SECRET": "✓ SET" if os.getenv("SLACK_CLIENT_SECRET") else "✗ MISSING",
            "SLACK_REDIRECT_URI": "✓ SET" if os.getenv("SLACK_REDIRECT_URI") else "✗ MISSING",
            "SLACK_BOT_TOKEN": "✓ SET" if os.getenv("SLACK_BOT_TOKEN") else "✗ MISSING",
            "SLACK_APP_TOKEN": "✓ SET" if os.getenv("SLACK_APP_TOKEN") else "✗ MISSING",
            "SLACK_SIGNING_SECRET": "✓ SET" if os.getenv("SLACK_SIGNING_SECRET") else "✗ MISSING",
            "LYZR_API_KEY": "✓ SET" if os.getenv("LYZR_API_KEY") else "✗ MISSING",
        },
        "message": "Check Vercel dashboard Environment Variables if any show MISSING"
    })


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


def is_event_processed(event_id: str) -> bool:
    """
    Check if we've already processed this event (to prevent handling Slack retries).
    """
    for processed_id, _ in processed_events:
        if processed_id == event_id:
            logger.info(f"Event {event_id} already processed, skipping")
            return True
    return False


def mark_event_processed(event_id: str):
    """
    Mark an event as processed to prevent handling retries.
    """
    processed_events.append((event_id, datetime.now()))
    logger.info(f"Marked event {event_id} as processed")


async def process_slack_event(event: dict, event_id: str):
    """
    Process Slack event asynchronously.
    This runs in the background after we return 200 OK to Slack.
    """
    try:
        event_type = event.get("type")
        logger.info(f"Processing event {event_id} type {event_type}")
        
        # Handle app mentions
        if event_type == "app_mention":
            user_id = event.get("user")
            channel_id = event.get("channel")
            thread_ts = event.get("thread_ts", event.get("ts"))
            message_text = event.get("text", "")
            
            logger.info(f"Mention from {user_id} in {channel_id}: {message_text}")
            
            if slack_client:
                try:
                    # Call AI agent to get response
                    ai_response = call_ai_agent(message_text)
                    
                    slack_client.chat_postMessage(
                        channel=channel_id,
                        text=ai_response,
                        thread_ts=thread_ts
                    )
                    logger.info(f"AI response sent: {ai_response}")
                except Exception as e:
                    logger.error(f"Error sending mention response: {str(e)}")
        
        # Handle DMs
        elif event_type == "message":
            # Skip if this is a bot message or a message from our bot
            if event.get("bot_id") or event.get("subtype") in ["bot_message", "message_deleted"]:
                logger.info("Skipping bot message")
            elif not event.get("user"):
                logger.info("Skipping message without user ID")
            else:
                # Check if this is a direct message
                channel_type = event.get("channel_type")
                channel_id = event.get("channel")
                user_id = event.get("user")
                
                logger.info(f"Message event - channel_type: {channel_type}, channel: {channel_id}, user: {user_id}")
                
                # D-prefix indicates direct message channel, or channel_type is "im"
                if channel_type == "im" or (channel_id and channel_id.startswith("D")):
                    message_text = event.get("text", "")
                    logger.info(f"DM from {user_id} in {channel_id}: {message_text}")
                    
                    if slack_client:
                        try:
                            # Call AI agent to get response
                            ai_response = call_ai_agent(message_text)
                            
                            slack_client.chat_postMessage(
                                channel=channel_id,
                                text=ai_response
                            )
                            logger.info(f"AI DM response sent: {ai_response}")
                        except Exception as e:
                            logger.error(f"Error sending DM response: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {str(e)}", exc_info=True)


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


@app.get("/slack/events")
def slack_events_get() -> Response:
    """
    Handle GET requests to the webhook endpoint.
    Slack may test the endpoint with a GET request.
    """
    logger.info("Received GET request to /slack/events")
    return Response("OK", status_code=200)


@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Handle Slack events via webhooks.
    Returns 200 OK immediately, processes events asynchronously.
    This prevents Slack from retrying due to slow AI API calls.
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
            event_id = data.get("event_id")
            
            # Check if we've already processed this event
            if is_event_processed(event_id):
                logger.info(f"Event {event_id} is a retry, returning 200 OK without processing")
                return Response("OK", status_code=200)
            
            # Mark as processed
            mark_event_processed(event_id)
            
            # Process event asynchronously in background
            background_tasks.add_task(process_slack_event, event, event_id)
            logger.info(f"Event {event_id} queued for background processing")
        
        # Always return 200 to acknowledge receipt immediately
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
