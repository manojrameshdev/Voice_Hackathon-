from twilio.rest import Client
from datetime import datetime

# ===== YOUR TWILIO CREDENTIALS =====
TWILIO_ACCOUNT_SID = "AC5f53cf902cab3585403d9121ea1f4932"
TWILIO_AUTH_TOKEN = "6e7e59714c1cfcbebee8dabb0dd4b7e1"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

def send_whatsapp_alert(guardian_phone, patient_name, medication_name, scheduled_time):
    """Send WhatsApp alert to guardian when medication is missed"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_body = f"""🚨 *MEDICATION ALERT*

Patient: {patient_name}
Medication: {medication_name}
Scheduled Time: {scheduled_time}
Status: ❌ MISSED

This medication was not taken as scheduled. Please check on the patient.

- DoseBuddy Alert System"""

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=f"whatsapp:{guardian_phone}"
        )
        
        print(f"✅ WhatsApp alert sent! Message SID: {message.sid}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")
        return False

def send_low_stock_alert(guardian_phone, patient_name, medication_name, remaining_count):
    """Send WhatsApp alert for low stock"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_body = f"""⚠️ *LOW STOCK ALERT*

Patient: {patient_name}
Medication: {medication_name}
Remaining: {remaining_count} doses

Please refill the medication soon!

- DoseBuddy Alert System"""

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=f"whatsapp:{guardian_phone}"
        )
        
        print(f"✅ Low stock alert sent! Message SID: {message.sid}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")
        return False

def test_whatsapp_connection(guardian_phone):
    """Test WhatsApp connection"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body="✅ DoseBuddy WhatsApp notifications are now active! You will receive alerts when medications are missed or stock is low.",
            to=f"whatsapp:{guardian_phone}"
        )
        
        return True, f"Test message sent successfully! Message SID: {message.sid}"
    
    except Exception as e:
        error_msg = str(e)
        
        if "20003" in error_msg:
            return False, "Authentication failed. Check your Auth Token."
        elif "21608" in error_msg:
            return False, f"Phone number {guardian_phone} not verified. Join WhatsApp sandbox first by sending join code to +14155238886"
        elif "21211" in error_msg:
            return False, f"Invalid phone number: {guardian_phone}. Must include country code (e.g., +919876543210)"
        else:
            return False, f"Error: {error_msg}"

def send_daily_summary(guardian_phone, patient_name, stats):
    """Send daily summary report"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        adherence = stats.get('adherence_rate', 0)
        taken = stats.get('taken', 0)
        missed = stats.get('missed', 0)
        
        emoji = "🌟" if adherence == 100 else "✅" if adherence >= 80 else "⚠️"
        feedback = "Perfect day!" if adherence == 100 else "Good job!" if adherence >= 80 else "Needs improvement"
        
        message_body = f"""📊 *DAILY SUMMARY*

Patient: {patient_name}
Date: {datetime.now().strftime('%B %d, %Y')}

✅ Taken: {taken} dose(s)
❌ Missed: {missed} dose(s)
📈 Adherence: {adherence}%

{emoji} {feedback}

- DoseBuddy Daily Report"""

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=f"whatsapp:{guardian_phone}"
        )
        
        print(f"✅ Daily summary sent! Message SID: {message.sid}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending daily summary: {e}")
        return False
