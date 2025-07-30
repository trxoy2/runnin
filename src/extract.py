import requests
import logging
import json
from datetime import datetime, timezone, time
import os
from utils.logsetup import setup_logger
from utils.auth import refresh_access_token

LAST_RUN_FILE = "data/last_run.txt"
setup_logger()

def log_human_readable_time(ts):
    utc_time = datetime.fromtimestamp(ts, tz=timezone.utc)
    formatted_time = utc_time.strftime("%A, %B %d, %Y, at %I:%M:%S %p %Z").replace(" 0", " ")
    return formatted_time

def get_last_run_timestamp():
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, "r") as f:
            ts = int(f.read().strip())
            log_human_readable_time(ts)
            return ts
    # Default: start of today UTC
    now = datetime.now(timezone.utc)
    start_of_day = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    ts = int(start_of_day.timestamp())
    log_human_readable_time(ts)
    return ts

def set_last_run_timestamp(ts):
    with open(LAST_RUN_FILE, "w") as f:
        f.write(str(ts))

def fetch_activity_data():
    access_token, _ = refresh_access_token()
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    after_timestamp = get_last_run_timestamp()
    after_timestamp = log_human_readable_time(after_timestamp)
    logging.info(f"Fetching activities after: {after_timestamp}")
    # hardcode temporary after timestamp for bulk upload
    after_timestamp = 1735689600 
    params = {
        "after": after_timestamp,
        "per_page": 100
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        logging.info("Successfully fetched activity data since last run.")
        activities = response.json()

        if activities:
            latest_dt = max(
                datetime.strptime(activity['start_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                for activity in activities if 'start_date' in activity
            )

            latest_ts = int(latest_dt.timestamp())

            set_last_run_timestamp(latest_ts)
            formatted_tm = log_human_readable_time(latest_ts)
            logging.info(f"Updated last run timestamp to: {formatted_tm}")
        else:
            logging.info("No new activities found; last run timestamp not updated.")
    else:
        logging.error(f"Failed to fetch activity data: {response.status_code} - {response.text}")
        raise Exception(f"Error fetching activity data: {response.status_code} - {response.text}")
    
    return activities


activities = fetch_activity_data()
logging.info(f"Fetched {len(activities)} activities from Strava since last run.")
with open("data/activities.json", "w") as f:
    json.dump(activities, f, indent=2)