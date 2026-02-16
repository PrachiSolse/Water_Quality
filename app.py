import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# =========================================================
# 1. CONFIGURATION
# =========================================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZH2sKmRwJpILV5fDYn_gv07yPTE45gj9EkMPh_cCLBWckw2Q_oWb6DIxDvceRB1-jtA/exec"

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1BlROSLN7OLqbjxEuEfuFoZy8xWJPhUwN7L-VUgbAWjv_9fkdnw4jmm7W2v7xI40VUXFV3w-ogQJE/pub?output=csv"

# =========================================================
# 2. PAGE SETTINGS
# =========================================================
st.set_page_config(page_title="AI Water Intelligence", layout="wide")

# =========================================================
# 3. LOAD GOOGLE SHEET DATA (COLUMN SAFE)
# =========================================================
def load_data(url):
    df = pd.read_csv(url)

    # clean column names
    df.columns = df.columns.str.strip().str.lower()

    return df


# =========================================================
# 4. UI
# =========================================================
st.title("🌊 Smart Water Quality AI Portal")

col1, col2 = st.columns([1, 1.2])

# ================= INPUT PANEL =================
with col1:
    st.subheader("📥 Sensor Data Entry")

    with st.form("manual_entry"):
        val_ph = st.slider("pH Level", 0.0, 14.0, 7.2, step=0.1)
        val_tds = st.number_input("TDS (ppm)", value=250)
        val_turb = st.slider("Turbidity (NTU)", 0.0, 50.0, 2.0, step=0.1)
        val_temp = st.number_input("Temperature (°C)", value=25)

        submitted = st.form_submit_button("🚀 RUN AI ANALYSIS & SYNC")

# ================= AI REPORT =================
with col2:
    st.subheader("🧠 AI Analysis Report")

    if submitted:

        # -------- Sync to Google Sheet --------
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

        # -------- Water Quality Logic --------
        is_safe = (
            6.5 <= val_ph <= 8.5
            and val_tds <= 500
            and val_turb <= 5
        )

        result_text = "SAFE FOR USE" if is_safe else "POOR / UNHEALTHY"

        # -------- ML Prediction --------
        try:
            df_hist = load_data(CSV_URL)

            if "tds" in df_hist.columns and len(df_hist) > 2:

                y = df_hist["tds"].values.reshape(-1, 1)
                x = np.arange(len(y)).reshape(-1, 1)

                model = LinearRegression().fit(x, y)

                future_pred = model.predict([[len(y) + 1]])[0][0]
                pred_msg = f"Next cycle estimate: **{future_pred:.2f} ppm**"

            else:
                pred_msg = "Not enough historical data."

        except:
            pred_msg = "Database connecting... Predicting stability."

        # -------- Remediation --------
        remedy = "Standard monitoring."

        if val_ph < 6.5:
            remedy = "Deploy Calcite Neutralizing Filter."
        elif val_tds > 500:
            remedy = "Activate Reverse Osmosis (RO) system."

        # -------- Display Report --------
        st.markdown(f"""
        ### ✅ Status: {result_text}

        **Future Outlook (ML Prediction):**  
        {pred_msg}

        **Safety Precaution:**  
        {"Levels stable." if is_safe else "Risk of contamination detected."}

        **Recommended Action:**  
        {remedy}
        """)

# =========================================================
# 5. HISTORICAL DATA VISUALIZATION
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