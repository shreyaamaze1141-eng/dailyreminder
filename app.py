# ===============================
# SIMPLE STREAMLIT REMINDER APP
# MADE LIKE A 5TH CLASS STUDENT
# WITH COMMENTS ON EVERY LINE
# ===============================

import streamlit as st               # Streamlit for our website
from twilio.rest import Client       # Twilio for sending SMS
import json                          # To save reminders in a file
import os                            # To talk to computer system
from datetime import datetime, date, time  # To work with dates and time

# -------------------------------
# FILE NAME WHERE WE SAVE DATA
# -------------------------------
DATA_FILE = "reminders.json"

# -------------------------------
# GET TWILIO INFORMATION
# (TAKEN FROM SYSTEM ENVIRONMENT)
# -------------------------------
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")        # Twilio account SID
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")       # Twilio auth token
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")       # Twilio phone number

# -------------------------------
# CREATE TWILIO CLIENT IF POSSIBLE
# -------------------------------
def get_twilio_client():
    # If any Twilio detail missing, return None
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_FROM:
        return None
    # Otherwise return working client
    return Client(TWILIO_SID, TWILIO_TOKEN)

# -------------------------------
# LOAD REMINDERS FROM FILE
# -------------------------------
def load_data():
    # If file does not exist, return empty list
    if not os.path.exists(DATA_FILE):
        return []

    # Read JSON file safely
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# -------------------------------
# SAVE REMINDERS TO FILE
# -------------------------------
def save_data(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

# -------------------------------
# SEND SMS USING TWILIO
# -------------------------------
def send_sms(phone, message):
    client = get_twilio_client()          # Get Twilio client

    if client is None:
        return False, "Missing Twilio details."

    try:
        # Try sending SMS
        msg = client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=phone
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)

# ======================================================
# STREAMLIT UI - OUR SIMPLE WEBPAGE
# ======================================================
st.set_page_config(
    page_title="Simple Reminder",
    layout="centered"
)

# Title on top
st.title("📱 Super Simple SMS Reminder App")

st.write("This app sends reminders as SMS using Twilio.")

# ------------------------------------------------------
# LOAD EXISTING REMINDERS
# ------------------------------------------------------
reminders = load_data()

# ------------------------------------------------------
# FORM TO ADD A NEW REMINDER
# ------------------------------------------------------
st.header("Add a new reminder")

# User enters message text
message = st.text_input(
    "What should we remind you?",
    value="Drink water"
)

# User enters phone number
phone = st.text_input(
    "Phone number (example: +919999888877)",
    value=""
)

# User chooses date
r_date = st.date_input(
    "Choose a date",
    value=date.today()
)

# User chooses time
r_time = st.time_input(
    "Choose a time",
    value=datetime.now().time().replace(second=0, microsecond=0)
)

# User presses button to save reminder
if st.button("Save Reminder"):
    # Convert chosen date & time into a single datetime
    reminder_dt = datetime.combine(r_date, r_time)

    # Make a reminder dictionary to store
    reminders.append({
        "message": message,
        "phone": phone,
        "time": reminder_dt.isoformat(),
        "sent": False
    })

    # Save to file
    save_data(reminders)

    # Tell user it's saved
    st.success("🎉 Reminder saved!")

    # Refresh page so new reminder shows up
    st.rerun()

# ------------------------------------------------------
# CHECK IF ANY REMINDER TIME HAS COME
# ------------------------------------------------------
now = datetime.now()  # current time

for reminder in reminders:
    # Only check reminders not sent yet
    if not reminder.get("sent", False):
        # Convert saved time string to datetime
        r_time = datetime.fromisoformat(reminder["time"])

        # If current time is past reminder time
        if now >= r_time:
            # Try sending SMS
            ok, info = send_sms(
                reminder["phone"],
                reminder["message"]
            )

            if ok:
                # Mark as sent
                reminder["sent"] = True
                save_data(reminders)
                st.success(f"SMS sent: {reminder['message']}")
            else:
                st.error("SMS sending failed: " + info)

# ------------------------------------------------------
# SHOW ALL REMINDERS ON SCREEN
# ------------------------------------------------------
st.header("All reminders")

if len(reminders) == 0:
    st.info("No reminders yet.")
else:
    for r in reminders:
        st.write("Message:", r["message"])
        st.write("Phone:", r["phone"])
        st.write("Time:", r["time"])
        st.write("Sent:", "Yes" if r["sent"] else "No")
        st.write("---")
