import streamlit as st
from database import *
from scheduler import start_scheduler, load_all_schedules
from ai_assistant import get_ai_response, get_medication_list_for_ai
from analytics import create_pie_chart, create_bar_chart, calculate_adherence_score
from PIL import Image
import os
import sqlite3
from datetime import datetime, time as dt_time

# Page configuration
st.set_page_config(
    page_title="DoseBuddy - Smart Medication Tracker",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Common medication names for autocomplete suggestions
COMMON_MEDICATIONS = [
    "Paracetamol", "Dolo 650", "Dolo 500", "Crocin 650", "Crocin Advance", 
    "Aspirin", "Disprin", "Ibuprofen", "Combiflam", "Brufen",
    "Amoxicillin", "Augmentin", "Azithromycin", "Zithromax", "Ciprofloxacin",
    "Metformin", "Glycomet", "Atorvastatin", "Lipitor", "Amlodipine",
    "Lisinopril", "Levothyroxine", "Eltroxin", "Omeprazole", "Pantoprazole",
    "Pan 40", "Cetirizine", "Allegra", "Montelukast", "Montair",
    "Salbutamol", "Asthalin", "Insulin", "Metoprolol", "Betaloc",
    "Clopidogrel", "Plavix", "Warfarin", "Digoxin", "Furosemide",
    "Ranitidine", "Aciloc", "Domperidone", "Vomistop", "Ondansetron",
    "Vitamin D3", "Calcium", "Shelcal", "Iron", "Folvite", "Vitamin B12"
]

# Dynamic CSS based on theme
def apply_theme_css():
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
            }
            [data-testid="stSidebar"] {
                background-color: #1a1d24;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #4CAF50 !important;
                font-weight: 700 !important;
            }
            p, span, div, label, .stMarkdown {
                color: #fafafa !important;
            }
            [data-testid="stMetricValue"] {
                color: #4CAF50 !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }
            [data-testid="stMetricLabel"] {
                color: #e0e0e0 !important;
                font-weight: 600 !important;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white !important;
                border-radius: 8px;
                border: none;
                padding: 0.5rem 1rem;
                font-weight: 600;
            }
            .stFormSubmitButton>button {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #262730 !important;
                color: white !important;
                border: 1px solid #4CAF50 !important;
            }
            .stSelectbox>div>div {
                background-color: #262730 !important;
                color: white !important;
            }
            .streamlit-expanderHeader {
                background-color: #1e2128 !important;
                color: white !important;
                border-left: 4px solid #4CAF50;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #262730;
                color: white !important;
            }
            .stTabs [aria-selected="true"] {
                background-color: #4CAF50 !important;
            }
            .stRadio > label, .stCheckbox > label {
                color: white !important;
            }
            .low-stock-alert {
                background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
                padding: 1.5rem;
                border-radius: 12px;
                animation: pulse 2s infinite;
            }
            .low-stock-title, .low-stock-item {
                color: white !important;
            }
            @keyframes pulse {
                0%, 100% { box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4); }
                50% { box-shadow: 0 4px 20px rgba(255, 107, 107, 0.8); }
            }
        </style>
        """, unsafe_allow_html=True)
    else:  # light theme
        st.markdown("""
        <style>
            .stApp {
                background-color: #ffffff;
            }
            [data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #2e7d32 !important;
                font-weight: 700 !important;
            }
            p, span, div, label, .stMarkdown {
                color: #000000 !important;
            }
            [data-testid="stMetricValue"] {
                color: #2e7d32 !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }
            [data-testid="stMetricLabel"] {
                color: #424242 !important;
                font-weight: 600 !important;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white !important;
                border-radius: 8px;
                border: none;
                padding: 0.5rem 1rem;
                font-weight: 600;
            }
            .stFormSubmitButton>button {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #f5f5f5 !important;
                color: #000000 !important;
                border: 2px solid #4CAF50 !important;
            }
            .stSelectbox>div>div {
                background-color: #f5f5f5 !important;
                color: #000000 !important;
            }
            .streamlit-expanderHeader {
                background-color: #e8f5e9 !important;
                color: #000000 !important;
                border-left: 4px solid #4CAF50;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #e0e0e0;
                color: #000000 !important;
            }
            .stTabs [aria-selected="true"] {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            .stRadio > label, .stCheckbox > label {
                color: #000000 !important;
            }
            .low-stock-alert {
                background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
                padding: 1.5rem;
                border-radius: 12px;
                animation: pulse 2s infinite;
            }
            .low-stock-title, .low-stock-item {
                color: white !important;
            }
            .stSuccess {
                background-color: #c8e6c9 !important;
                color: #1b5e20 !important;
            }
            .stWarning {
                background-color: #fff9c4 !important;
                color: #f57f17 !important;
            }
            .stError {
                background-color: #ffcdd2 !important;
                color: #b71c1c !important;
            }
            .stInfo {
                background-color: #b3e5fc !important;
                color: #01579b !important;
            }
        </style>
        """, unsafe_allow_html=True)

# Apply theme CSS
apply_theme_css()

# Initialize database
init_database()

# Start scheduler in background
if 'scheduler_started' not in st.session_state:
    start_scheduler()
    load_all_schedules()
    st.session_state.scheduler_started = True

# Sidebar with theme toggle
st.sidebar.title("💊 DoseBuddy")
st.sidebar.markdown("*Your Smart Medication Companion*")

# Theme Toggle Button
theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
theme_text = "Dark Mode" if st.session_state.theme == 'light' else "Light Mode"

if st.sidebar.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.rerun()

st.sidebar.markdown("---")

# Check low stock for notification badge
meds = get_all_medications()
low_stock_count = len([m for m in meds if m[6] <= 10])

if low_stock_count > 0:
    st.sidebar.warning(f"🔔 {low_stock_count} Low Stock Alert(s)!")

# Check if guardian is configured
guardian = get_guardian_info()
if guardian:
    st.sidebar.success(f"👨‍👩‍👧 Guardian: {guardian[2]}")

page = st.sidebar.radio("Navigate", [
    "🏠 Dashboard", 
    "💊 My Medications", 
    "📊 Analytics", 
    "📋 Prescriptions", 
    "👨‍👩‍👧 Guardian Setup",
    "🤖 AI Assistant", 
    "⚙️ Settings"
])

# Helper functions
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

def get_med_type_icon(med_type):
    """Return icon based on medication type"""
    icons = {
        "Tablet": "💊",
        "Capsule": "💊",
        "Syrup": "🧪",
        "Injection": "💉",
        "Drops": "💧",
        "Inhaler": "🌬️",
        "Cream/Ointment": "🧴",
        "Other": "📦"
    }
    return icons.get(med_type, "💊")

# ===== DASHBOARD PAGE =====
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard")
    
    score = calculate_adherence_score()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Adherence Score", f"{score}%", 
                 delta="Good" if score >= 80 else "Needs Improvement")
    
    with col2:
        st.metric("Active Medications", len(meds))
    
    with col3:
        low_stock = [m for m in meds if m[6] <= 10]
        st.metric("Low Stock Alerts", len(low_stock), delta="Critical" if len(low_stock) > 0 else None)
    
    if low_stock:
        st.markdown("""
        <div class="low-stock-alert">
            <div class="low-stock-title">🔔 URGENT: Low Stock Medications</div>
        """, unsafe_allow_html=True)
        
        for med in low_stock:
            med_type_icon = get_med_type_icon(med[8] if len(med) > 8 else "Tablet")
            st.markdown(f"""
            <div class="low-stock-item">
                {med_type_icon} <strong>{med[1]}</strong> ({med[2]}) - Only <strong>{med[6]}</strong> remaining
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("📅 Today's Schedule")
    medications = get_all_medications()
    if medications:
        for med in medications:
            times_list = med[4].split(',')
            formatted_times = [format_time_12hr(t) for t in times_list]
            med_type_icon = get_med_type_icon(med[8] if len(med) > 8 else "Tablet")
            
            with st.expander(f"{med_type_icon} {med[1]} - {med[2]}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Type:** {med[8] if len(med) > 8 else 'Tablet'}")
                    st.write(f"**Times:** {', '.join(formatted_times)}")
                with col2:
                    st.write(f"**Remaining:** {med[6]}")
                    if med[6] <= 10:
                        st.error("⚠️ Low!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Taken", key=f"taken_{med[0]}"):
                        log_medication_taken(med[0], "Manual", "Taken")
                        new_count = med[6] - 1
                        update_tablet_count(med[0], new_count)
                        st.success("Logged as taken!")
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Missed", key=f"missed_{med[0]}"):
                        log_medication_taken(med[0], "Manual", "Missed")
                        st.warning("Logged as missed")
                        st.rerun()
    else:
        st.info("No medications added yet. Go to 'My Medications' to add one!")

# ===== MY MEDICATIONS PAGE =====
elif page == "💊 My Medications":
    st.title("💊 My Medications")
    
    tab1, tab2 = st.tabs(["Add New Medication", "View All Medications"])
    
    with tab1:
        st.subheader("Add New Medication")
        
        # Frequency selector OUTSIDE form with buttons
        st.write("**Step 1: Select Frequency**")
        if 'temp_frequency' not in st.session_state:
            st.session_state.temp_frequency = 1
        
        col_freq = st.columns([1, 2, 1])
        with col_freq[0]:
            if st.button("➖", key="freq_minus"):
                if st.session_state.temp_frequency > 1:
                    st.session_state.temp_frequency -= 1
                    st.rerun()
        with col_freq[1]:
            st.markdown(f"<h3 style='text-align: center;'>{st.session_state.temp_frequency}x per day</h3>", unsafe_allow_html=True)
        with col_freq[2]:
            if st.button("➕", key="freq_plus"):
                if st.session_state.temp_frequency < 6:
                    st.session_state.temp_frequency += 1
                    st.rerun()
        
        med_frequency = st.session_state.temp_frequency
        
        st.markdown("---")
        st.write("**Step 2: Fill Medication Details**")
        
        with st.form("add_medication_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Medication Name** *")
                use_custom = st.checkbox("Enter custom medication name", value=False)
                
                if use_custom:
                    med_name = st.text_input("Custom Medication Name", placeholder="e.g., New Medicine", label_visibility="collapsed")
                else:
                    med_name = st.selectbox(
                        "Select or type medication name",
                        options=[""] + COMMON_MEDICATIONS,
                        help="Start typing to search medications",
                        label_visibility="collapsed"
                    )
                
                med_dosage = st.text_input("Dosage *", placeholder="e.g., 500mg")
            
            with col2:
                med_type = st.selectbox("Medication Type *", 
                    ["Tablet", "Capsule", "Syrup", "Injection", "Drops", "Inhaler", "Cream/Ointment", "Other"])
                st.info(f"✅ Frequency: {med_frequency}x per day")
            
            times = []
            st.write("**Schedule Times:**")
            
            time_labels = {
                1: ["Morning"],
                2: ["Morning", "Evening"],
                3: ["Morning", "Afternoon", "Night"],
                4: ["Morning", "Afternoon", "Evening", "Night"],
                5: ["Early Morning", "Morning", "Afternoon", "Evening", "Night"],
                6: ["Early Morning", "Morning", "Late Morning", "Afternoon", "Evening", "Night"]
            }
            
            default_times = {
                0: (10, 0), 1: (14, 0), 2: (21, 0),
                3: (6, 0), 4: (18, 0), 5: (12, 0)
            }
            
            labels = time_labels.get(med_frequency, [f"Time {i+1}" for i in range(med_frequency)])
            
            st.write(f"*Enter {med_frequency} time(s) for your medication:*")
            
            for row_start in range(0, med_frequency, 3):
                cols = st.columns(3)
                for col_idx in range(3):
                    time_index = row_start + col_idx
                    if time_index < med_frequency:
                        with cols[col_idx]:
                            label = labels[time_index]
                            default_hour, default_min = default_times.get(time_index, (9, 0))
                            
                            time_input = st.time_input(
                                f"{label} *", 
                                value=dt_time(default_hour, default_min), 
                                key=f"time_input_{time_index}_{med_frequency}"
                            )
                            times.append(time_input.strftime("%H:%M"))
            
            quantity_label = "Total Count *"
            if med_type in ["Syrup", "Drops", "Cream/Ointment"]:
                quantity_label = "Total ml/grams *"
            elif med_type == "Injection":
                quantity_label = "Total Syringes *"
            elif med_type == "Inhaler":
                quantity_label = "Total Puffs *"
            
            med_count = st.number_input(quantity_label, min_value=1, value=30)
            
            submitted = st.form_submit_button("✅ Add Medication")
            
            if submitted:
                if med_name and med_dosage and len(times) == med_frequency:
                    times_str = ",".join(times)
                    add_medication_with_type(med_name, med_dosage, med_frequency, times_str, med_count, med_type)
                    load_all_schedules()
                    st.success(f"✅ {med_name} added successfully!")
                    st.balloons()
                    st.session_state.temp_frequency = 1
                    st.rerun()
                else:
                    st.error(f"⚠️ Please fill all required fields. Need {med_frequency} times, got {len(times)}")
    
    with tab2:
        st.subheader("All Medications")
        medications = get_all_medications()
        
        if medications:
            for med in medications:
                med_type_icon = get_med_type_icon(med[8] if len(med) > 8 else "Tablet")
                with st.expander(f"{med_type_icon} {med[1]} - {med[2]}"):
                    times_list = med[4].split(',')
                    formatted_times = [format_time_12hr(t) for t in times_list]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {med[8] if len(med) > 8 else 'Tablet'}")
                        st.write(f"**Frequency:** {med[3]}x daily")
                        st.write(f"**Times:** {', '.join(formatted_times)}")
                        st.write(f"**Added on:** {med[7]}")
                    with col2:
                        unit = "units"
                        if len(med) > 8:
                            if med[8] in ["Syrup", "Drops", "Cream/Ointment"]:
                                unit = "ml/grams"
                            elif med[8] == "Injection":
                                unit = "syringes"
                            elif med[8] == "Inhaler":
                                unit = "puffs"
                            else:
                                unit = "tablets"
                        
                        st.write(f"**Total:** {med[5]} {unit}")
                        st.write(f"**Remaining:** {med[6]} {unit}")
                        
                        if med[6] <= 10:
                            st.error("⚠️ Low stock!")
                        elif med[6] <= 20:
                            st.warning("⚠️ Running low")
                    
                    if st.button(f"🗑️ Delete {med[1]}", key=f"delete_{med[0]}"):
                        delete_medication(med[0])
                        load_all_schedules()
                        st.success(f"✅ Deleted {med[1]}")
                        st.rerun()
        else:
            st.info("No medications added yet")

# ===== ANALYTICS PAGE =====
elif page == "📊 Analytics":
    st.title("📊 Analytics Dashboard")
    
    low_stock = [m for m in meds if m[6] <= 10]
    if low_stock:
        st.markdown("""
        <div class="low-stock-alert">
            <div class="low-stock-title">🔔 Low Stock Medications - Take Action!</div>
        """, unsafe_allow_html=True)
        
        for med in low_stock:
            med_type_icon = get_med_type_icon(med[8] if len(med) > 8 else "Tablet")
            percentage = (med[6] / med[5]) * 100
            st.markdown(f"""
            <div class="low-stock-item">
                {med_type_icon} <strong>{med[1]}</strong> - {med[6]}/{med[5]} remaining ({percentage:.0f}%)
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    days_filter = st.selectbox("Select Time Period", [7, 14, 30], index=0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Adherence Overview")
        pie_fig = create_pie_chart(days_filter)
        if pie_fig:
            st.pyplot(pie_fig)
        else:
            st.info("No data available yet. Start tracking your medications!")
    
    with col2:
        st.subheader("Daily Adherence Trend")
        bar_fig = create_bar_chart(days_filter)
        if bar_fig:
            st.pyplot(bar_fig)
        else:
            st.info("No data available yet")
    
    st.subheader("Overall Performance")
    score = calculate_adherence_score()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Adherence Score (30 days)", f"{score}%")
    
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT 
            SUM(CASE WHEN status='Taken' THEN 1 ELSE 0 END) as taken,
            SUM(CASE WHEN status='Missed' THEN 1 ELSE 0 END) as missed
        FROM schedule_log
        WHERE date >= date('now', '-30 days')
    ''')
    stats = cursor.fetchone()
    conn.close()
    
    if stats and stats[0]:
        with col2:
            st.metric("Doses Taken", stats[0])
        with col3:
            st.metric("Doses Missed", stats[1] if stats[1] else 0)
    
    if score >= 90:
        st.success("🌟 Excellent adherence! Keep up the great work!")
    elif score >= 70:
        st.warning("⚠️ Good adherence, but there's room for improvement")
    else:
        st.error("❗ Poor adherence. Please consult your doctor")
    
    st.subheader("Recent Missed Doses")
    conn = sqlite3.connect('data/dosebuddy.db')
    cursor = conn.execute('''
        SELECT m.name, m.dosage, sl.date, sl.scheduled_time
        FROM schedule_log sl
        JOIN medications m ON sl.medication_id = m.id
        WHERE sl.status = 'Missed'
        ORDER BY sl.date DESC, sl.scheduled_time DESC
        LIMIT 10
    ''')
    missed = cursor.fetchall()
    conn.close()
    
    if missed:
        for m in missed:
            st.write(f"- **{m[0]}** ({m[1]}) - {m[2]} at {format_time_12hr(m[3])}")
    else:
        st.info("No missed doses! Great job! 🎉")

# ===== PRESCRIPTIONS PAGE =====
elif page == "📋 Prescriptions":
    st.title("📋 Prescription Manager")
    
    medications = get_all_medications()
    
    if not medications:
        st.info("Add medications first to upload prescriptions")
    else:
        st.subheader("Upload New Prescription")
        med_names = {f"{get_med_type_icon(med[8] if len(med) > 8 else 'Tablet')} {med[1]} ({med[2]})": med[0] for med in medications}
        selected_med = st.selectbox("Select Medication", list(med_names.keys()))
        
        uploaded_file = st.file_uploader("Upload Prescription Image", type=['jpg', 'jpeg', 'png', 'pdf'])
        
        if uploaded_file and st.button("💾 Save Prescription"):
            med_id = med_names[selected_med]
            
            if not os.path.exists('prescriptions'):
                os.makedirs('prescriptions')
            
            file_path = f"prescriptions/prescription_{med_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            conn = sqlite3.connect('data/dosebuddy.db')
            conn.execute('''
                INSERT INTO prescriptions (medication_id, image_path, upload_date)
                VALUES (?, ?, ?)
            ''', (med_id, file_path, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            
            st.success("✅ Prescription saved successfully!")
            st.rerun()
        
        st.subheader("Saved Prescriptions")
        conn = sqlite3.connect('data/dosebuddy.db')
        cursor = conn.execute('''
            SELECT p.id, p.image_path, p.upload_date, m.name, m.dosage
            FROM prescriptions p
            JOIN medications m ON p.medication_id = m.id
            ORDER BY p.upload_date DESC
        ''')
        prescriptions = cursor.fetchall()
        conn.close()
        
        if prescriptions:
            for presc in prescriptions:
                with st.expander(f"💊 {presc[3]} ({presc[4]}) - Uploaded on {presc[2]}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if os.path.exists(presc[1]):
                            try:
                                image = Image.open(presc[1])
                                st.image(image, use_container_width=True)
                            except:
                                st.error("Unable to display image")
                        else:
                            st.error("Image file not found")
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"del_presc_{presc[0]}"):
                            if os.path.exists(presc[1]):
                                os.remove(presc[1])
                            conn = sqlite3.connect('data/dosebuddy.db')
                            conn.execute('DELETE FROM prescriptions WHERE id = ?', (presc[0],))
                            conn.commit()
                            conn.close()
                            st.success("Prescription deleted")
                            st.rerun()
        else:
            st.info("No prescriptions uploaded yet")

# ===== GUARDIAN SETUP PAGE (NEW) =====
elif page == "👨‍👩‍👧 Guardian Setup":
    st.title("👨‍👩‍👧 Guardian Setup")
    st.write("Configure WhatsApp alerts for your guardian/caretaker when medications are missed")
    
    guardian = get_guardian_info()
    
    if guardian:
        st.success(f"✅ Guardian Configured: {guardian[2]} ({guardian[3]})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Patient Name:** {guardian[1]}")
            st.info(f"**Guardian Name:** {guardian[2]}")
        with col2:
            st.info(f"**WhatsApp Number:** {guardian[3]}")
            status = "✅ Enabled" if guardian[4] == 1 else "❌ Disabled"
            st.info(f"**WhatsApp Alerts:** {status}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Send Test WhatsApp"):
                try:
                    from whatsapp_notifier import test_whatsapp_connection
                    success, msg = test_whatsapp_connection(guardian[3])
                    if success:
                        st.success("✅ Test message sent! Check WhatsApp.")
                    else:
                        st.error(f"❌ Error: {msg}")
                except Exception as e:
                    st.error(f"❌ WhatsApp notifier not configured: {e}")
        
        with col2:
            current_status = guardian[4] == 1
            new_status = st.toggle("Enable Alerts", value=current_status, key="whatsapp_toggle")
            if new_status != current_status:
                update_guardian_whatsapp_status(new_status)
                st.success(f"WhatsApp alerts {'enabled' if new_status else 'disabled'}")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Remove Guardian"):
                delete_guardian()
                st.success("Guardian removed")
                st.rerun()
        
        st.markdown("---")
        st.subheader("📱 How It Works")
        st.markdown("""
        **Automatic WhatsApp Alerts:**
        - 🚨 **Missed Medication:** Alert sent 15 minutes after scheduled time if not taken
        - 📦 **Low Stock:** Daily notification when medication count ≤5
        - 📊 **Daily Summary:** End-of-day adherence report at 10 PM
        
        **Guardian receives instant WhatsApp messages with:**
        - Patient name
        - Medication details
        - Scheduled vs actual time
        - Stock levels
        """)
    
    else:
        st.write("### 📝 Add Guardian Contact")
        
        with st.form("guardian_form"):
            patient_name = st.text_input("Patient Name *", placeholder="e.g., John Doe")
            guardian_name = st.text_input("Guardian Name *", placeholder="e.g., Jane Doe (Mother)")
            guardian_phone = st.text_input("Guardian WhatsApp Number *", 
                placeholder="e.g., +919876543210 (with country code)")
            email = st.text_input("Email (Optional)", placeholder="guardian@example.com")
            
            st.info("📱 **Important:** Number must include country code (e.g., +91 for India, +1 for USA)")
            
            submitted = st.form_submit_button("💾 Save Guardian")
            
            if submitted:
                if patient_name and guardian_name and guardian_phone:
                    if not guardian_phone.startswith('+'):
                        st.error("⚠️ Phone number must start with + and country code (e.g., +919876543210)")
                    else:
                        add_guardian(patient_name, guardian_name, guardian_phone, email)
                        st.success("✅ Guardian added successfully!")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.markdown("---")
        st.subheader("📋 Setup Instructions")
        
        with st.expander("📱 Step 1: Get Twilio Account (FREE)"):
            st.markdown("""
            1. Visit: [**https://www.twilio.com/try-twilio**](https://www.twilio.com/try-twilio)
            2. Sign up (get $15 free credit - no credit card needed)
            3. Verify your email and phone number
            """)
        
        with st.expander("💬 Step 2: Setup WhatsApp Sandbox"):
            st.markdown("""
            1. Go to **Twilio Console** → **Messaging** → **Try it out** → **Send a WhatsApp message**
            2. Scan QR code with your WhatsApp
            3. Send the join code (e.g., "join <code>") to the Twilio number
            4. You'll receive confirmation message
            """)
        
        with st.expander("🔑 Step 3: Get API Credentials"):
            st.markdown("""
            1. In Twilio Console, find:
               - **Account SID** (starts with AC...)
               - **Auth Token** (click to reveal)
            2. Open `whatsapp_notifier.py` file
            3. Replace:
               ```
               TWILIO_ACCOUNT_SID = "your_account_sid_here"
               TWILIO_AUTH_TOKEN = "your_auth_token_here"
               ```
            4. Save the file
            """)
        
        with st.expander("✅ Step 4: Test Connection"):
            st.markdown("""
            1. Add guardian details above
            2. Click **"Send Test WhatsApp"** button
            3. Check if guardian receives test message
            4. If successful, alerts are ready!
            """)
        
        st.info("""
        **💡 Features:**
        - ✅ Instant WhatsApp notifications for missed medications
        - ✅ Low stock warnings
        - ✅ Daily adherence summaries
        - ✅ FREE for up to 1000 messages/month
        - ✅ No credit card required for sandbox
        """)

# ===== AI ASSISTANT PAGE =====
elif page == "🤖 AI Assistant":
    st.title("🤖 DoseBuddy AI Assistant")
    st.write("Ask me anything about your medications!")
    
    user_meds = get_medication_list_for_ai()
    
    if user_meds != "No medications currently tracked":
        st.info(f"**Your Medications:** {user_meds}")
    else:
        st.warning("No medications added yet!")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.subheader("💡 Suggested Questions:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What is this medicine used for?"):
            st.session_state.suggested_q = "What is this medicine used for?"
        if st.button("What are the side effects?"):
            st.session_state.suggested_q = "What are the side effects?"
    with col2:
        if st.button("Can I take it with food?"):
            st.session_state.suggested_q = "Can I take it with food?"
        if st.button("What if I miss a dose?"):
            st.session_state.suggested_q = "What if I miss a dose?"
    
    user_question = st.text_input("Ask your question:", 
                                  value=st.session_state.get('suggested_q', ''),
                                  placeholder="e.g., What is Dolo 650 used for?")
    
    if 'suggested_q' in st.session_state:
        del st.session_state.suggested_q
    
    if st.button("🚀 Ask DoseBuddy AI") and user_question:
        with st.spinner("Thinking..."):
            response = get_ai_response(user_question, user_meds)
            st.session_state.chat_history.append(("You", user_question))
            st.session_state.chat_history.append(("DoseBuddy AI", response))
    
    st.subheader("💬 Conversation")
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 You:** {message}")
        else:
            st.markdown(f"**🤖 DoseBuddy AI:** {message}")
            st.markdown("---")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.info("ℹ️ **Note:** AI responses are for informational purposes only.")

# ===== SETTINGS PAGE =====
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("🎨 Appearance")
    current_theme = "Dark" if st.session_state.theme == 'dark' else "Light"
    st.write(f"**Current Theme:** {current_theme}")
    st.info("Use the theme toggle button in the sidebar to switch between light and dark modes")
    
    st.subheader("📬 Notification Settings")
    enable_notif = st.checkbox("Enable Desktop Notifications", value=True)
    notif_sound = st.checkbox("Enable Notification Sound", value=True)
    low_stock_notif = st.checkbox("Enable Low Stock Notifications", value=True)
    
    st.subheader("⏰ Reminder Settings")
    reminder_interval = st.slider("Follow-up Reminder Interval (minutes)", 5, 30, 10)
    low_stock_threshold = st.slider("Low Stock Alert Threshold", 5, 20, 10)
    
    st.subheader("📊 Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Data"):
            try:
                import pandas as pd
                conn = sqlite3.connect('data/dosebuddy.db')
                df = pd.read_sql_query("""
                    SELECT m.name, m.med_type, m.dosage, sl.date, sl.status
                    FROM schedule_log sl
                    JOIN medications m ON sl.medication_id = m.id
                    ORDER BY sl.date DESC
                """, conn)
                conn.close()
                
                csv = df.to_csv(index=False)
                st.download_button("💾 Download CSV", csv, 
                    f"dosebuddy_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🗑️ Clear All Data"):
            if st.checkbox("I confirm"):
                clear_all_data()
                st.success("All data cleared!")
                st.rerun()
    
    st.subheader("ℹ️ About DoseBuddy")
    st.markdown(f"""
    **DoseBuddy v1.0** | Current Theme: **{current_theme}**
    
    **Features:**
    - 💊 Multiple medication types with smart icons
    - 🔔 Low stock alerts with pulsing animations
    - 📊 Beautiful 3D adherence analytics
    - 📱 WhatsApp guardian alerts
    - 🤖 AI assistance (optional)
    - 🌙☀️ Light/Dark theme toggle
    - 🔍 Medication name autocomplete
    - ⏰ Smart reminders & notifications
    """)
    
    st.subheader("🛠️ System Info")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Medications", get_total_medications_count())
    with col2:
        st.metric("Logs", get_total_logs_count())
    with col3:
        conn = sqlite3.connect('data/dosebuddy.db')
        presc_count = conn.execute('SELECT COUNT(*) FROM prescriptions').fetchone()[0]
        conn.close()
        st.metric("Prescriptions", presc_count)

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("DoseBuddy © 2025")
st.sidebar.caption("Stay Healthy! 💪")
theme_display = "🌙 Dark Theme" if st.session_state.theme == 'dark' else "☀️ Light Theme"
st.sidebar.caption(theme_display)
