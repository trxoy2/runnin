import os
import json
import logging
import requests
from datetime import datetime, timezone, time
from utils.auth import refresh_access_token
from utils.logsetup import setup_logger

setup_logger()

def get_last_run_file(user_key):
    return f"data/last_run_{user_key}.txt"

def get_last_run_timestamp(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return int(f.read().strip())
    now = datetime.now(timezone.utc)
    return int(datetime.combine(now.date(), time.min, tzinfo=timezone.utc).timestamp())

def set_last_run_timestamp(ts, file_path):
    with open(file_path, "w") as f:
        f.write(str(ts))

def log_time(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%B %d %Y, %I:%M:%S %p UTC")

def fetch_athlete_profile(access_token, user_key):
    url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile = response.json()
        logging.info(f"{user_key}: Fetched athlete profile for {profile.get('firstname', '')} {profile.get('lastname', '')}")
        # Save profile JSON to file
        out_path = f"data/athlete_profile_{user_key}.json"
        with open(out_path, "w") as f:
            json.dump(profile, f, indent=2)
        return profile
    else:
        logging.error(f"{user_key}: Failed to fetch athlete profile: {response.status_code} - {response.text}")
        return None

def fetch_activity_data(user_key, access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}

    last_run_file = get_last_run_file(user_key)
    after_timestamp = get_last_run_timestamp(last_run_file)
    logging.info(f"{user_key}: Fetching activities after {log_time(after_timestamp)}")

    # Uncomment or remove hardcoded after_timestamp for bulk overwrite
    #after_timestamp = 1735689600 

    params = {"after": after_timestamp, "per_page": 100}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        logging.error(f"{user_key}: Failed to fetch activities: {response.status_code} - {response.text}")
        return []

    activities = response.json()
    logging.info(f"{user_key}: Fetched {len(activities)} activities.")

    if activities:
        latest_ts = max(
            int(datetime.strptime(a["start_date"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp())
            for a in activities
        )
        set_last_run_timestamp(latest_ts, last_run_file)
        logging.info(f"{user_key}: Updated last run to {log_time(latest_ts)}")

    return activities

def main():
    users = ["TROY", "SAM"]

    for user in users:
        access_token, _ = refresh_access_token(user)
        if not access_token:
            logging.error(f"{user}: No access token, skipping.")
            continue

        # Fetch and save athlete profile
        fetch_athlete_profile(access_token, user)

        # Fetch and save activities
        activities = fetch_activity_data(user, access_token)
        out_path = f"data/activities_{user}.json"
        with open(out_path, "w") as f:
            json.dump(activities, f, indent=2)
        logging.info(f"{user}: Saved activities to {out_path}")

if __name__ == "__main__":
    main()