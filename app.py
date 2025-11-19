import streamlit as st                # This imports Streamlit so we can make a web app
from twilio.rest import Client        # This imports Twilio for sending SMS
from datetime import datetime, timedelta # This helps with date and time
import threading                      # This helps us wait and send SMS later

# Turn off dark mode by setting a light theme in Streamlit

st.set_page_config(page_title="Simple SMS Reminder", layout="centered")

# Make the title of the app

st.title("🕒 Simple SMS Reminder App")

# Ask the user to enter Twilio details

st.subheader("Enter Twilio Details")
sid = st.text_input("Twilio Account SID")   # Where user types the SID
token = st.text_input("Twilio Auth Token")  # Where user types the token
from_number = st.text_input("Twilio From Number")  # Number to send SMS from

# Divider line

st.markdown("---")

# Ask the user to enter reminder information

st.subheader("Set Reminder")

phone = st.text_input("Phone Number to Send SMS (Example: +919876543210)")  # Phone number
message = st.text_area("Reminder Message")                                  # Reminder text
reminder_date = st.date_input("Select Date")                                # Date of reminder
reminder_time = st.time_input("Select Time")                                # Time of reminder

# Function to send SMS

def send_sms():
client = Client(sid, token)                      # This creates a Twilio client
client.messages.create(                          # This sends the SMS
body=message,                                # SMS text
from_=from_number,                           # The Twilio number
to=phone                                     # Number to send to
)
st.success("Message Sent!")                      # Show a success message

# Function to calculate how many seconds to wait

def schedule_sms():
trigger_datetime = datetime.combine(reminder_date, reminder_time)   # Combine date + time
current_datetime = datetime.now()                                   # Get current datetime
delay = (trigger_datetime - current_datetime).total_seconds()       # How long to wait

```
if delay < 0:                                                       # If time already gone
    st.error("Selected time already passed!")                       # Show error
    return

timer = threading.Timer(delay, send_sms)                           # Wait until time
timer.start()                                                      # Start waiting
```

# Button to schedule the reminder

if st.button("Schedule Reminder"):
if not sid or not token or not from_number:                       # Check Twilio details entered
st.error("Please fill all Twilio details!")
elif not message or not phone:                                    # Check reminder details
st.error("Please enter message and phone number!")
else:
schedule_sms()                                                # Call function to schedule
st.success("Reminder Scheduled!")
