# -------------------------------------------------------------
# Daily SMS Reminder App (Very Simple, Explained Line by Line)
# -------------------------------------------------------------

# We import things we need
import streamlit as st              # For making the web app
import json                         # To save and load reminders
from datetime import datetime       # To handle date and time
from twilio.rest import Client      # To send SMS using Twilio

# -------------------------------------------------------------
# HARD CODE TWILIO DETAILS HERE (Replace with your own)
# -------------------------------------------------------------
TWILIO_ACCOUNT_SID = "AC9b0b3cd58ad339916c3b7e02449eed0b"
TWILIO_AUTH_TOKEN  = "8131b7b98e59ce7c08b7685847cc5a50"
TWILIO_FROM_NUMBER = "+16362095482"      # This MUST be your Twilio phone number

# -------------------------------------------------------------
# Make a Twilio client using the above details
# -------------------------------------------------------------
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# -------------------------------------------------------------
# File where reminders will be stored
# -------------------------------------------------------------
FILE_NAME = "reminders.json"

# -------------------------------------------------------------
# Function to load saved reminders from the file
# -------------------------------------------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:     # Open file to read
            return json.load(f)             # Return stored reminders
    except:
        return []                           # Return empty if file missing

# -------------------------------------------------------------
# Function to save reminders back to the file
# -------------------------------------------------------------
def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:         # Open file to write
        json.dump(reminders, f, indent=2)   # Save pretty JSON

# -------------------------------------------------------------
# Function that sends SMS using Twilio
# -------------------------------------------------------------
def send_sms(phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=phone
        )
        return True, msg.sid               # Return success
    except Exception as e:
        return False, str(e)              # Return error message

# -------------------------------------------------------------
# Load previously saved reminders into memory
# -------------------------------------------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# -------------------------------------------------------------
# Set layout and heading
# -------------------------------------------------------------
st.set_page_config(page_title="SMS Reminder App", layout="centered")
st.title("📱 Simple Daily Reminder App")

st.write("This app lets you schedule an SMS reminder to any phone number.")

# -------------------------------------------------------------
# ASK USER TO ENTER REMINDER DETAILS
# -------------------------------------------------------------
reminder_text = st.text_input(
    "Write what message you want to send:",
    placeholder="Example: Water the plants"
)

phone_number = st.text_input(
    "Enter phone number (with +country code):",
    placeholder="+917758887339"
)

date_sel = st.date_input("Pick a date for sending the SMS")

time_str = st.text_input(
    "Enter time in 24-hour format (HH:MM):",
    value="09:00"
)

# -------------------------------------------------------------
# When user clicks the button, store the reminder
# -------------------------------------------------------------
if st.button("Save Reminder"):
    try:
        # Convert typed HH:MM into Python time
        user_time = datetime.strptime(time_str, "%H:%M").time()

        # Combine date + time into one datetime
        combined_dt = datetime.combine(date_sel, user_time)

        # Store reminder
        st.session_state["reminders"].append({
            "text": reminder_text,
            "phone": phone_number,
            "datetime": combined_dt.strftime("%Y-%m-%d %H:%M")
        })

        # Save to file
        save_reminders(st.session_state["reminders"])

        st.success("Reminder saved!")

    except:
        st.error("Time format wrong! Please use HH:MM (example: 09:30)")

# -------------------------------------------------------------
# Show list of saved reminders
# -------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Saved Reminders")

if len(st.session_state["reminders"]) == 0:
    st.info("No reminders saved yet.")
else:
    for i, r in enumerate(st.session_state["reminders"]):
        st.write(f"**Message:** {r['text']}")
        st.write(f"**Phone:** {r['phone']}")
        st.write(f"**Send At:** {r['datetime']}")

        # Button to send now
        if st.button(f"Send Now #{i}"):
            ok, msg = send_sms(r["phone"], r["text"])
            if ok:
                st.success("SMS sent successfully!")
            else:
                st.error("SMS NOT sent: " + str(msg))

        st.write("---")
