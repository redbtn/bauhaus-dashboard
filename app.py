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

# -------- Reusable Chart Function --------
def plot_soil_sensor(df, title):
    # Convert timestamp
    df['gateway_timestamp'] = pd.to_datetime(df['gateway_timestamp'])
    df = df.sort_values('gateway_timestamp')

    # Date range filter
    min_date = df['gateway_timestamp'].min().date()
    max_date = df['gateway_timestamp'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range", [min_date, max_date],
        min_value=min_date, max_value=max_date
    )
    if len(date_range) == 2:
        start, end = date_range
        df = df[(df['gateway_timestamp'].dt.date >= start) & (df['gateway_timestamp'].dt.date <= end)]

    # Metric selector
    metrics = ["raw_adc", "vwc_percent", "rssi_dbm", "distance_m", "battery_voltage", "soc_percent"]
    selected_metrics = st.multiselect("Choose metrics to plot:", metrics, default=metrics)

    # Prepare data for Plotly
    df_melt = df.melt(id_vars=['gateway_timestamp'], value_vars=selected_metrics,
                      var_name='Metric', value_name='Value')

    # Plot
    fig = px.scatter(
        df_melt,
        x='gateway_timestamp',
        y='Value',
        color='Metric',
        symbol='Metric',
        title="Metrics Over Time",
        template='plotly_dark'
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        title_font=dict(size=22, family="Arial Black"),
        xaxis_title="Time",
        yaxis_title="Value",
        legend_title="Metric",
        hovermode="x unified",
        plot_bgcolor='rgba(17,17,17,1)',
        paper_bgcolor='rgba(17,17,17,1)',
        font=dict(color="white"),
        margin=dict(t=80, l=40, r=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Sensor 1 ---
if page == "Sensor 1":
    st.title("🌱 Soil Sensor 1 Data Dashboard")

    df1 = load_csv(sensor1_file)
    df1['gateway_timestamp'] = pd.to_datetime(df1['gateway_timestamp'])

    selected_cols = [
        'gateway_timestamp', 'raw_adc', 'vwc_percent',
        'rssi_dbm', 'distance_m', 'battery_voltage', 'soc_percent'
    ]
    df1 = df1[selected_cols]

    # --- Cards: Highest & Lowest raw_adc and vwc_percent ---
    if not df1.empty:
        highest_adc = df1['raw_adc'].max()
        lowest_adc = df1['raw_adc'].min()
        highest_vwc = df1['vwc_percent'].max()
        lowest_vwc = df1['vwc_percent'].min()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔺 Highest raw_adc", f"{highest_adc:.2f}")
        with c2:
            st.metric("🔻 Lowest raw_adc", f"{lowest_adc:.2f}")
        with c3:
            st.metric("💧 Highest vwc_percent", f"{highest_vwc:.2f}%")
        with c4:
            st.metric("🏜️ Lowest vwc_percent", f"{lowest_vwc:.2f}%")

    # --- Date range filter ---
    min_date, max_date = df1['gateway_timestamp'].min(), df1['gateway_timestamp'].max()
    default_start = max(min_date, max_date - timedelta(days=30))
    default_end = max_date

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[default_start.date(), default_end.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    df1 = df1[
        (df1['gateway_timestamp'].dt.date >= start_date)
        & (df1['gateway_timestamp'].dt.date <= end_date)
    ]

    # --- Plot ---
    df1_melt = df1.melt(id_vars='gateway_timestamp', var_name='Metric', value_name='Value')
    fig = px.scatter(
        df1_melt, x='gateway_timestamp', y='Value', color='Metric',
        title="Metrics Over Time", template='plotly_dark'
    )
    fig.update_layout(
        font=dict(color="white"),
        paper_bgcolor='rgba(17,17,17,1)',
        plot_bgcolor='rgba(17,17,17,1)',
        title_font=dict(size=22, family="Arial Black")
    )
    st.plotly_chart(fig, use_container_width=True)


# --- Sensor 2 ---
elif page == "Sensor 2":
    st.title("🌾 Soil Sensor 2 Data Dashboard")

    df2 = load_csv(sensor2_file)
    df2['gateway_timestamp'] = pd.to_datetime(df2['gateway_timestamp'])

    selected_cols = [
        'gateway_timestamp', 'raw_adc', 'vwc_percent',
        'rssi_dbm', 'distance_m', 'battery_voltage', 'soc_percent'
    ]
    df2 = df2[selected_cols]

    # --- Cards: Highest & Lowest raw_adc and vwc_percent ---
    if not df2.empty:
        highest_adc = df2['raw_adc'].max()
        lowest_adc = df2['raw_adc'].min()
        highest_vwc = df2['vwc_percent'].max()
        lowest_vwc = df2['vwc_percent'].min()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔺 Highest raw_adc", f"{highest_adc:.2f}")
        with c2:
            st.metric("🔻 Lowest raw_adc", f"{lowest_adc:.2f}")
        with c3:
            st.metric("💧 Highest vwc_percent", f"{highest_vwc:.2f}%")
        with c4:
            st.metric("🏜️ Lowest vwc_percent", f"{lowest_vwc:.2f}%")

    # --- Date range filter ---
    min_date, max_date = df2['gateway_timestamp'].min(), df2['gateway_timestamp'].max()
    default_start = max(min_date, max_date - timedelta(days=30))
    default_end = max_date

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[default_start.date(), default_end.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    df2 = df2[
        (df2['gateway_timestamp'].dt.date >= start_date)
        & (df2['gateway_timestamp'].dt.date <= end_date)
    ]

    # --- Plot ---
    df2_melt = df2.melt(id_vars='gateway_timestamp', var_name='Metric', value_name='Value')
    fig2 = px.scatter(
        df2_melt, x='gateway_timestamp', y='Value', color='Metric',
        title="Metrics Over Time", template='plotly_dark'
    )
    fig2.update_layout(
        font=dict(color="white"),
        paper_bgcolor='rgba(17,17,17,1)',
        plot_bgcolor='rgba(17,17,17,1)',
        title_font=dict(size=22, family="Arial Black")
    )
    st.plotly_chart(fig2, use_container_width=True)



# -------- Camera Sensor --------
elif page == "Camera Sensor":
    st.title("📷 Camera Sensor Data")

    df_camera = load_csv(camera_file)

    if "detected_object" in df_camera.columns:
        # Normalize text
        df_camera['detected_object'] = df_camera['detected_object'].astype(str).str.lower()

        # Define target categories
        categories = {
            'snail-infested crops': ['snail', 'snail infestation', 'infested', 'snail-infested'],
            'stressed crops': ['stressed', 'wilting', 'yellow', 'dehydrated', 'deficient'],
            'healthy crops': ['healthy', 'green', 'good', 'normal'],
            'dead crops': ['dead', 'dry', 'rotten', 'destroyed']
        }

        # Categorize data
        def categorize(obj):
            for cat, keywords in categories.items():
                if any(k in obj for k in keywords):
                    return cat
            return 'unclassified'

        df_camera['category'] = df_camera['detected_object'].apply(categorize)

        # Build summary DataFrame
        summary = (
            df_camera['category']
            .value_counts()
            .reindex(categories.keys(), fill_value=0)
            .reset_index()
        )
        summary.columns = ['Category', 'Count']  # ✅ ensure proper names

        # Convert count to numeric and calculate %
        summary['Count'] = pd.to_numeric(summary['Count'], errors='coerce').fillna(0)
        total = summary['Count'].sum()
        summary['Percentage'] = (summary['Count'] / total * 100).round(2) if total > 0 else 0

        # Plot pie chart
        fig_pie = px.pie(
            summary,
            names='Category',  # ✅ now exists
            values='Count',
            title="Crop Health Status Distribution",
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

        # Show breakdown
        st.subheader("📊 Category Breakdown")
        st.dataframe(summary, use_container_width=True)
    else:
        st.warning("The 'detected_object' column was not found in the CSV file.")

