from twilio.rest import Client

client = Client("AC9b0b3cd58ad339916c3b7e02449eed0b", "8131b7b98e59ce7c08b7685847cc5a50")

message = client.messages.create(
    body="Test SMS from Twilio",
    from_="+16362095482",   # Twilio number here
    to="+917758887339"     # Your verified number
)

print(message.sid)
