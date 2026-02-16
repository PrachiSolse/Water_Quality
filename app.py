import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# =========================================================
# CONFIGURATION
# =========================================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZH2sKmRwJpILV5fDYn_gv07yPTE45gj9EkMPh_cCLBWckw2Q_oWb6DIxDvceRB1-jtA/exec"

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1BlROSLN7OLqbjxEuEfuFoZy8xWJPhUwN7L-VUgbAWjv_9fkdnw4jmm7W2v7xI40VUXFV3w-ogQJE/pub?output=csv"

# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(
    page_title="AI Water Intelligence",
    layout="wide"
)

# =========================================================
# PREMIUM CSS DESIGN
# =========================================================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1 {
    text-align:center;
    color:white;
    font-weight:700;
}

/* Glass Card */
.glass-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    border-radius:18px;
    padding:25px;
    border:1px solid rgba(255,255,255,0.2);
    box-shadow:0 8px 32px rgba(0,0,0,0.35);
}

/* Report Card */
.report-card {
    background: linear-gradient(145deg,#ffffff,#f1f5f9);
    border-radius:20px;
    padding:25px;
    box-shadow:0 12px 30px rgba(0,0,0,0.35);
    border-left:8px solid #00c6ff;
    color:#111111 !important;   /* FIX TEXT COLOR */
}

/* FORCE ALL TEXT INSIDE CARD TO BE DARK */
.report-card p,
.report-card div,
.report-card span,
.report-card b {
    color:#111111 !important;
}

/* Labels */
label, p, span {
    color:white !important;
    font-weight:600 !important;
}

/* Button */
.stButton>button {
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    border-radius:12px;
    height:3em;
    font-size:16px;
    font-weight:700;
    border:none;
    transition:0.3s;
}

.stButton>button:hover {
    transform:scale(1.05);
    box-shadow:0 6px 20px rgba(0,114,255,0.6);
}

/* Status Colors */
.status-good {
    color:#00e676;
    font-size:2rem;
    font-weight:800;
}

.status-bad {
    color:#ff5252;
    font-size:2rem;
    font-weight:800;
}

/* Form Styling */
[data-testid="stForm"] {
    background:rgba(255,255,255,0.06);
    backdrop-filter:blur(10px);
    border-radius:15px;
    padding:25px;
    border:1px solid rgba(255,255,255,0.2);
}

/* Chart box */
[data-testid="stLineChart"] {
    background:rgba(255,255,255,0.05);
    padding:15px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADER
# =========================================================
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    return df

# =========================================================
# TITLE
# =========================================================
st.title("🌊 AI Smart Water Quality Intelligence Dashboard")

col1, col2 = st.columns([1, 1.2])

# =========================================================
# INPUT PANEL
# =========================================================
with col1:
    st.subheader("📥 Sensor Data Entry")

    with st.form("manual_entry"):
        val_ph = st.slider("pH Level", 0.0, 14.0, 7.2, step=0.1)
        val_tds = st.number_input("TDS (ppm)", value=250)
        val_turb = st.slider("Turbidity (NTU)", 0.0, 50.0, 2.0, step=0.1)
        val_temp = st.number_input("Temperature (°C)", value=25)

        submitted = st.form_submit_button("🚀 RUN AI ANALYSIS & SYNC")

# =========================================================
# AI ANALYSIS
# =========================================================
with col2:
    st.subheader("🧠 AI Analysis Report")

    if submitted:

        # -------- GOOGLE SHEET SYNC --------
        try:
            requests.post(
                SCRIPT_URL,
                json={
                    "ph": val_ph,
                    "tds": val_tds,
                    "turbidity": val_turb,
                    "temperature": val_temp
                },
                timeout=3
            )
            st.success("✅ Cloud Database Synced Successfully")
        except:
            st.error("❌ Sync Failed. Check Script URL.")

        # -------- QUALITY CHECK --------
        is_safe = (
            6.5 <= val_ph <= 8.5
            and val_tds <= 500
            and val_turb <= 5
        )

        result_text = "SAFE FOR USE" if is_safe else "POOR / UNHEALTHY"
        status_class = "status-good" if is_safe else "status-bad"

        # -------- ML TREND PREDICTION --------
        try:
            df_hist = load_data(CSV_URL)

            if "tds" in df_hist.columns and len(df_hist) > 2:
                y = df_hist["tds"].values.reshape(-1,1)
                x = np.arange(len(y)).reshape(-1,1)

                model = LinearRegression().fit(x,y)
                future_pred = model.predict([[len(y)+1]])[0][0]

                pred_msg = f"Next cycle estimate: <b>{future_pred:.2f} ppm</b>"
            else:
                pred_msg = "Not enough historical data."

        except:
            pred_msg = "Database connecting..."

        # -------- REMEDIATION --------
        remedy = "Standard monitoring."

        if val_ph < 6.5:
            remedy = "Deploy Calcite Neutralizing Filter."
        elif val_tds > 500:
            remedy = "Activate Reverse Osmosis (RO) system."

        # -------- DISPLAY CARD --------
        st.markdown(f"""
        <div class="report-card">
            <div class="{status_class}">{result_text}</div>
            <hr>
            <p><b>Future Outlook (ML):</b><br>{pred_msg}</p>
            <hr>
            <p><b>Safety:</b><br>
            {"Levels stable." if is_safe else "Risk of contamination detected."}</p>
            <hr>
            <p><b>Recommended Action:</b><br>{remedy}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# HISTORICAL DATA VISUALIZATION
# =========================================================
st.divider()
st.subheader("📊 Data Historical Study (AI Dataset)")

try:
    df_plot = load_data(CSV_URL)

    required_cols = ["ph", "tds", "turbidity"]

    available_cols = [c for c in required_cols if c in df_plot.columns]

    if not df_plot.empty and available_cols:
        st.line_chart(df_plot[available_cols])
    else:
        st.warning("Google Sheet has no usable data yet.")

except Exception as e:
    st.error(f"Waiting for Google Sheet CSV Link... Error: {e}")