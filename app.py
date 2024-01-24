from datetime import datetime
from collections import defaultdict
import time
import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv, set_key
import os

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


# Custom sorting function to extract month and year from the date string
def custom_sort(item):
    return (int(item[0].split("/")[1]), int(item[0].split("/")[0]))


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
        # output_date_str = input_date.strftime("%B %Y")
        output_date_str = input_date.strftime("%m/%Y")
        # Increment the count for the corresponding month
        ride_counts_by_month[output_date_str] += 1

    # Manually add empty months
    ride_counts_by_month.update({"11/2021": 0, "12/2021": 0})

    # Sort the list by month and year
    sorted_data = sorted(ride_counts_by_month.items(), key=custom_sort)

    total_ride_count = 0
    json_data = []
    for month, rides in sorted_data:
        total_ride_count += rides
        json_data.append(
            {"Month": month, "Rides": rides, "Total Rides": total_ride_count}
        )

    json_data.pop()
    return json_data


def create_dataframe(json_data):
    df = pd.DataFrame(json_data, columns=["Month", "Rides", "Total Rides"])
    df["Month"] = pd.to_datetime(df["Month"], format="%m/%Y")
    return df


def create_plot(df):
    # fig = px.line(df, x="Month", y="Rides")
    fig = px.line(df, x="Month", y="Rides", width=900, height=1600)
    # fig = px.line(df, x="Month", y="Total Rides", width=900, height=1600)
    # fig = px.line(df, x="Month", y=["Rides", "Total Rides"])
    fig.update_traces(line_color="#d0021b")
    fig.show()


if __name__ == "__main__":
    access_token = get_access_token()
    data = get_data(access_token)
    json_data = process_data(data)
    df = create_dataframe(json_data)
    create_plot(df)
