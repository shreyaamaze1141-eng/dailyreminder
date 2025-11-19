# Import required libraries
import streamlit as st            # Streamlit for web app UI
from twilio.rest import Client    # Twilio for sending SMS
from datetime import datetime, date, time   # For date & time handling

# Set Streamlit page configuration
st.set_page_config(
    page_title="Daily SMS Reminder",   # Title shown in browser tab
    layout="centered"                  # Center page layout
)

# ----------------------------------------------------
# Initialize session state to store reminders
# ----------------------------------------------------
if "reminders" not in st.session_state:            # Check if reminders list exists
    st.session_state["reminders"] = []             # Create empty list for reminders

# ----------------------------------------------------
# Input section where user enters the data
# ----------------------------------------------------
st.title("📱 Daily SMS Reminder")                  # Main app title

task_text = st.text_input(                         # Input box for reminder text
    "Reminder Text"
)

task_date = st.date_input(                         # Date picker
    "Select Date",
    date.today()                                   # Default is today's date
)

task_time = st.time_input(                         # Time picker
    "Select Time (HH:MM)",
    datetime.now().time()                          # Default is current time
)

phone_number = st.text_input(                      # Phone number to send SMS
    "Send To Mobile Number (+91XXXXXXXXXX)"
)

twilio_sid = st.text_input(                        # Twilio SID input
    "Twilio Account SID",
    type="password"                                # Hide input for safety
)

twilio_auth = st.text_input(                       # Twilio Auth Token input
    "Twilio Auth Token",
    type="password"                                # Hidden input
)

twilio_from = st.text_input(                       # Twilio Sender number
    "Twilio From Number (+1XXXXXXXXXX)"
)

# ----------------------------------------------------
# Save reminder into session
# ----------------------------------------------------
if st.button("Save Reminder"):                     # Button clicked to save reminder
    reminder_dt = datetime.combine(                # Combine date and time to one datetime
        task_date, task_time
    )

    st.session_state["reminders"].append({         # Add new reminder to session list
        "text": task_text,                         # Save reminder text
        "datetime": reminder_dt.strftime("%Y-%m-%d %H:%M"),  # Save date and time formatted
        "phone": phone_number                      # Save target phone number
    })

    st.success("Reminder saved successfully!")     # Show success message

# ----------------------------------------------------
# Display saved reminders to user
# ----------------------------------------------------
st.subheader("📋 Saved Reminders")                 # Section heading

if len(st.session_state["reminders"]) > 0:         # Check if reminders exist
    for r in st.session_state["reminders"]:        # Loop through reminders
        text = r.get("text", "No Text")            # Fetch reminder text safely
        dt = r.get("datetime", "No Time")          # Fetch date/time safely
        phone = r.get("phone", "Unknown")          # Fetch phone safely

        st.write(                                   # Display reminder in formatted line
            f"- **{text}** at `{dt}` → 📱 {phone}"
        )
else:
    st.write("No reminders saved yet.")             # If no reminders exist, say so

# ----------------------------------------------------
# Button to manually trigger SMS sending
# ----------------------------------------------------
if st.button("Send Test SMS Now"):                  # When button is clicked
    if not all([twilio_sid, twilio_auth, twilio_from, phone_number]):
        st.error("Missing Twilio details or phone number!")  # Show error if required fields missing
    else:
        try:
            client = Client(twilio_sid, twilio_auth)          # Initialize Twilio client

            msg = client.messages.create(                     # Send SMS
                body=f"Test message: {task_text}",            # Message content
                from_=twilio_from,                            # Twilio sender number
                to=phone_number                               # Target user number
            )

            st.success("SMS sent successfully!")              # Display success
        except Exception as e:
            st.error(f"SMS sending failed: {e}")              # Show error in case of failure
