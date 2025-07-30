import sqlite3
import os
import json
import pandas as pd

#-----------------------------------------------------
#--------- Read JSON data and transform----------------
#-----------------------------------------------------

#read activities.json from data folder
with open("data/activities.json", "r") as f:
    activities = json.load(f)

# read json into pandas dataframe
df = pd.DataFrame(activities)
#handle athlete object {'id': 163373391, 'resource_state': 1}
df['athlete_id'] = df['athlete'].apply(lambda x: x['id'] if isinstance(x, dict) else None)
df['athlete_resource_state'] = df['athlete'].apply(lambda x: x['resource_state'] if isinstance(x, dict) else None)
# handle map column
df['map_id'] = df['map'].apply(lambda x: x['id'] if isinstance(x, dict) else None)
df['map_summary_polyline'] = df['map'].apply(lambda x: x['summary_polyline'] if isinstance(x, dict) else None)
df['map_resource_state'] = df['map'].apply(lambda x: x['resource_state'] if isinstance(x, dict) else None)
# drop has_kudoed total_photo_count
df = df.drop(columns=["has_kudoed", "total_photo_count", "athlete", "map", 'start_latlng', 'end_latlng'])

#convert distance to miles
df['distance'] = df['distance'] * 0.000621371
#convert moving_time to minutes
df['moving_time'] = df['moving_time'] / 60
#convert elapsed_time to minutes
df['elapsed_time'] = df['elapsed_time'] / 60
#convert total_elevation_gain to feet
df['total_elevation_gain'] = df['total_elevation_gain'] * 3.28084
#convert start_date to datetime
df['start_date'] = pd.to_datetime(df['start_date'], utc=True)
#convert start_date_local to datetime
df['start_date_local'] = pd.to_datetime(df['start_date_local'], utc=True)
#sort by start_date
df['start_date'] = pd.to_datetime(df['start_date'])
df = df.sort_values(by='start_date', ascending=False)


#----------------------------------------------------
#--------- Database setup and loading----------------
#----------------------------------------------------

# Create a new SQLite database (or connect to an existing one)
db_connection = sqlite3.connect("data/activities.db")

# Create a table for activities if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    name TEXT,
    distance REAL,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain INTEGER,
    type TEXT,
    sport_type TEXT,
    workout_type TEXT,
    start_date TIMESTAMP,
    start_date_local TIMESTAMP,
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
    gear_id INTEGER,
    start_latlng TEXT,
    end_latlng TEXT,
    average_speed REAL,
    max_speed REAL,
    has_heartrate BOOLEAN,
    average_heartrate REAL,
    max_heartrate REAL,
    heartrate_opt_out BOOLEAN,
    display_hide_heartrate_option BOOLEAN,
    elev_high INTEGER,
    elev_low INTEGER,
    upload_id INTEGER,
    upload_id_str TEXT,
    external_id TEXT,
    from_accepted_tag BOOLEAN,
    pr_count INTEGER,
    athlete_id INTEGER,
    athlete_resource_state INTEGER,
    map_id TEXT,
    map_summary_polyline TEXT,
    map_resource_state INTEGER
);
"""

with db_connection:
    db_connection.execute(create_table_query)

# Load the DataFrame into the SQLite database
#overwrite
df.to_sql("activities", db_connection, if_exists="replace", index=False)
#append
#df.to_sql("activities", db_connection, if_exists="append", index=False)

# Close the database connection
db_connection.close()
print("Data loaded successfully into SQLite database.")

#read the table back to verify
#db_connection = sqlite3.connect("data/activities.db")
#df_loaded = pd.read_sql_query("SELECT * FROM activities", db_connection)
#print(df_loaded.head())
#db_connection.close()