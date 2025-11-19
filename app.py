import streamlit as st
from twilio.rest import Client
import json
import datetime
import time
import threading

REMINDER_FILE = "reminders.json"


# -------------------------------
# SAVE & LOAD REMINDERS
# -------------------------------
def load_reminders():
    try:
        with open(REMINDER_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=4)


# -------------------------------
# SEND MESSAGE (SMS / WhatsApp)
# -------------------------------
def send_message(text, client, from_number, to_number):
    try:
        message = client.messages.create(
            body=text,
            from_=from_number,
            to=to_number
        )
        print("Message sent:", message.sid)
    except Exception as e:
        print("Sending failed:", e)


# -------------------------------
# BACKGROUND SCHEDULER LOOP
# -------------------------------
def scheduler_loop():
    while True:

        if all(k in st.session_state for k in ("sid", "token", "from", "to")):

            client = Client(st.session_state.sid, st.session_state.token)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            reminders = load_reminders()
            updated = False

            for r in reminders:
                # Check if time AND date match and message not already sent
                if r["datetime"] == now and not r.get("sent", False):
                    send_message(
                        f"⏰ Reminder: {r['text']}",
                        client,
                        st.session_state["from"],
                        st.session_state["to"]
                    )
                    r["sent"] = True
                    updated = True

            if updated:
                save_reminders(reminders)

        time.sleep(60)  # Check once every minute


# Start scheduler once
if "scheduler_started" not in st.session_state:
    threading.Thread(target=scheduler_loop, daemon=True).start()
    st.session_state.scheduler_started = True


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="Daily SMS Reminder", layout="centered")
st.title("📅 SMS Reminder App")


# --------------------------------
# Twilio Credentials Input
# --------------------------------
st.subheader("🔐 Enter Twilio Credentials")

sid = st.text_input("Twilio ACCOUNT SID")
token = st.text_input("Twilio AUTH TOKEN", type="password")

from_number = st.text_input(
    "Twilio From Number",
    placeholder="whatsapp:+14155238886 or +1234567890"
)

to_number = st.text_input(
    "Your Number",
    placeholder="whatsapp:+91XXXXXXXXXX or +91XXXXXXXXXX"
)

if st.button("Save Twilio Settings"):
    if sid and token and from_number and to_number:
        st.session_state.sid = sid
        st.session_state.token = token
        st.session_state["from"] = from_number
        st.session_state["to"] = to_number
        st.success("Twilio settings saved!")
    else:
        st.error("Please fill all fields.")


if not all(k in st.session_state for k in ("sid", "token", "from", "to")):
    st.warning("Enter Twilio settings above to continue.")
    st.stop()


# -------------------------------
# REMINDER FORM
# -------------------------------
st.subheader("⏰ Add a Reminder")

reminders = load_reminders()

reminder_text = st.text_input("Reminder Text")

reminder_date = st.date_input("Pick a Date", datetime.date.today())
reminder_time = st.time_input("Pick Time", datetime.time(9, 0))

if st.button("Save Reminder"):
    reminder_datetime = datetime.datetime.combine(reminder_date, reminder_time)
    reminders.append({
        "text": reminder_text,
        "datetime": reminder_datetime.strftime("%Y-%m-%d %H:%M"),
        "sent": False
    })
    save_reminders(reminders)
    st.success("Reminder saved!")


# -------------------------------
# SHOW REMINDERS
# -------------------------------
st.subheader("📋 Saved Reminders")

if len(reminders) == 0:
    st.info("No reminders yet.")
else:
    for r in reminders:
        st.write(f"- **{r['text']}** at `{r['datetime']}`")

if st.button("Clear All Reminders"):
    save_reminders([])
    st.warning("All reminders deleted.")
