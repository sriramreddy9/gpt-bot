"""
Main FastAPI application for Slack Bot.
Runs the OAuth endpoints and initializes Socket Mode for event listening.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG
from auth.oauth import router as oauth_router
from bot.slack_app import init_socket_mode
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


@app.on_event("startup")
async def startup_event():
    """Initialize Socket Mode on startup."""
    logger.info("Starting Slack Bot...")
    init_socket_mode()
    logger.info("Slack Bot started successfully")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG
    )
