import sqlite3

def get_ai_response(user_question, user_medications=""):
    """AI response function"""
    return """⚠️ **AI Assistant Feature**

The AI Assistant is currently disabled.

**All other DoseBuddy features work perfectly:**
✅ Medication Tracking
✅ Reminders & Notifications  
✅ Beautiful 3D Analytics Charts
✅ Prescription Storage
✅ Low Stock Alerts

**To enable AI:**
1. Visit: https://aistudio.google.com/app/apikey
2. Get FREE Google Gemini API key
3. Update ai_assistant.py with the key

For medication information, consult your pharmacist or search online."""

def get_medication_list_for_ai():
    """Get formatted medication list"""
    try:
        conn = sqlite3.connect('data/dosebuddy.db')
        cursor = conn.execute('SELECT name, dosage, frequency FROM medications')
        meds = cursor.fetchall()
        conn.close()
        
        if not meds:
            return "No medications currently tracked"
        
        med_list = []
        for med in meds:
            med_list.append(f"{med[0]} ({med[1]}, {med[2]}x daily)")
        
        return ", ".join(med_list)
    except:
        return "No medications currently tracked"
