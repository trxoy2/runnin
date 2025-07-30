import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from utils.logsetup import setup_logger
setup_logger()
#-----------------------------------------------------
#--------- Read JSON data and transform----------------
#-----------------------------------------------------

with open("data/activities.json", "r") as f:
    activities = json.load(f)

df = pd.DataFrame(activities)

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

#----------------------------------------------------
#--------- Database setup and loading----------------
#----------------------------------------------------

db_host = os.getenv("POSTGRES_HOST", "db")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
db_port = os.getenv("POSTGRES_PORT", 5432)

connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

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

# Append data to the existing table, do not replace
#df.to_sql("activities", engine, if_exists="append", index=False)
# Overwrite the table if it already exists
df.to_sql("activities", engine, if_exists="replace", index=False)

print("Data loaded successfully into PostgreSQL database.")

# select all data to verify
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM activities LIMIT 10;"))
    for row in result:
        print(row)
    conn.close()    
