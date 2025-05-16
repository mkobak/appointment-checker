# from dotenv import load_dotenv
import os
import requests
import datetime
import time
import ctypes
import json

# Load environment variables from .env file
# load_dotenv()

# Configuration
API_URL = os.getenv("API_URL")
PARAMS = {
    "owner": os.getenv("OWNER"),
    "appointmentTypeId": os.getenv("APPOINTMENT_TYPE_ID"),
    "calendarId": os.getenv("CALENDAR_ID"),
    "startDate": datetime.date.today().strftime("%Y-%m-%d"),
    "maxDays": 5,
    "timezone": "Europe/Zurich"
}

# File to store the last recorded closest date
THRESHOLD_FILE = "threshold_date.json"

# Load additional email configuration from environment variables
url = os.getenv("EMAIL_URL")
api_key = os.getenv("EMAIL_API_KEY")
sender = os.getenv("EMAIL_SENDER")
receiver = os.getenv("EMAIL_RECEIVER")


# Function to fetch appointments
def fetch_appointments():
    response = requests.get(API_URL, params=PARAMS)
    response.raise_for_status()
    return response.json()

# Function to send email notification
def send_simple_message(date):
    response = requests.post(
        url,
        auth=("api", api_key),
        data={
            "from": sender,
            "to": receiver,
            "subject": "New appointment found",
            "text": f"A new appointment has been found. Date: {date}"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


# Function to load the last threshold date from file
def load_threshold_date():
    try:
        with open(THRESHOLD_FILE, "r") as file:
            data = json.load(file)
            return datetime.datetime.strptime(data["threshold_date"], "%Y-%m-%d").date()
    except (FileNotFoundError, KeyError, ValueError):
        return None

# Function to save the new threshold date to file
def save_threshold_date(new_date):
    with open(THRESHOLD_FILE, "w") as file:
        json.dump({"threshold_date": new_date.strftime("%Y-%m-%d")}, file)

# Function to check for closer appointments
def check_for_closer_appointments():
    data = fetch_appointments()

    # Load the last threshold date
    last_threshold_date = load_threshold_date()
    print(f"Last threshold date: {last_threshold_date}")

    closest_date = None

    for date, appointments in data.items():
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        print(f"Checking appointment date: {date_obj}")

        if closest_date is None or date_obj < closest_date:
            closest_date = date_obj

    if closest_date:
        print(f"Closest appointment date found: {closest_date}")

        # Compare with the last threshold date
        if last_threshold_date is None or closest_date < last_threshold_date or closest_date != last_threshold_date:
            print(f"New closer appointment found: {closest_date}")
            send_simple_message(closest_date)
            save_threshold_date(closest_date)
        else:
            print("No new closer appointment found.")
    else:
        print("No appointments available.")

if __name__ == "__main__":
    check_for_closer_appointments()
