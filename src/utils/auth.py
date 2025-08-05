import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

def refresh_access_token(user_key):
    refresh_token = os.getenv(f"{user_key}_REFRESH_TOKEN")
    if not refresh_token:
        logging.warning(f"{user_key}_REFRESH_TOKEN not found in .env")
        return None, None

    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        tokens = response.json()
        logging.info(f"{user_key}: Access token refreshed.")
        if tokens["refresh_token"] != refresh_token:
            logging.warning(f"{user_key}: New refresh token issued: {tokens['refresh_token']}")
        return tokens["access_token"], tokens["refresh_token"]
    else:
        logging.error(f"{user_key}: Failed to refresh token: {response.text}")
        return None, None