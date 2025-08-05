import logging
import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from utils.logsetup import setup_logger
setup_logger()

#---------------------------------------------------------------------
#--------- Read JSON data and transform for athlete profiles----------
#---------------------------------------------------------------------
users = ["TROY", "SAM"]
user_profiles_map = {}

for user in users:
    try:
        with open(f"data/athlete_profile_{user}.json") as f:
            profile = json.load(f)
            if not isinstance(profile, dict):
                profile = {}
    except (FileNotFoundError, json.JSONDecodeError):
        profile = {}
    user_profiles_map[user] = profile

# Combine all profiles into a list (skip empty dicts)
all_profiles = [p for p in user_profiles_map.values() if p]

# Create one DataFrame from all profiles
df_profiles = pd.DataFrame(all_profiles)
#---------------------------------------------------------------------
#--------- Read JSON data and transform for activities----------------
#---------------------------------------------------------------------
users = ["TROY", "SAM"]
user_activities_map = {}

for user in users:
    try:
        with open(f"data/activities_{user}.json") as f:
            activities = json.load(f)
            if not isinstance(activities, list):
                activities = []
    except (FileNotFoundError, json.JSONDecodeError):
        activities = []
    user_activities_map[user] = activities

# Flatten all user activities into a single list
all_activities = []
for activities in user_activities_map.values():
    all_activities.extend(activities)

# Create one DataFrame from all combined activities
df = pd.DataFrame(all_activities)

if df.empty:
    logging.info("No new activities found. Skipping transformation and database load.")
else:
    # Extract nested fields
    df['athlete_id'] = df['athlete'].apply(lambda x: x['id'] if isinstance(x, dict) else None)
    df['athlete_resource_state'] = df['athlete'].apply(lambda x: x['resource_state'] if isinstance(x, dict) else None)

    df['map_id'] = df['map'].apply(lambda x: x['id'] if isinstance(x, dict) else None)
    df['map_summary_polyline'] = df['map'].apply(lambda x: x['summary_polyline'] if isinstance(x, dict) else None)
    df['map_resource_state'] = df['map'].apply(lambda x: x['resource_state'] if isinstance(x, dict) else None)

    df = df.drop(columns=["has_kudoed", "total_photo_count", "athlete", "map", 'start_latlng', 'end_latlng'])

    # Unit conversions
    df['distance'] = df['distance'] * 0.000621371
    df['moving_time'] = df['moving_time'] / 60
    df['elapsed_time'] = df['elapsed_time'] / 60
    df['total_elevation_gain'] = df['total_elevation_gain'] * 3.28084
    df['start_date'] = pd.to_datetime(df['start_date'], utc=True)
    df['start_date_local'] = pd.to_datetime(df['start_date_local'], utc=True)



#---------------------------------------------------------------------
#--------- Load athlete profiles into database-----------------------
#---------------------------------------------------------------------

    # Database setup and loading
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_port = os.getenv("POSTGRES_PORT", 5432)

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)

    create_table_query = """
    CREATE TABLE IF NOT EXISTS athlete_profiles (
        id BIGINT PRIMARY KEY,
        username TEXT,
        resource_state INTEGER,
        firstname TEXT,
        lastname TEXT,
        bio TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        sex TEXT,
        premium BOOLEAN,
        summit BOOLEAN,
        created_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ,
        badge_type_id INTEGER,
        weight FLOAT,
        profile_medium TEXT,
        profile TEXT,
        friend BOOLEAN,
        follower BOOLEAN
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_query))

    # Load athlete profiles into database
    df_profiles.to_sql("athlete_profiles", engine, if_exists="replace", index=False)
    logging.info("Athlete profiles loaded successfully into PostgreSQL database.")

#---------------------------------------------------------------------
#--------- Load activities into database-----------------------
#---------------------------------------------------------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS activities (
        id BIGINT PRIMARY KEY,
        name TEXT,
        distance FLOAT,
        moving_time INTEGER,
        elapsed_time INTEGER,
        total_elevation_gain FLOAT,
        type TEXT,
        sport_type TEXT,
        workout_type TEXT,
        start_date TIMESTAMPTZ,
        start_date_local TIMESTAMPTZ,
        timezone TEXT,
        utc_offset INTEGER,
        location_city TEXT,
        location_state TEXT,
        location_country TEXT,
        achievement_count INTEGER,
        kudos_count INTEGER,
        comment_count INTEGER,
        athlete_count INTEGER,
        photo_count INTEGER,
        trainer BOOLEAN,
        commute BOOLEAN,
        manual BOOLEAN,
        private BOOLEAN,
        visibility TEXT,
        flagged BOOLEAN,
        gear_id TEXT,
        average_speed FLOAT,
        max_speed FLOAT,
        has_heartrate BOOLEAN,
        average_heartrate FLOAT,
        max_heartrate FLOAT,
        heartrate_opt_out BOOLEAN,
        display_hide_heartrate_option BOOLEAN,
        elev_high FLOAT,
        elev_low FLOAT,
        upload_id BIGINT,
        upload_id_str TEXT,
        external_id TEXT,
        from_accepted_tag BOOLEAN,
        pr_count INTEGER,
        athlete_id BIGINT,
        athlete_resource_state INTEGER,
        map_id TEXT,
        map_summary_polyline TEXT,
        map_resource_state INTEGER
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_query))

    #overwrite
    df.to_sql("activities", engine, if_exists="replace", index=False)
    #append
    #df.to_sql("activities", engine, if_exists="append", index=False)
    logging.info("Data loaded successfully into PostgreSQL database.")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM activities LIMIT 10;"))
        for row in result:
            print(row)
