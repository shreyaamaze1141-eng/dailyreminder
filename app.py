"""
Streamlit Daily-Chore Reminder + Twilio SMS (single-file)

How to run:
1. Install requirements.
2. Set env vars TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
   (or create a .env file in same folder for local testing).
3. streamlit run app.py
"""

import os
import json
from datetime import datetime, date, time, timedelta
import threading
import uuid
import pytz

import streamlit as st
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

# --- Config / constants ---
JOBS_FILE = "reminder_jobs.json"
LOCAL_TZ = pytz.timezone("Asia/Kolkata")  # change if you want another timezone

# Twilio credentials from env
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")  # e.g. +1234567890

# Create Twilio client lazily (so app loads even without creds for preview)
def get_twilio_client():
    if not TWILIO_SID or not TWILIO_TOKEN:
        return None
    return Client(TWILIO_SID, TWILIO_TOKEN)

# --- Scheduler setup ---
scheduler = BackgroundScheduler()
scheduler.start()

# Lock to prevent simultaneous file writes
file_lock = threading.Lock()

# --- Persistence helpers ---
def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return {}
    with file_lock:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    return data

def save_jobs(jobs_dict):
    with file_lock:
        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs_dict, f, indent=2, default=str)

# --- SMS sending function ---
def send_sms_via_twilio(reminder):
    """
    reminder: dict containing keys: id, phone, text, repeat_daily(bool)
    """
    client = get_twilio_client()
    if client is None:
        print("Twilio credentials not set. Skipping send. Reminder:", reminder)
        return False, "Twilio credentials not configured."

    to_number = reminder.get("phone")
    body = reminder.get("text")

    try:
        msg = client.messages.create(
            body=body,
            from_=TWILIO_FROM,
            to=to_number
        )
        print(f"Sent SMS for reminder {reminder.get('id')} -> sid {msg.sid}")
        return True, msg.sid
    except Exception as e:
        print("Twilio send error:", e)
        return False, str(e)

# --- Job scheduling helpers ---
def schedule_reminder_job(reminder):
    """
    Schedule a job for the reminder. If repeat_daily, schedule a daily job.
    reminder dict must include: id, run_at (ISO str), repeat_daily (bool), phone, text
    """
    job_id = reminder["id"]

    # Remove existing job with same id (if exists)
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    # parse run_at to datetime
    run_at = datetime.fromisoformat(reminder["run_at"])
    run_at = run_at.astimezone(LOCAL_TZ)

    def job_func(r=reminder):
        success, info = send_sms_via_twilio(r)
        # update last_sent in persisted jobs
        jobs = load_jobs()
        if r["id"] in jobs:
            jobs[r["id"]]["last_sent"] = datetime.now(LOCAL_TZ).isoformat()
            save_jobs(jobs)
        # if not repeating, remove the job & persisted reminder
        if not r.get("repeat_daily", False):
            try:
                scheduler.remove_job(r["id"])
            except Exception:
                pass
            jobs = load_jobs()
            if r["id"] in jobs:
                jobs.pop(r["id"])
                save_jobs(jobs)

    if reminder.get("repeat_daily", False):
        # schedule first run at run_at, then every day
        scheduler.add_job(
            job_func,
            'cron',
            id=job_id,
            hour=run_at.hour,
            minute=run_at.minute,
            second=run_at.second,
            timezone=LOCAL_TZ
        )
    else:
        # one-off run
        scheduler.add_job(job_func, 'date', run_date=run_at, id=job_id, timezone=LOCAL_TZ)

# On startup, read jobs.json and reschedule pending jobs
def reschedule_all_on_startup():
    jobs = load_jobs()
    now = datetime.now(LOCAL_TZ)
    for rid, j in jobs.items():
        # If non-repeating one-off and time already passed, skip
        try:
            run_at = datetime.fromisoformat(j["run_at"]).astimezone(LOCAL_TZ)
        except Exception:
            continue
        if not j.get("repeat_daily", False) and run_at < now:
            # remove outdated one-off
            continue
        # schedule
        schedule_reminder_job(j)

# Call at module load
reschedule_all_on_startup()

# --- Streamlit UI ---
st.set_page_config(page_title="Chore Reminders (SMS)", layout="centered")
st.title("Daily Chore Reminders — send SMS with Twilio")

st.markdown(
    """
Enter a chore reminder, the phone number to send to, and choose time.
- Uses Twilio to send SMS.
- Reminders persist to `reminder_jobs.json`.
- Repeating daily reminders run every day at the chosen time.
"""
)

with st.form("add_reminder", clear_on_submit=True):
    col1, col2 = st.columns([2,1])
    with col1:
        text = st.text_area("Reminder text (what to do)", value="Water the plants", height=60)
    with col2:
        to_phone = st.text_input("Phone number (E.164, e.g. +919876543210)", value="")
        d = st.date_input("Date", value=date.today())
        t = st.time_input("Time", value=(datetime.now().time().replace(second=0, microsecond=0)))
        repeat_daily = st.checkbox("Repeat daily at this time?", value=True)
    submitted = st.form_submit_button("Schedule reminder")
    if submitted:
        # Validate phone naive
        if not to_phone.strip():
            st.error("Please enter a phone number.")
        elif not text.strip():
            st.error("Reminder text cannot be empty.")
        else:
            # combine date and time in local tz
            dt = datetime.combine(d, t)
            dt_local = LOCAL_TZ.localize(dt)
            reminder_id = str(uuid.uuid4())
            reminder = {
                "id": reminder_id,
                "text": text.strip(),
                "phone": to_phone.strip(),
                "run_at": dt_local.isoformat(),
                "repeat_daily": bool(repeat_daily),
                "created_at": datetime.now(LOCAL_TZ).isoformat(),
                "last_sent": None
            }
            jobs = load_jobs()
            jobs[reminder_id] = reminder
            save_jobs(jobs)
            schedule_reminder_job(reminder)
            st.success(f"Scheduled reminder for {dt_local.strftime('%Y-%m-%d %H:%M:%S %Z')} (id {reminder_id})")
            st.experimental_rerun()

st.markdown("---")

# Show current reminders
jobs = load_jobs()
if not jobs:
    st.info("No reminders scheduled yet.")
else:
    st.subheader("Scheduled reminders")
    rows = []
    for rid, r in sorted(jobs.items(), key=lambda kv: kv[1]["run_at"]):
        run_at = datetime.fromisoformat(r["run_at"]).astimezone(LOCAL_TZ)
        rows.append((rid, r["text"], r["phone"], r["repeat_daily"], run_at, r.get("last_sent")))

    for rid, text_val, phone, repeat, run_at, last_sent in rows:
        st.markdown(f"**{text_val}** — to `{phone}`")
        st.write(f"- Time: {run_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        st.write(f"- Repeat daily: {'Yes' if repeat else 'No'}")
        st.write(f"- Last sent: {last_sent if last_sent else 'Never'}")
        col_a, col_b, col_c = st.columns([1,1,2])
        if col_a.button("Send now", key=f"now_{rid}"):
            # immediate send (not changing scheduled run)
            success, info = send_sms_via_twilio(jobs[rid])
            if success:
                jobs = load_jobs()
                jobs[rid]["last_sent"] = datetime.now(LOCAL_TZ).isoformat()
                save_jobs(jobs)
                st.success("Sent now. SID: " + str(info))
            else:
                st.error("Send failed: " + str(info))
            st.experimental_rerun()
        if col_b.button("Delete", key=f"del_{rid}"):
            # remove job from scheduler and persisted file
            try:
                scheduler.remove_job(rid)
            except Exception:
                pass
            jobs = load_jobs()
            if rid in jobs:
                jobs.pop(rid)
                save_jobs(jobs)
            st.warning("Deleted reminder.")
            st.experimental_rerun()
        # spacer
        st.write("")

st.markdown("---")
st.subheader("Twilio status / Debug")
if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_FROM:
    st.warning("Twilio credentials are not set. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER in environment.")
else:
    st.success("Twilio credentials found (will attempt to send).")

st.caption("App stores reminders in `reminder_jobs.json` in the app folder. For reliable production use, run scheduler as a separate worker or use a more durable job queue.")
