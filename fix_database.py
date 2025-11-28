import sqlite3
import os

print("🔧 DoseBuddy Database Fix Script")
print("=" * 50)

# Check if database exists
if not os.path.exists('data/dosebuddy.db'):
    print("❌ Database not found at 'data/dosebuddy.db'")
    print("The database will be created when you run the app.")
    exit()

# Connect to database
conn = sqlite3.connect('data/dosebuddy.db')
cursor = conn.cursor()

print("✅ Connected to database")

# Fix 1: Add med_type column if missing
try:
    cursor.execute("SELECT med_type FROM medications LIMIT 1")
    print("✅ Column 'med_type' already exists")
except sqlite3.OperationalError:
    print("⚠️  Column 'med_type' missing. Adding it now...")
    cursor.execute("ALTER TABLE medications ADD COLUMN med_type TEXT DEFAULT 'Tablet'")
    conn.commit()
    print("✅ Column 'med_type' added successfully!")

# Fix 2: Update existing medications to have default type
cursor.execute("UPDATE medications SET med_type = 'Tablet' WHERE med_type IS NULL")
conn.commit()
print("✅ Updated existing medications with default type")

# Verify the fix
cursor.execute("PRAGMA table_info(medications)")
columns = cursor.fetchall()
print("\n📋 Current database columns:")
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

conn.close()
print("\n" + "=" * 50)
print("✅ Database fix completed successfully!")
print("You can now run: streamlit run app.py")
