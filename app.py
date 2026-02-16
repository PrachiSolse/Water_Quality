import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# =========================================================
# 1. CONFIGURATION - DOUBLE CHECK THESE LINKS
# =========================================================
# Make sure this is the 'Executible' URL from Apps Script deployment
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZH2sKmRwJpILV5fDYn_gv07yPTE45gj9EkMPh_cCLBWckw2Q_oWb6DIxDvceRB1-jtA/exec" 

# Make sure this ends in 'output=csv' or is a direct CSV export link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1BlROSLN7OLqbjxEuEfuFoZy8xWJPhUwN7L-VUgbAWjv_9fkdnw4jmm7W2v7xI40VUXFV3w-ogQJE/pub?output=csv" 

# =========================================================
# 2. MASTER CSS (Fixes Invisible Labels & Contrast)
# =========================================================
st.set_page_config(page_title="AI Water Intelligence", layout="wide")

st.markdown("""
    <style>
    /* 1. Main Background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* 2. FORCE LABELS TO BE VISIBLE (White text for dark theme) */
    label, p, span, .stMarkdown, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }

    /* 3. THE WHITE ANALYSIS CARD (High Contrast) */
    .report-card { 
        background-color: #ffffff !important; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        border-top: 10px solid #007bff;
    }
    
    /* Force text INSIDE the white card to be BLACK */
    .report-card p, .report-card div, .report-card hr {
        color: #1a1a1a !important;
        font-size: 1rem !important;
    }

    .req-label {
        font-weight: 800 !important;
        color: #007bff !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        margin-bottom: 0px;
    }

    .status-good { color: #28a745 !important; font-weight: 800; font-size: 1.8rem !important; }
    .status-bad { color: #dc3545 !important; font-weight: 800; font-size: 1.8rem !important; }
    
    /* 4. Input Form Styling */
    [data-testid="stForm"] {
        background-color: #1a1c24;
        border: 1px solid #3d4455;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. APP LOGIC
# =========================================================
st.title("🌊 Smart Water Quality AI Portal")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📥 Sensor Data Entry")
    with st.form("manual_entry"):
        # Labels will now be white and readable
        val_ph = st.slider("pH Level", 0.0, 14.0, 7.2, step=0.1)
        val_tds = st.number_input("TDS (ppm)", value=250)
        val_turb = st.slider("Turbidity (NTU)", 0.0, 50.0, 2.0, step=0.1)
        val_temp = st.number_input("Temperature (°C)", value=25)
        submitted = st.form_submit_button("🚀 RUN AI ANALYSIS & SYNC")

with col2:
    st.subheader("🧠 AI Analysis Report")
    
    if submitted:
        # SYNC ATTEMPT
        try:
            requests.post(SCRIPT_URL, json={"ph": val_ph, "tds": val_tds, "turb": val_turb, "temp": val_temp}, timeout=3)
            st.success("✅ Cloud Database Synced Successfully")
        except:
            st.error("❌ Sync Failed. Check Script URL or Internet.")

        # AI CALCULATIONS
        is_safe = 6.5 <= val_ph <= 8.5 and val_tds <= 500 and val_turb <= 5
        res_text = "SAFE FOR USE" if is_safe else "POOR / UNHEALTHY"
        res_class = "status-good" if is_safe else "status-bad"

        # TREND PREDICTION (Requirement 2)
        try:
            df_hist = pd.read_csv(CSV_URL)
            df_hist.columns = df_hist.columns.str.strip().str.lower()
            y = df_hist['tds'].values.reshape(-1, 1)
            x = np.array(range(len(y))).reshape(-1, 1)
            model = LinearRegression().fit(x, y)
            future_pred = model.predict([[len(y) + 1]])[0][0]
            pred_msg = f"Next cycle estimate: **{future_pred:.2f} ppm**"
        except:
            pred_msg = "Database connecting... Predicting stability."

        # REMEDIATION (Requirement 4)
        remedy = "Standard monitoring."
        if val_ph < 6.5: remedy = "Action: Deploy Calcite Neutralizing Filter."
        elif val_tds > 500: remedy = "Action: Activate Reverse Osmosis (RO) system."

        # THE VISIBLE CARD
        st.markdown(f"""
            <div class="report-card">
                <p class="req-label">Requirement 1: Quality Check</p>
                <div class="{res_class}">{res_text}</div>
                <hr>
                <p class="req-label">Requirement 2: Future Outlook (ML)</p>
                <p>{pred_msg}</p>
                <hr>
                <p class="req-label">Requirement 3: Safety Precautions</p>
                <p>⚠️ {"Levels stable." if is_safe else "Risk of corrosion/mineral buildup."}</p>
                <hr>
                <p class="req-label">Requirement 4: Remediation Steps</p>
                <p>🛠️ <b>{remedy}</b></p>
            </div>
        """, unsafe_allow_html=True)

# =========================================================
# 4. DATA HISTORICAL STUDY (CSV CONNECTION)
# =========================================================
st.divider()
st.subheader("📊 Data Historical Study (AI Dataset)")
try:
    df_plot = pd.read_csv(CSV_URL)
    df_plot.columns = df_plot.columns.str.strip().str.lower()
    # Check if we have data to plot
    if not df_plot.empty:
        st.line_chart(df_plot[['ph', 'tds', 'turb']])
    else:
        st.warning("Google Sheet is empty. Sync data to see the chart.")
except Exception as e:
    st.error(f"Waiting for Google Sheet CSV Link... Error: {e}")