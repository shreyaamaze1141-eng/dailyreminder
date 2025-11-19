import streamlit as st
import json
from datetime import datetime
from twilio.rest import Client

# -------------------------------------------------------------
# TWILIO DETAILS (REPLACE WITH YOURS)
# -------------------------------------------------------------
TWILIO_ACCOUNT_SID = "AC9b0b3cd58ad339916c3b7e02449eed0b"
TWILIO_AUTH_TOKEN = "8131b7b98e59ce7c08b7685847cc5a50"

# Sandbox WhatsApp number (default Twilio sandbox number)
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"

# Create Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# File to store reminders
FILE_NAME = "whatsapp_reminders.json"

# -------------------------------------------------------------
# Load reminder file
# -------------------------------------------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except:
        return []

# -------------------------------------------------------------
# Save reminder file
# -------------------------------------------------------------
def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:
        json.dump(reminders, f, indent=2)

# -------------------------------------------------------------
# Send WhatsApp message
# -------------------------------------------------------------
def send_whatsapp(to_phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone}"
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)

# -------------------------------------------------------------
# Load reminders into session state
# -------------------------------------------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# Page title
st.title("💬 WhatsApp Reminder App")

st.write("Send scheduled reminders to WhatsApp using Twilio.")

# -------------------------------------------------------------
# Get user input
# -------------------------------------------------------------
reminder_text = st.text_input(
    "Enter reminder message:",
    placeholder="Pick up groceries"
)

phone_number = st.text_input(
    "Enter WhatsApp number (with country code):",
    placeholder="+918888888888"
)

date_sel = st.date_input("Select reminder date")

time_str = st.text_input(
    "Enter time (24H, HH:MM):",
    value="09:00"
)

# -------------------------------------------------------------
# Save reminder
# -------------------------------------------------------------
if st.button("Save Reminder"):
    try:
        user_time = datetime.strptime(time_str, "%H:%M").time()
        send_datetime = datetime.combine(date_sel, user_time)

        st.session_state["reminders"].append({
            "text": reminder_text,
            "phone": phone_number,
            "datetime": send_datetime.strftime("%Y-%m-%d %H:%M")
        })

        save_reminders(st.session_state["reminders"])
        st.success("Reminder saved!")

    except:
        st.error("Invalid time format. Use HH:MM like 14:30")

# -------------------------------------------------------------
# Display saved reminders
# -------------------------------------------------------------
st.subheader("📋 Saved Reminders")

if len(st.session_state["reminders"]) == 0:
    st.info("No reminders yet.")
else:
    for i, r in enumerate(st.session_state["reminders"]):
        st.write(f"**Message:** {r['text']}")
        st.write(f"**To:** {r['phone']}")
        st.write(f"**At:** {r['datetime']}")

        if st.button(f"Send Now #{i}"):
            ok, msg = send_whatsapp(r["phone"], r["text"])
            if ok:
                st.success("WhatsApp message sent!")
            else:
                st.error("Failed: " + str(msg))

        st.write("---")
