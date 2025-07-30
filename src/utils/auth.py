import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

def refresh_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": STRAVA_REFRESH_TOKEN
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        logging.info("Successfully refreshed access token.")
         # Check if a new refresh token is provided
        tokens = response.json()
        new_refresh_token = tokens["refresh_token"]
        if new_refresh_token != STRAVA_REFRESH_TOKEN:
            logging.warning("NOTICE: Strava issued a new refresh token. Please update your .env file.")
            logging.warning(f"New refresh token: {new_refresh_token}")
        return tokens["access_token"], new_refresh_token
    else:
        response.raise_for_status()