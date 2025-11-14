import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# -------- Page Config --------
st.set_page_config(page_title="Soil & Camera Sensor Dashboard", layout="wide")

# -------- Sidebar Navigation --------
st.sidebar.title("🌿 Sensor Dashboard")
page = st.sidebar.radio("Select Sensor", ["Sensor 1", "Sensor 2", "Camera Sensor"])

# -------- Load CSV --------
@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

# -------- File Paths --------
sensor1_file = "data/soil_moisture_sensor_data_1.csv"
sensor2_file = "data/soil_moisture_sensor_data_2.csv"
camera_file = "data/plant_health_status.csv"


# -------------------------------------------------------------------------
# ------------------------ SHARED FUNCTIONS -------------------------------
# -------------------------------------------------------------------------

def vwc_status(value):
    """Return DRY / NORMAL / WET based on vwc_percent."""
    if value < 80:
        return "DRY 🌵"
    elif value > 80:
        return "WET 💧"
    return "NORMAL 🌿"


def show_sensor_page(df, title):
    st.title(title)

    df['gateway_timestamp'] = pd.to_datetime(df['gateway_timestamp'])

    selected_cols = [
        'gateway_timestamp', 'raw_adc', 'vwc_percent',
        'rssi_dbm', 'distance_m', 'battery_voltage', 'soc_percent'
    ]
    df = df[selected_cols]

    # --- Cards: Highest & Lowest raw_adc and vwc_percent ---
    if not df.empty:
        highest_vwc = df['vwc_percent'].max()
        lowest_vwc = df['vwc_percent'].min()

        # Add 5 columns including avg card
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("💧 Highest vwc_percent", f"{highest_vwc:.2f}%")
        with c2:
            st.metric("🏜️ Lowest vwc_percent", f"{lowest_vwc:.2f}%")

        # --- Average vwc card ---
        avg_vwc = df['vwc_percent'].mean()
        status = vwc_status(avg_vwc)

        with c3:
            st.metric("🌡️ Average vwc_percent", f"{avg_vwc:.2f}%", status)

    # --- Date range filter ---
    min_date, max_date = df['gateway_timestamp'].min(), df['gateway_timestamp'].max()
    default_start = max(min_date, max_date - timedelta(days=30))
    default_end = max_date

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[default_start.date(), default_end.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    df = df[
        (df['gateway_timestamp'].dt.date >= start_date)
        & (df['gateway_timestamp'].dt.date <= end_date)
    ]

    # --- Metric Selector ---
    metrics = ["raw_adc", "vwc_percent", "rssi_dbm", "distance_m", "battery_voltage", "soc_percent"]
    selected_metrics = st.multiselect("Choose metrics to plot:", metrics, default=metrics)

    # --- Plot ---
    df_melt = df.melt(id_vars='gateway_timestamp', value_vars=selected_metrics,
                      var_name='Metric', value_name='Value')

    fig = px.scatter(
        df_melt, x='gateway_timestamp', y='Value', color='Metric',
        title="Metrics Over Time", template='plotly_dark'
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        font=dict(color="white"),
        paper_bgcolor='rgba(17,17,17,1)',
        plot_bgcolor='rgba(17,17,17,1)',
        title_font=dict(size=22, family="Arial Black")
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------------
# --------------------------- MAIN PAGES ----------------------------------
# -------------------------------------------------------------------------

# --- Sensor 1 ---
if page == "Sensor 1":
    df1 = load_csv(sensor1_file)
    show_sensor_page(df1, "🌱 Soil Sensor 1 Data")


# --- Sensor 2 ---
elif page == "Sensor 2":
    df2 = load_csv(sensor2_file)
    show_sensor_page(df2, "🌾 Soil Sensor 2 Data")

# -------- Camera Sensor --------
elif page == "Camera Sensor":
    st.title("📷 Camera Sensor Data")

    df_camera = load_csv(camera_file)

    if "detected_object" in df_camera.columns:
        df_camera['detected_object'] = df_camera['detected_object'].astype(str).str.lower()

        categories = {
            'snail-infested crops': ['snail', 'snail infestation', 'infested', 'snail-infested'],
            'stressed crops': ['stressed', 'wilting', 'yellow', 'dehydrated', 'deficient'],
            'healthy crops': ['healthy', 'green', 'good', 'normal'],
            'dead crops': ['dead', 'dry', 'rotten', 'destroyed']
        }

        def categorize(obj):
            for cat, keywords in categories.items():
                if any(k in obj for k in keywords):
                    return cat
            return 'unclassified'

        df_camera['category'] = df_camera['detected_object'].apply(categorize)

        summary = (
            df_camera['category']
            .value_counts()
            .reindex(categories.keys(), fill_value=0)
            .reset_index()
        )
        summary.columns = ['Category', 'Count']

        summary['Count'] = pd.to_numeric(summary['Count'], errors='coerce').fillna(0)
        total = summary['Count'].sum()
        summary['Percentage'] = (summary['Count'] / total * 100).round(2) if total > 0 else 0

        fig_pie = px.pie(
            summary,
            names='Category',
            values='Count',
            title="Crop Health Status",
            color='Category',
            color_discrete_map={
                'healthy crops': '#00CC96',
                'stressed crops': '#FFA15A',
                'snail-infested crops': '#AB63FA',
                'dead crops': '#EF553B'
            },
            hole=0.3,
            template='plotly_dark'
        )

        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            font=dict(color="white"),
            paper_bgcolor='rgba(17,17,17,1)',
            plot_bgcolor='rgba(17,17,17,1)',
            title_font=dict(size=22, family="Arial Black")
        )

        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📊 Category Breakdown")
        st.dataframe(summary, use_container_width=True)

    else:
        st.warning("The 'detected_object' column was not found in the CSV file.")
