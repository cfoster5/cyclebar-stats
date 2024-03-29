import os
import time
from collections import defaultdict
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv, set_key
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()

location_id = os.getenv("LOCATION_ID")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
access_token = os.getenv("ACCESS_TOKEN")
access_token_expires_at = int(os.getenv("ACCESS_TOKEN_EXPIRES_AT"))


def get_access_token():
    timestamp_seconds = int(time.time())
    if timestamp_seconds >= access_token_expires_at:
        url = "https://members.cyclebar.com/api/sessions"
        payload = {
            "location_id": location_id,
            "email": email,
            "password": password,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload)
        new_access_token = response.json()["user"]["access_token"]
        new_expires_at = response.json()["user"]["access_token_expires_at"]
        set_key(".env", "ACCESS_TOKEN", new_access_token)
        set_key(
            ".env",
            "ACCESS_TOKEN_EXPIRES_AT",
            str(new_expires_at),
        )
        return new_access_token
    else:
        return access_token


def get_data(access_token):
    url = "https://members.cyclebar.com/api/workout_stats"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    return response.json()


def process_data(data):
    # Create a defaultdict to store ride counts for each month
    ride_counts_by_month = defaultdict(int)

    # Process each class entry
    for class_entry in data["class_stats"]:
        # Extract the month from the date property in schedule_entry
        date = class_entry["schedule_entry"]["date"]
        # Convert the string to a datetime object
        input_date = datetime.strptime(date, "%Y-%m-%d")
        # Format the datetime object to the desired output format
        output_date_str = input_date.strftime("%m/%Y")
        # Increment the count for the corresponding month
        ride_counts_by_month[output_date_str] += 1

    # Sort the list by month and year
    sorted_data = sorted(
        ride_counts_by_month.items(),
        key=lambda item: datetime.strptime(item[0], "%m/%Y"),
    )

    return sorted_data


def create_dataframe(json_data):
    df = pd.DataFrame(json_data, columns=["month", "rides"])
    df["month"] = pd.to_datetime(df["month"], format="%m/%Y")
    df["total_rides"] = df["rides"].cumsum()
    return df


@app.route("/")
def handle():
    access_token = get_access_token()
    data = get_data(access_token)
    sorted_data = process_data(data)
    df = create_dataframe(sorted_data)
    json = df.to_json(orient="records", date_format="iso")
    return json
