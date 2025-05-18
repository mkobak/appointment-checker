import os
import requests
import datetime
import json
# from dotenv import load_dotenv # comment out for deployment on github actions

# Load environment variables from .env file
# load_dotenv() # comment out for deployment on github actions

# --- Configuration ---
# API and email configuration loaded from environment variables
API_URL = os.getenv("API_URL")
EMAIL_API_URL = os.getenv("EMAIL_URL")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Appointment search parameters
APPOINTMENT_PARAMS = {
    "startDate": datetime.date.today().strftime("%Y-%m-%d"),
    "maxDays": 5,
    "timezone": "Europe/Zurich"
}

# File to persist the last notified closest appointment date
LATEST_DATE_FILE = "latest_date.json"

# --- Appointment Fetching ---
def fetch_appointment_data():
    """Fetch available appointments from the API."""
    response = requests.get(API_URL, params=APPOINTMENT_PARAMS)
    # print(f"Request URL: {response.url}")
    response.raise_for_status()
    return response.json()

# --- Email Notification ---
def send_email_notification(appointment_date):
    """Send an email notification about a new closer appointment."""
    response = requests.post(
        EMAIL_API_URL,
        auth=("api", EMAIL_API_KEY),
        data={
            "from": EMAIL_SENDER,
            "to": EMAIL_RECEIVER,
            "subject": f"New appointment found - {appointment_date}",
            "text": f"A new appointment has been found. Date: {appointment_date}"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

# --- Latest Date Persistence ---
def load_last_notified_date():
    """Load the last notified closest appointment date from file."""
    try:
        with open(LATEST_DATE_FILE, "r") as file:
            data = json.load(file)
            return datetime.date.fromisoformat(data["latest_date"])
    except (FileNotFoundError, KeyError, ValueError):
        return None

# --- Save Last Notified Date ---
def save_latest_date(new_date):
    """Save the new closest appointment date to file."""
    with open(LATEST_DATE_FILE, "w") as file:
        json.dump({"latest_date": new_date.strftime("%Y-%m-%d")}, file)

# --- Main Logic ---
def check_for_closer_appointment():
    """Check for a closer appointment and send notification if found."""
    appointments = fetch_appointment_data()
    last_notified_date = load_last_notified_date()
    print(f"Last notified date: {last_notified_date}")

    # Get the earliest (closest) appointment date key from the dictionary
    closest_date_str = min(appointments.keys())
    closest_date = datetime.date.fromisoformat(closest_date_str)
  
    print(f"Closest appointment date found: {closest_date}")
    # Only notify if this date is closer than the last notified date
    if last_notified_date is None or closest_date < last_notified_date:
        print(f"New closer appointment found: {closest_date}")
        send_email_notification(closest_date)
        save_latest_date(closest_date)
    elif closest_date > last_notified_date:
        print("Latest date found is later than the last notified date.")
        save_latest_date(closest_date)
    else:
        print("No new closer appointment found.")

if __name__ == "__main__":
    check_for_closer_appointment()
