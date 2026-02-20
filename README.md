# Slack GPT Bot

A Python-based Slack bot that integrates with OpenAI's GPT model. The bot listens for mentions and direct messages, and responds intelligently.

## Project Structure

```
slack_bot/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Environment variables and settings
├── bot/                   # Bot core functionality
│   ├── __init__.py
│   ├── slack_app.py       # Slack Bolt app initialization
│   └── handlers/          # Event handlers
│       ├── __init__.py
│       ├── mention_handler.py    # @bot mentions
│       └── dm_handler.py         # Direct messages
├── auth/                  # OAuth authentication
│   ├── __init__.py
│   └── oauth.py          # Slack OAuth endpoints
├── utils/                # Utility functions
│   ├── __init__.py
│   └── logger.py         # Logging configuration
├── main.py               # FastAPI app entry point
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Prerequisites

- Python 3.8+
- Slack Workspace Admin access
- A Slack App created at https://api.slack.com/apps

## Setup Instructions

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name: `GPT Bot`
5. Select your workspace
6. Click "Create App"

### 2. Configure OAuth & Permissions

1. Go to **OAuth & Permissions** in the left menu
2. Under **Redirect URLs**, add: `http://localhost:8000/slack/oauth/callback`
3. Under **Bot Token Scopes**, add all the required scopes:
   - app_mentions:read
   - assistant:write
   - bookmarks:read
   - bookmarks:write
   - calls:read / write
   - canvases:read / write
   - channels:history, join, manage, read, write.*
   - chat:write*
   - commands
   - conversations.connect:manage
   - emoji:read
   - im:history, read, write
   - mpim:history
   - users:read, write

4. Scroll to **Bot Token** and copy it (starts with `xoxb-`)

### 3. Enable Socket Mode

1. Go to **Socket Mode** in the left menu
2. Click "Enable Socket Mode"
3. Create an **App-Level Token** with scope: `connections:write`
4. Copy the token (starts with `xapp-`)

### 4. Configure Event Subscriptions

1. Go to **Event Subscriptions**
2. Toggle "Enable Events" to **On**
3. Under **Subscribe to bot events**, add:
   - `app_mention`
   - `message.im`
4. Save changes
5. Reinstall the app

### 5. Install the Project

```bash
# Clone or navigate to the project
cd slack_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Slack OAuth Configuration
SLACK_CLIENT_ID=your_client_id
SLACK_CLIENT_SECRET=your_client_secret
SLACK_REDIRECT_URI=http://localhost:8000/slack/oauth/callback

# Slack Bot Tokens
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

Replace with your actual values from the Slack App dashboard.

## Running the Bot

```bash
# Make sure virtual environment is activated
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## Usage

### Install Bot to Workspace

1. Open `http://localhost:8000/slack/connect` in your browser
2. Select the workspace
3. Review and approve permissions
4. Bot will be installed

### Use the Bot in Slack

**Mention in Channel:**
```
@gptbot hello
```

**Direct Message:**
- Send a DM to @gptbot

**Bot will respond:**
```
hey i am gptbot
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health check
- `GET /slack/connect` - Start OAuth flow
- `GET /slack/oauth/callback` - OAuth callback handler

## Extending the Bot

### Adding New Event Handlers

1. Create a new handler file in `bot/handlers/`
2. Define a `register_*_handler` function
3. Import and call it in `bot/slack_app.py`

Example:
```python
# bot/handlers/reaction_handler.py
def register_reaction_handler(app):
    @app.event("reaction_added")
    def handle_reaction(event, say):
        # Handle reaction logic
        pass
```

Then in `bot/slack_app.py`:
```python
from bot.handlers.reaction_handler import register_reaction_handler
register_reaction_handler(slack_app)
```

## Troubleshooting

### Socket Mode Connection Issues
- Verify `SLACK_APP_TOKEN` is correct
- Check that Socket Mode is enabled in Slack App settings
- Check logs for connection errors

### OAuth Issues
- Verify `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`
- Ensure redirect URI matches exactly in Slack settings
- Check browser console for errors

### Bot Not Responding
- Verify event subscriptions are enabled
- Check that bot is invited to channels
- Check application logs for errors

## Development

### Logging

All events are logged to console. Check `utils/logger.py` to configure logging levels:
- Set `DEBUG=False` in `.env` for production
- Set `DEBUG=True` in `.env` for development

### Adding Dependencies

```bash
pip install package_name
pip freeze > requirements.txt
```

## Future Enhancements

- [ ] GPT integration for intelligent responses
- [ ] User input processing and context
- [ ] Message history storage
- [ ] Custom commands
- [ ] Admin dashboard
- [ ] Analytics and metrics

## Support

For issues with Slack API, visit: https://api.slack.com/docs

## License

MIT
