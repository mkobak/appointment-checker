from dotenv import load_dotenv
import os
import requests
import datetime
import time
import ctypes

# Load environment variables from .env file
load_dotenv()

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

# Define the threshold date for appointments
THRESHOLD_DATE = (datetime.date.today() + datetime.timedelta(days=90))
CHECK_INTERVAL = 0.5 * 60 * 60  # Check every 6 hours

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


# Function to check for closer appointments
def check_for_closer_appointments():
    data = fetch_appointments()

    for date in data.items():
        date_str = date[0] # Extract the date string from the tuple
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() # Convert to date object
        print(f"Checking appointment date: {date}")
        # Check if the date is before the threshold date
        if date < THRESHOLD_DATE:
            print(f"Closer appointment found: {date}")
            send_simple_message(date)
            return
    print("No closer appointments found.")

if __name__ == "__main__":
    while True:
        check_for_closer_appointments()
        time.sleep(CHECK_INTERVAL)