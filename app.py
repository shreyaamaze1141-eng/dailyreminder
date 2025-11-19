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

# SEND WHATSAPP MESSAGE

# -------------------------------

def send_whatsapp_message(text, client, from_number, to_number):
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

# BACKGROUND SCHEDULER

# -------------------------------

def scheduler_loop():
while True:
# Only run scheduler if Twilio details exist
if all(k in st.session_state for k in ("sid", "token", "from", "to")):

```
        client = Client(st.session_state.sid, st.session_state.token)
        now = datetime.datetime.now().strftime("%H:%M")

        reminders = load_reminders()
        updated = False

        for r in reminders:
            if r["time"] == now and not r.get("sent", False):
                send_whatsapp_message(
                    f"⏰ Reminder: {r['text']}",
                    client,
                    st.session_state["from"],
                    st.session_state["to"]
                )
                r["sent"] = True
                updated = True

        if updated:
            save_reminders(reminders)

    time.sleep(60)
```

# Start scheduler once

if "scheduler_started" not in st.session_state:
threading.Thread(target=scheduler_loop, daemon=True).start()
st.session_state.scheduler_started = True

# -------------------------------

# STREAMLIT UI

# -------------------------------

st.set_page_config(page_title="Daily WhatsApp Reminder", layout="centered")
st.title("🕑 Daily WhatsApp Reminder")

st.subheader("🔐 Enter Twilio Credentials")

# Twilio inputs

sid = st.text_input("Twilio ACCOUNT SID", type="default")
token = st.text_input("Twilio AUTH TOKEN", type="password")

from_whatsapp = st.text_input(
"WhatsApp FROM number (Twilio Sandbox)",
placeholder="whatsapp:+14155238886"
)

to_whatsapp = st.text_input(
"Your WhatsApp number",
placeholder="whatsapp:+91XXXXXXXXXX"
)

# Save inputs in memory

if st.button("Save Twilio Settings"):
if sid and token and from_whatsapp and to_whatsapp:
st.session_state.sid = sid
st.session_state.token = token
st.session_state["from"] = from_whatsapp
st.session_state["to"] = to_whatsapp
st.success("Twilio settings saved.")
else:
st.error("Please fill all fields.")

# Check if credentials exist before showing reminder area

if not all(k in st.session_state for k in ("sid", "token", "from", "to")):
st.warning("Enter Twilio details first.")
st.stop()

# -------------------------------

# REMINDER FORM

# -------------------------------

st.subheader("➕ Add New Reminder")

reminders = load_reminders()

reminder_text = st.text_input("Reminder Text")
reminder_time = st.time_input("Time", datetime.time(9, 0))

if st.button("Save Reminder"):
reminders.append({
"text": reminder_text,
"time": reminder_time.strftime("%H:%M"),
"sent": False
})
save_reminders(reminders)
st.success("Reminder saved successfully!")

# -------------------------------

# SHOW REMINDERS

# -------------------------------

st.subheader("📋 Saved Reminders")
if len(reminders) == 0:
st.info("No reminders yet.")
else:
for r in reminders:
st.write(f"- {r['text']} at **{r['time']}**")

if st.button("Clear All Reminders"):
save_reminders([])
st.warning("All reminders deleted.")
