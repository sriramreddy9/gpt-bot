"""
Main FastAPI application for Slack Bot.
Runs OAuth endpoints and handles webhook events (compatible with Vercel).
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG
from auth.oauth import router as oauth_router
from bot.slack_app import slack_app
from utils.logger import logger
from slack_bolt.adapter.fastapi import SlackRequestHandler

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

# Initialize Slack Bolt handler for FastAPI
handler = SlackRequestHandler(slack_app)


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
    Slack will POST events to this endpoint.
    The SlackRequestHandler will route to appropriate handlers.
    """
    logger.info("Received Slack event webhook")
    return await handler.async_handle(request)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG
    )
