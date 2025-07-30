import requests

# This code snippet is for testing the Strava OAuth token exchange, specifically for obtaining a new access token.
response = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": "170469",
        "client_secret": "2379664a12ad335f771a9fe36ddc465f7e95c732",
        "code": "074987963eec4683cd3a108768d868a4ba1c0c30",
        "grant_type": "authorization_code"
    }
)
print(response.json())