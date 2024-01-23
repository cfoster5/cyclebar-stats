from datetime import datetime
import json
from collections import defaultdict
import pandas as pd
import plotly.express as px

# Load JSON data from file
with open("workout_stats.json", "r") as file:
    data = json.load(file)

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


# Custom sorting function to extract month and year from the date string
def custom_sort(item):
    return (int(item[0].split("/")[1]), int(item[0].split("/")[0]))


# Sort the list by month and year
sorted_data = sorted(ride_counts_by_month.items(), key=custom_sort)

# Print the ride counts for each month
# for month, count in sorted_data:
#     print(f"{month}: {count} rides")

total_ride_count = 0
json_data = []
for month, rides in sorted_data:
    total_ride_count += rides
    json_data.append({"Month": month, "Rides": rides, "Total Rides": total_ride_count})


df = pd.DataFrame(json_data, columns=["Month", "Rides", "Total Rides"])
df["Month"] = pd.to_datetime(df["Month"], format="%m/%Y")
fig.show()
