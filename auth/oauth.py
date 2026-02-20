"""
Slack OAuth endpoints for app installation and authorization.
"""

import requests
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from config.settings import (
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
    SLACK_REDIRECT_URI,
    SLACK_SCOPES
)
from utils.logger import logger

router = APIRouter(
    prefix="/slack",
    tags=["slack_oauth"]
)


@router.get("/connect")
def connect_slack():
    """
    Redirect user to Slack OAuth consent screen.
    """
    scope_str = ",".join(SLACK_SCOPES)
    oauth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&scope={scope_str}"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
        f"&state=secure_random_state"
    )
    logger.info(f"Redirecting to Slack OAuth: {oauth_url}")
    return RedirectResponse(oauth_url)


@router.get("/oauth/callback")
def slack_callback(code: str, state: str):
    """
    Handle Slack OAuth callback and exchange code for token.
    """
    try:
        logger.info(f"Received Slack OAuth callback with code: {code[:20]}...")
        
        url = "https://slack.com/api/oauth.v2.access"
        payload = {
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI
        }
        
        response = requests.post(url, data=payload)
        slack_data = response.json()
        
        logger.info(f"Slack OAuth Response: {slack_data}")
        
        if slack_data.get("ok"):
            logger.info(f"Successfully installed bot in workspace: {slack_data.get('team_id')}")
            return JSONResponse({
                "status": "success",
                "message": "Bot installed successfully!",
                "team_id": slack_data.get("team_id"),
                "bot_user_id": slack_data.get("bot_user_id"),
                "authed_user": slack_data.get("authed_user"),
                "scopes": slack_data.get("scope")
            })
        else:
            error_msg = slack_data.get("error", "Unknown error")
            logger.error(f"Slack OAuth Error: {error_msg}")
            return JSONResponse({
                "status": "error",
                "message": f"OAuth failed: {error_msg}"
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"Exception in OAuth callback: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)
