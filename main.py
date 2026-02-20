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
    Verifies the request signature and processes events.
    """
    try:
        # Get headers
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        
        # Get body
        body = await request.body()
        
        logger.info(f"Received Slack webhook - Timestamp: {timestamp}, Has signature: {bool(signature)}")
        
        # Verify request
        if not verify_slack_request(body, timestamp, signature):
            logger.warning("Invalid Slack request signature")
            return Response("Unauthorized", status_code=401)
        
        # Parse body
        data = json.loads(body)
        
        # Handle URL verification challenge
        if data.get("type") == "url_verification":
            logger.info("Responding to Slack URL verification challenge")
            return Response(data.get("challenge"), media_type="text/plain")
        
        # Handle events
        logger.info(f"Processing Slack event: {data.get('type')}")
        
        # Process event with Slack Bolt
        try:
            # Use Slack Bolt's dispatch method
            response = await slack_app.async_dispatch(request)
            return response
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}", exc_info=True)
            return Response("OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Error in /slack/events: {str(e)}", exc_info=True)
        return Response("Internal Server Error", status_code=500)


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
