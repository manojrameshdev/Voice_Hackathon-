import schedule
import time
from threading import Thread
from plyer import notification
import sqlite3
from datetime import datetime, timedelta


def send_notification(med_name, dosage):
    """Send desktop notification for DoseBuddy"""
    try:
        notification.notify(
            title=f"💊 DoseBuddy Reminder: {med_name}",
            message=f"Time to take {dosage}\nPlease confirm in the app!",
            timeout=15,
            app_name="DoseBuddy",
            app_icon=None
        )
        print(f"✅ Notification sent: {med_name} at {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        print(f"❌ Notification error: {e}")


def check_missed_medications():
    """Check for missed medications and send INSTANT WhatsApp alerts after 1 minute"""
    try:
        from database import get_guardian_info, get_medication_by_id, log_medication_taken, check_medication_status
        
        conn = sqlite3.connect('data/dosebuddy.db')
        cursor = conn.execute('SELECT id, name, dosage, times FROM medications')
        medications = cursor.fetchall()
        conn.close()
        
        # Get guardian info
        guardian = get_guardian_info()
        if not guardian or guardian[4] != 1:  # whatsapp_enabled check
            return
        
        guardian_phone = guardian[3]
        patient_name = guardian[1]
        
        current_time = datetime.now()
        current_date = current_time.strftime("%Y-%m-%d")
        
        for med in medications:
            med_id, med_name, med_dosage, times_str = med
            times_list = times_str.split(',')
            
            for scheduled_time in times_list:
                scheduled_time = scheduled_time.strip()
                
                try:
                    scheduled_dt = datetime.strptime(f"{current_date} {scheduled_time}", "%Y-%m-%d %H:%M")
                except:
                    continue
                
                # Calculate time difference in minutes
                time_diff = (current_time - scheduled_dt).total_seconds() / 60
                
                # ⚡⚡⚡ SUPER FAST: Send alert after just 1 MINUTE!
                if 1 <= time_diff <= 1.5:  # Between 1-1.5 mins late
                    status = check_medication_status(med_id, scheduled_time, current_date)
                    
                    if status != 'Taken':
                        # Mark as missed
                        if status is None:
                            log_medication_taken(med_id, scheduled_time, "Missed")
                            print(f"⚠️ Medication marked as missed: {med_name} at {scheduled_time}")
                        
                        # Send INSTANT WhatsApp alert
                        try:
                            from whatsapp_notifier import send_whatsapp_alert
                            
                            send_whatsapp_alert(
                                guardian_phone=guardian_phone,
                                patient_name=patient_name,
                                medication_name=f"{med_name} ({med_dosage})",
                                scheduled_time=format_time_12hr(scheduled_time)
                            )
                            print(f"📱⚡ INSTANT WhatsApp alert sent (1 min) for: {med_name}")
                        except ImportError:
                            print("⚠️ WhatsApp notifier not configured")
                        except Exception as e:
                            print(f"❌ WhatsApp alert error: {e}")
    
    except Exception as e:
        print(f"❌ Error checking missed medications: {e}")


def check_low_stock_medications():
    """Check for low stock and send alerts"""
    try:
        from database import get_guardian_info, get_low_stock_medications
        
        guardian = get_guardian_info()
        if not guardian or guardian[4] != 1:
            return
        
        guardian_phone = guardian[3]
        patient_name = guardian[1]
        
        low_stock_meds = get_low_stock_medications(threshold=10)
        
        if low_stock_meds:
            for med in low_stock_meds:
                conn = sqlite3.connect('data/dosebuddy.db')
                cursor = conn.execute('''
                    SELECT id FROM low_stock_alerts 
                    WHERE medication_id = ? AND alert_date = ?
                ''', (med[0], datetime.now().strftime('%Y-%m-%d')))
                
                already_alerted = cursor.fetchone()
                conn.close()
                
                if not already_alerted and med[6] <= 5:
                    try:
                        from whatsapp_notifier import send_low_stock_alert
                        
                        send_low_stock_alert(
                            guardian_phone=guardian_phone,
                            patient_name=patient_name,
                            medication_name=f"{med[1]} ({med[2]})",
                            remaining_count=med[6]
                        )
                        
                        conn = sqlite3.connect('data/dosebuddy.db')
                        
                        conn.execute('''
                            CREATE TABLE IF NOT EXISTS low_stock_alerts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                medication_id INTEGER,
                                alert_date TEXT
                            )
                        ''')
                        
                        conn.execute('''
                            INSERT INTO low_stock_alerts (medication_id, alert_date)
                            VALUES (?, ?)
                        ''', (med[0], datetime.now().strftime('%Y-%m-%d')))
                        
                        conn.commit()
                        conn.close()
                        
                        print(f"📱 Low stock alert sent for: {med[1]}")
                    except ImportError:
                        print("⚠️ WhatsApp notifier not configured")
                    except Exception as e:
                        print(f"❌ Low stock alert error: {e}")
    
    except Exception as e:
        print(f"❌ Error checking low stock: {e}")


def format_time_12hr(time_str):
    """Convert 24-hour time to 12-hour format"""
    try:
        hour, minute = time_str.strip().split(':')
        hour = int(hour)
        period = "AM" if hour < 12 else "PM"
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour = hour - 12
        return f"{hour}:{minute} {period}"
    except:
        return time_str


def schedule_medication(med_id, med_name, dosage, times):
    """Schedule medication reminders"""
    times_list = times.split(',')
    
    for time_str in times_list:
        time_str = time_str.strip()
        try:
            schedule.every().day.at(time_str).do(
                send_notification, med_name, dosage
            )
            print(f"✅ Scheduled: {med_name} at {time_str}")
        except Exception as e:
            print(f"❌ Error scheduling {med_name} at {time_str}: {e}")


def daily_summary():
    """Send daily summary at end of day"""
    try:
        from database import get_guardian_info, get_adherence_statistics
        
        guardian = get_guardian_info()
        if not guardian or guardian[4] != 1:
            return
        
        stats = get_adherence_statistics(days=1)
        
        if stats['total_doses'] > 0:
            try:
                from whatsapp_notifier import send_daily_summary
                
                send_daily_summary(
                    guardian_phone=guardian[3],
                    patient_name=guardian[1],
                    stats=stats
                )
                
                print(f"✅ Daily summary sent")
            except Exception as e:
                print(f"❌ Daily summary error: {e}")
    
    except Exception as e:
        print(f"❌ Error generating daily summary: {e}")


def run_scheduler():
    """Run scheduler in background thread"""
    print("🔄 Scheduler started...")
    
    while True:
        schedule.run_pending()
        time.sleep(20)  # ⚡ Check every 20 seconds for faster response


def start_scheduler():
    """Start scheduler thread with all background tasks"""
    
    schedule.clear()
    
    load_all_schedules()
    
    # ⚡⚡⚡ Check for missed medications every 30 SECONDS for 1-minute alerts
    schedule.every(30).seconds.do(check_missed_medications)
    
    # Check low stock once daily at 9 AM
    schedule.every().day.at("09:00").do(check_low_stock_medications)
    
    # Send daily summary at 10 PM
    schedule.every().day.at("22:00").do(daily_summary)
    
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("✅ DoseBuddy Scheduler started successfully!")
    print("📅 Loaded medication schedules")
    print("📱 WhatsApp alerts enabled")
    print("🔔 Desktop notifications active")
    print("⚡⚡⚡ SUPER FAST: 1-MINUTE missed medication alerts!")


def load_all_schedules():
    """Load all medications and schedule them"""
    try:
        conn = sqlite3.connect('data/dosebuddy.db')
        cursor = conn.execute('SELECT id, name, dosage, times FROM medications')
        medications = cursor.fetchall()
        conn.close()
        
        scheduled_count = 0
        for med in medications:
            schedule_medication(med[0], med[1], med[2], med[3])
            scheduled_count += 1
        
        print(f"📋 Loaded {scheduled_count} medication schedule(s)")
    
    except Exception as e:
        print(f"❌ Error loading schedules: {e}")


def get_next_scheduled_times():
    """Get next scheduled medication times"""
    try:
        conn = sqlite3.connect('data/dosebuddy.db')
        cursor = conn.execute('SELECT name, dosage, times FROM medications')
        medications = cursor.fetchall()
        conn.close()
        
        current_time = datetime.now()
        current_date = current_time.strftime("%Y-%m-%d")
        
        upcoming = []
        
        for med in medications:
            name, dosage, times_str = med
            times_list = times_str.split(',')
            
            for scheduled_time in times_list:
                scheduled_time = scheduled_time.strip()
                try:
                    scheduled_dt = datetime.strptime(f"{current_date} {scheduled_time}", "%Y-%m-%d %H:%M")
                    
                    if scheduled_dt < current_time:
                        scheduled_dt += timedelta(days=1)
                    
                    upcoming.append({
                        'medication': f"{name} ({dosage})",
                        'time': scheduled_time,
                        'datetime': scheduled_dt
                    })
                except:
                    continue
        
        upcoming.sort(key=lambda x: x['datetime'])
        
        return upcoming[:5]
    
    except Exception as e:
        print(f"❌ Error getting next scheduled times: {e}")
        return []


def test_notification():
    """Test notification system"""
    send_notification("Test Medication", "500mg - This is a test")
    print("✅ Test notification sent")


def test_whatsapp_integration():
    """Test WhatsApp integration"""
    try:
        from database import get_guardian_info
        from whatsapp_notifier import send_whatsapp_alert
        
        guardian = get_guardian_info()
        if not guardian:
            print("❌ No guardian configured")
            return False
        
        send_whatsapp_alert(
            guardian_phone=guardian[3],
            patient_name=guardian[1],
            medication_name="Test Medication (500mg)",
            scheduled_time="10:00 AM"
        )
        
        print("✅ Test WhatsApp sent successfully")
        return True
    
    except Exception as e:
        print(f"❌ WhatsApp test failed: {e}")
        return False
