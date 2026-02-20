import requests
import json

# ================= CONFIG =================

USER_ID = "sriram@lyzr.ai"
AGENT_ID = "6998b8e647a42b7319aeace1"
SESSION_ID = "6998b8e647a42b7319aeace1-wy3l2mpgi2"

CHAT_URL = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
# ==========================================

payload = {
    "user_id": USER_ID,
    "agent_id": AGENT_ID,
    "session_id": SESSION_ID,
    "message": "Hello, how are you?"
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def extract_clean_response(api_json):
    try:
        # Step 1: Get outer "response"
        outer_response = api_json.get("response", "")

        # Step 2: Parse the inner JSON string
        parsed_inner = json.loads(outer_response)

        # Step 3: Extract actual message
        return parsed_inner.get("response", "")

    except Exception as e:
        print("⚠️ Parsing error:", str(e))
        return "Unable to parse response"

try:
    response = requests.post(CHAT_URL, headers=headers, json=payload)

    if response.status_code == 200:
        api_json = response.json()


        clean_message = extract_clean_response(api_json)

        print("\n✅ Clean Extracted Message:")
        print(clean_message)

    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print("❌ Exception occurred:", str(e))