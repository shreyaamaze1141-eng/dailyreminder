import streamlit as st
from twilio.rest import Client
from datetime import datetime, time
import threading

# Turn off dark mode by using light theme
st.set_page_config(page_title="Daily Reminder", layout="centered")

# Title
st.title("🕒 Daily Reminder App")

# Twilio details
st.subheader("Enter Twilio Details")
sid = st.text_input("Twilio Account SID")
token = st.text_input("Twilio Auth Token")
from_number = st.text_input("Twilio From Number")

st.markdown("---")

# Reminder settings
st.subheader("Set Reminder")

phone = st.text_input("Phone Number (Example: +919876543210)")
message = st.text_area("Reminder Message")
reminder_date = st.date_input("Select Date")

st.write("Select Time")
hour = st.selectbox("Hour (0–23)", list(range(24)))
minute = st.selectbox("Minute (0–59)", list(range(60)))

# Function to send SMS
def send_sms():
    client = Client(sid, token)
    client.messages.create(
        body=message,
        from_=from_number,
        to=phone
    )
    st.success("Message Sent!")

# Function to schedule message
def schedule_sms():
    reminder_time = time(hour, minute)
    trigger_datetime = datetime.combine(reminder_date, reminder_time)
    now = datetime.now()
    delay = (trigger_datetime - now).total_seconds()

    if delay < 0:
        st.error("Selected time already passed!")
        return

    timer = threading.Timer(delay, send_sms)
    timer.start()

if st.button("Schedule Reminder"):
    if not sid or not token or not from_number:
        st.error("Please fill Twilio details!")
    elif not phone or not message:
        st.error("Please enter message and phone number!")
    else:
        schedule_sms()
        st.success("Reminder Scheduled!")
