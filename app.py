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
st.set_page_config(page_title="AI Water Intelligence", layout="wide")

# =========================================================
# PREMIUM CSS
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}

h1 { text-align:center; color:white; }

.report-card {
    background: linear-gradient(145deg,#ffffff,#f1f5f9);
    border-radius:20px;
    padding:25px;
    border-left:8px solid #00c6ff;
    color:#111 !important;
}

.report-card * { color:#111 !important; }

label,p,span { color:white !important; }

.status-good { color:#00e676; font-size:2rem; font-weight:800;}
.status-bad { color:#ff5252; font-size:2rem; font-weight:800;}

.stButton>button{
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    border-radius:12px;
    font-weight:700;
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
# ML PREDICTION FUNCTION
# =========================================================
def predict_parameter(df, column):
    if column not in df.columns or len(df) < 3:
        return None

    y = df[column].values.reshape(-1,1)
    x = np.arange(len(y)).reshape(-1,1)

    model = LinearRegression().fit(x,y)
    pred = model.predict([[len(y)+1]])[0][0]

    return round(pred,2)

# =========================================================
# WATER CLASSIFICATION LOGIC
# =========================================================
def water_analysis(ph, tds, turb):

    if 6.5<=ph<=8.5 and tds<=300 and turb<=5:
        return (
            "✅ Drinking & Domestic Use",
            "Safe for daily consumption.",
            "Regular monitoring only."
        )

    elif tds<=600:
        return (
            "🏠 Domestic Use Only",
            "Avoid direct drinking.",
            "Use RO/UV filtration before drinking."
        )

    elif tds<=1200:
        return (
            "🌱 Agriculture / Irrigation",
            "Not suitable for household usage.",
            "Sediment filtration recommended."
        )

    else:
        return (
            "❌ Industrial / Unsafe",
            "Health risk detected.",
            "Immediate RO + UV + Carbon treatment required."
        )

# =========================================================
# TITLE
# =========================================================
st.title("🌊 AI Smart Water Quality Intelligence Dashboard")

col1, col2 = st.columns([1,1.2])

# =========================================================
# INPUT PANEL
# =========================================================
with col1:

    st.subheader("📥 Sensor Data Entry")

    with st.form("manual_entry"):

        val_ph = st.slider("pH Level",0.0,14.0,7.2,step=0.1)
        val_tds = st.number_input("TDS (ppm)",value=250)
        val_turb = st.slider("Turbidity (NTU)",0.0,50.0,2.0,step=0.1)
        val_temp = st.number_input("Temperature (°C)",value=25)

        submitted = st.form_submit_button("🚀 RUN AI ANALYSIS & SYNC")

# =========================================================
# AI REPORT
# =========================================================
with col2:

    st.subheader("🧠 AI Analysis Report")

    if submitted:

        # ---------- CLOUD SYNC ----------
        try:
            requests.post(
                SCRIPT_URL,
                json={
                    "ph":val_ph,
                    "tds":val_tds,
                    "turbidity":val_turb,
                    "temperature":val_temp
                },timeout=3
            )
            st.success("✅ Cloud Database Synced Successfully")
        except:
            st.error("❌ Sync Failed")

        # ---------- LOAD HISTORY ----------
        try:
            df_hist = load_data(CSV_URL)

            pred_ph = predict_parameter(df_hist,"ph")
            pred_tds = predict_parameter(df_hist,"tds")
            pred_turb = predict_parameter(df_hist,"turbidity")
            pred_temp = predict_parameter(df_hist,"temperature")

        except:
            pred_ph=pred_tds=pred_turb=pred_temp=None

        # ---------- SAFETY ----------
        is_safe = (6.5<=val_ph<=8.5 and val_tds<=500 and val_turb<=5)

        status = "SAFE FOR USE" if is_safe else "POOR / UNHEALTHY"
        status_class = "status-good" if is_safe else "status-bad"

        # ---------- WATER USAGE ----------
        usage, precaution, remedy = water_analysis(
            pred_ph or val_ph,
            pred_tds or val_tds,
            pred_turb or val_turb
        )

        # ---------- DISPLAY ----------
        st.markdown(f"""
        <div class="report-card">

        <div class="{status_class}">{status}</div>
        <hr>

        <b>🔮 Predicted Parameters:</b><br>
        pH: {pred_ph}<br>
        TDS: {pred_tds} ppm<br>
        Turbidity: {pred_turb} NTU<br>
        Temperature: {pred_temp} °C

        <hr>

        <b>💧 Recommended Usage:</b><br>
        {usage}

        <hr>

        <b>⚠ Precautions:</b><br>
        {precaution}

        <hr>

        <b>🛠 Remedies:</b><br>
        {remedy}

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# HISTORICAL GRAPH
# =========================================================
st.divider()
st.subheader("📊 Historical Water Trends")

try:
    df_plot = load_data(CSV_URL)

    cols = ["ph","tds","turbidity","temperature"]
    cols = [c for c in cols if c in df_plot.columns]

    if cols:
        st.line_chart(df_plot[cols])
    else:
        st.warning("No usable columns found.")

except Exception as e:
    st.error(f"Waiting for Google Sheet CSV Link... {e}")