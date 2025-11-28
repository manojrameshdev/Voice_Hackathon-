import sqlite3
from datetime import datetime
import os


def init_database():
    """Create database tables for DoseBuddy"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect('data/dosebuddy.db', check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    
    # Medications table with med_type column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            times TEXT NOT NULL,
            total_count INTEGER NOT NULL,
            remaining_count INTEGER NOT NULL,
            added_date TEXT NOT NULL,
            med_type TEXT DEFAULT 'Tablet'
        )
    ''')
    
    # Schedule log table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedule_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            scheduled_time TEXT NOT NULL,
            actual_time TEXT,
            status TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
        )
    ''')
    
    # Prescriptions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
        )
    ''')
    
    # Guardian table for WhatsApp alerts
    conn.execute('''
        CREATE TABLE IF NOT EXISTS guardian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            guardian_name TEXT NOT NULL,
            guardian_phone TEXT NOT NULL,
            whatsapp_enabled INTEGER DEFAULT 1,
            email TEXT,
            added_date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()


def add_medication_with_type(name, dosage, frequency, times, total_count, med_type):
    """Add new medication with type"""
    conn = sqlite3.connect('data/dosebuddy.db')
    conn.execute('''
        INSERT INTO medications (name, dosage, frequency, times, total_count, remaining_count, added_date, med_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, dosage, frequency, times, total_count, total_count, datetime.now().strftime('%Y-%m-%d'), med_type))
    conn.commit()
    conn.close()


def add_medication(name, dosage, frequency, times, total_count):
    """Add new medication (backward compatibility)"""
    add_medication_with_type(name, dosage, frequency, times, total_count, "Tablet")


def get_all_medications():
    """Get all medications"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('SELECT * FROM medications')
    medications = cursor.fetchall()
    conn.close()
    return medications


def get_medication_by_id(medication_id):
    """Get specific medication by ID"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('SELECT * FROM medications WHERE id = ?', (medication_id,))
    medication = cursor.fetchone()
    conn.close()
    return medication


def update_tablet_count(medication_id, new_count):
    """Update remaining tablet count"""
    conn = sqlite3.connect('data/dosebuddy.db')
    conn.execute('UPDATE medications SET remaining_count = ? WHERE id = ?', (new_count, medication_id))
    conn.commit()
    conn.close()


def log_medication_taken(medication_id, scheduled_time, status):
    """Log when medication is taken or missed"""
    conn = sqlite3.connect('data/dosebuddy.db')
    actual_time = datetime.now().strftime('%H:%M:%S') if status == 'Taken' else None
    
    # Check if already logged for this medication, time, and date
    cursor = conn.execute('''
        SELECT id FROM schedule_log 
        WHERE medication_id = ? AND scheduled_time = ? AND date = ?
    ''', (medication_id, scheduled_time, datetime.now().strftime('%Y-%m-%d')))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing log
        conn.execute('''
            UPDATE schedule_log 
            SET actual_time = ?, status = ?
            WHERE id = ?
        ''', (actual_time, status, existing[0]))
    else:
        # Insert new log
        conn.execute('''
            INSERT INTO schedule_log (medication_id, scheduled_time, actual_time, status, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (medication_id, scheduled_time, actual_time, status, datetime.now().strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()


def check_medication_status(medication_id, scheduled_time, date):
    """Check if medication was logged for specific time and date"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT status FROM schedule_log
        WHERE medication_id = ? AND scheduled_time = ? AND date = ?
    ''', (medication_id, scheduled_time, date))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_adherence_data(days=7):
    """Get adherence data for analytics"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT status, COUNT(*) as count
        FROM schedule_log
        WHERE date >= date('now', '-{} days')
        GROUP BY status
    '''.format(days))
    data = cursor.fetchall()
    conn.close()
    return data


def get_daily_adherence(days=7):
    """Get daily adherence for bar chart"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT date, status, COUNT(*) as count
        FROM schedule_log
        WHERE date >= date('now', '-{} days')
        GROUP BY date, status
        ORDER BY date
    '''.format(days))
    data = cursor.fetchall()
    conn.close()
    return data


# ===== GUARDIAN MANAGEMENT FUNCTIONS =====

def add_guardian(patient_name, guardian_name, guardian_phone, email=""):
    """Add guardian contact information for WhatsApp alerts"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    # Delete existing guardian (only one guardian allowed)
    conn.execute('DELETE FROM guardian')
    
    # Add new guardian
    conn.execute('''
        INSERT INTO guardian (patient_name, guardian_name, guardian_phone, email, whatsapp_enabled, added_date)
        VALUES (?, ?, ?, ?, 1, ?)
    ''', (patient_name, guardian_name, guardian_phone, email, datetime.now().strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()


def get_guardian_info():
    """Get guardian information"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('SELECT * FROM guardian ORDER BY id DESC LIMIT 1')
    guardian = cursor.fetchone()
    conn.close()
    return guardian


def update_guardian_whatsapp_status(enabled):
    """Enable or disable WhatsApp notifications"""
    conn = sqlite3.connect('data/dosebuddy.db')
    conn.execute('UPDATE guardian SET whatsapp_enabled = ?', (1 if enabled else 0,))
    conn.commit()
    conn.close()


def delete_guardian():
    """Remove guardian information"""
    conn = sqlite3.connect('data/dosebuddy.db')
    conn.execute('DELETE FROM guardian')
    conn.commit()
    conn.close()


# ===== MEDICATION HISTORY & REPORTING =====

def get_missed_medications_today():
    """Get medications missed today"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT m.name, m.dosage, sl.scheduled_time, sl.status
        FROM schedule_log sl
        JOIN medications m ON sl.medication_id = m.id
        WHERE sl.date = ? AND sl.status = 'Missed'
        ORDER BY sl.scheduled_time
    ''', (datetime.now().strftime('%Y-%m-%d'),))
    missed = cursor.fetchall()
    conn.close()
    return missed


def get_medication_history(medication_id, days=30):
    """Get medication history for specific medication"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT date, scheduled_time, actual_time, status
        FROM schedule_log
        WHERE medication_id = ? AND date >= date('now', '-{} days')
        ORDER BY date DESC, scheduled_time DESC
    '''.format(days), (medication_id,))
    history = cursor.fetchall()
    conn.close()
    return history


def get_low_stock_medications(threshold=10):
    """Get medications with low stock"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT * FROM medications
        WHERE remaining_count <= ?
        ORDER BY remaining_count ASC
    ''', (threshold,))
    low_stock = cursor.fetchall()
    conn.close()
    return low_stock


def get_total_medications_count():
    """Get total number of active medications"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('SELECT COUNT(*) FROM medications')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_logs_count():
    """Get total number of medication logs"""
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('SELECT COUNT(*) FROM schedule_log')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def delete_medication(medication_id):
    """Delete medication and all related data"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    # Delete from all tables
    conn.execute('DELETE FROM medications WHERE id = ?', (medication_id,))
    conn.execute('DELETE FROM schedule_log WHERE medication_id = ?', (medication_id,))
    conn.execute('DELETE FROM prescriptions WHERE medication_id = ?', (medication_id,))
    
    conn.commit()
    conn.close()


def clear_all_data():
    """Clear all data from database (use with caution)"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    conn.execute('DELETE FROM medications')
    conn.execute('DELETE FROM schedule_log')
    conn.execute('DELETE FROM prescriptions')
    conn.execute('DELETE FROM guardian')
    
    conn.commit()
    conn.close()


# ===== STATISTICS & ANALYTICS =====

def get_adherence_statistics(days=30):
    """Get detailed adherence statistics"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    cursor = conn.execute('''
        SELECT 
            COUNT(*) as total_doses,
            SUM(CASE WHEN status='Taken' THEN 1 ELSE 0 END) as taken,
            SUM(CASE WHEN status='Missed' THEN 1 ELSE 0 END) as missed,
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) as delayed
        FROM schedule_log
        WHERE date >= date('now', '-{} days')
    '''.format(days))
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats and stats[0] > 0:
        return {
            'total_doses': stats[0],
            'taken': stats[1] or 0,
            'missed': stats[2] or 0,
            'delayed': stats[3] or 0,
            'adherence_rate': round((stats[1] or 0) / stats[0] * 100, 1)
        }
    else:
        return {
            'total_doses': 0,
            'taken': 0,
            'missed': 0,
            'delayed': 0,
            'adherence_rate': 0
        }


def get_medication_streak():
    """Get current streak of consecutive days with 100% adherence"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    # Get last 30 days of data
    cursor = conn.execute('''
        SELECT date, 
               SUM(CASE WHEN status='Taken' THEN 1 ELSE 0 END) as taken,
               COUNT(*) as total
        FROM schedule_log
        WHERE date >= date('now', '-30 days')
        GROUP BY date
        ORDER BY date DESC
    ''')
    
    days_data = cursor.fetchall()
    conn.close()
    
    streak = 0
    for date, taken, total in days_data:
        if taken == total and total > 0:
            streak += 1
        else:
            break
    
    return streak


# ===== BACKUP & EXPORT =====

def export_data_to_dict():
    """Export all data to dictionary for backup"""
    conn = sqlite3.connect('data/dosebuddy.db')
    
    # Get all data
    medications = conn.execute('SELECT * FROM medications').fetchall()
    schedule_log = conn.execute('SELECT * FROM schedule_log').fetchall()
    guardian = conn.execute('SELECT * FROM guardian').fetchall()
    
    conn.close()
    
    return {
        'medications': medications,
        'schedule_log': schedule_log,
        'guardian': guardian,
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
