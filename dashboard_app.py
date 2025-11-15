import os
from datetime import datetime
import time

from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
from kafka import KafkaConsumer
import json
import threading

# Streamlit Setup
load_dotenv()

st.set_page_config(
    page_title="IoT Sensor Dashboard", layout="wide", initial_sidebar_state="expanded"
)
st.title("🌡️ Real-Time IoT Sensor Dashboard")

# Sidebar for settings
st.sidebar.title("⚙️ Settings")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 30, 5)
show_raw_data = st.sidebar.checkbox("Show raw data table", value=False)


# Database connection
def connect_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "airflow"),
        password=os.getenv("MYSQL_PASSWORD", "airflow"),
        database=os.getenv("MYSQL_DATABASE", "airflow_db"),
    )


def load_table(table_name, limit=None):
    try:
        conn = connect_db()
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
        else:
            query += ";"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error while reading {table_name}: {e}")
        return pd.DataFrame()


def get_latest_from_kafka(timeout_ms=5000, max_messages=200):
    """Get latest messages from Kafka - primary data source for real-time dashboard"""
    try:
        from kafka import TopicPartition

        topic_name = os.getenv("KAFKA_TOPIC_SENSOR_DATA", "iot_sensor_data")

        # Create consumer WITHOUT subscribing to topic (we'll assign manually)
        consumer = KafkaConsumer(
            bootstrap_servers=[os.getenv("KAFKA_BROKER", "localhost:9092")],
            auto_offset_reset="earliest",
            enable_auto_commit=False,  # Don't commit offsets
            group_id=None,  # No group needed - we'll manually assign partitions
            consumer_timeout_ms=timeout_ms,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

        messages = []

        # Get all partitions and assign them
        partitions = consumer.partitions_for_topic(topic_name)
        if not partitions:
            consumer.close()
            return pd.DataFrame()

        topic_partitions = [TopicPartition(topic_name, p) for p in partitions]
        consumer.assign(topic_partitions)

        # Seek to end minus max_messages for each partition
        for tp in topic_partitions:
            end_offset = consumer.end_offsets([tp])[tp]
            start_offset = max(0, end_offset - max_messages)
            consumer.seek(tp, start_offset)

        # Read messages
        for message in consumer:
            messages.append(message.value)
            if len(messages) >= max_messages:
                break

        consumer.close()

        # Sort messages by timestamp to get most recent
        if messages:
            df = pd.DataFrame(messages)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False).head(max_messages)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Kafka connection issue: {str(e)}")
        return pd.DataFrame()


# Auto-refresh logic
if auto_refresh:
    placeholder = st.empty()
    with placeholder.container():
        st.info(f"🔄 Auto-refreshing every {refresh_interval} seconds...")
    time.sleep(0.5)
    placeholder.empty()

# PRIMARY DATA SOURCE: Real-time Kafka stream
st.info("📡 Loading live data from Kafka stream...")
kafka_df = get_latest_from_kafka(timeout_ms=2000, max_messages=200)

# SECONDARY: Load historical data from DB (for comparison)
db_df = load_table("sensor_readings", limit=500)
avg_df = load_table("sensor_avg")

# Use Kafka as primary data source, fallback to DB if Kafka is empty
if not kafka_df.empty:
    df = kafka_df
    data_source = " LIVE: Kafka Stream"
    st.success(f" Using real-time Kafka data: {len(df)} messages")
else:
    df = db_df
    data_source = "Historical: Database"
    st.warning(
        " No live Kafka data - showing database records. Run Datagenerator.py to see live data!"
    )

# Status indicators
col_status1, col_status2, col_status3 = st.columns([1, 1, 2])
with col_status1:
    kafka_status = "🟢 Live" if not kafka_df.empty else "🟡 Waiting"
    st.metric("Kafka Stream", kafka_status)
with col_status2:
    db_status = "🟢 Connected" if not db_df.empty else "🔴 No Data"
    st.metric("Database", db_status)
with col_status3:
    st.metric("Data Source", data_source)

st.markdown("---")

if df.empty:
    st.error("❌ No data available from Kafka or Database!")
    st.info("💡 Run `python Datagenerator.py` to generate live data")
    st.stop()

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort by time
df = df.sort_values("timestamp", ascending=False)

# Extract alerts (using threshold from config)
TEMP_THRESHOLD = 45.0
df["alert"] = (df["temperature"] > TEMP_THRESHOLD).astype(int)

# KPIs section
col1, col2, col3, col4 = st.columns(4)

latest_temp = df.iloc[0]["temperature"]
latest_humidity = df.iloc[0]["humidity"]
temp_delta = latest_temp - df["temperature"].mean()
humidity_delta = latest_humidity - df["humidity"].mean()

col1.metric("Latest Temperature", f"{latest_temp:.1f} °C", f"{temp_delta:+.1f}°C")
col2.metric("Latest Humidity", f"{latest_humidity:.1f} %", f"{humidity_delta:+.1f}%")
col3.metric("Avg Temperature", f"{df['temperature'].mean():.2f} °C")
col4.metric("Alerts (>45°C)", int(df["alert"].sum()), delta_color="inverse")

st.markdown("---")


# Temperature & Humidity Time Series
st.subheader(" Sensor Readings Over Time")

# Prepare data for plotting (reverse to show oldest first in chart)
plot_df = df.sort_values("timestamp", ascending=True).tail(
    500
)  # Last 500 points for performance

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_temp = px.line(
        plot_df,
        x="timestamp",
        y="temperature",
        color="sensor_id",
        title=" Temperature Over Time",
        labels={"temperature": "Temperature (°C)", "timestamp": "Time"},
    )
    fig_temp.add_hline(
        y=TEMP_THRESHOLD,
        line_color="red",
        line_dash="dash",
        annotation_text=f"Alert Threshold ({TEMP_THRESHOLD}°C)",
    )
    fig_temp.update_layout(hovermode="x unified")
    st.plotly_chart(fig_temp, use_container_width=True)

with col_chart2:
    fig_hum = px.line(
        plot_df,
        x="timestamp",
        y="humidity",
        color="sensor_id",
        title=" Humidity Over Time",
        labels={"humidity": "Humidity (%)", "timestamp": "Time"},
    )
    fig_hum.add_hline(
        y=85,
        line_color="orange",
        line_dash="dash",
        annotation_text="Alert Threshold (85%)",
    )
    fig_hum.update_layout(hovermode="x unified")
    st.plotly_chart(fig_hum, use_container_width=True)


# Gauges for Latest Readings
st.subheader(" Current Readings")

col_gauge1, col_gauge2 = st.columns(2)

with col_gauge1:
    current_temp = float(df.iloc[0]["temperature"])
    gauge_temp = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=current_temp,
            delta={"reference": df["temperature"].mean()},
            title={"text": "Current Temperature (°C)"},
            gauge={
                "axis": {"range": [0, 60]},
                "bar": {
                    "color": "darkred" if current_temp > TEMP_THRESHOLD else "darkblue"
                },
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": TEMP_THRESHOLD,
                },
                "steps": [
                    {"range": [0, 30], "color": "lightblue"},
                    {"range": [30, 45], "color": "lightyellow"},
                    {"range": [45, 60], "color": "lightcoral"},
                ],
            },
        )
    )
    st.plotly_chart(gauge_temp, use_container_width=True)

with col_gauge2:
    current_hum = float(df.iloc[0]["humidity"])
    gauge_hum = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=current_hum,
            delta={"reference": df["humidity"].mean()},
            title={"text": "Current Humidity (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkorange" if current_hum > 85 else "darkgreen"},
                "threshold": {
                    "line": {"color": "orange", "width": 4},
                    "thickness": 0.75,
                    "value": 85,
                },
                "steps": [
                    {"range": [0, 60], "color": "lightgreen"},
                    {"range": [60, 85], "color": "lightyellow"},
                    {"range": [85, 100], "color": "lightcoral"},
                ],
            },
        )
    )
    st.plotly_chart(gauge_hum, use_container_width=True)


# Average Summary and Recent Alerts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(" Average Values By Sensor")
    if not avg_df.empty:
        # Format the dataframe
        display_avg = avg_df.copy()
        display_avg["avg_temperature"] = display_avg["avg_temperature"].apply(
            lambda x: f"{x:.2f}°C"
        )
        display_avg["avg_humidity"] = display_avg["avg_humidity"].apply(
            lambda x: f"{x:.2f}%"
        )
        st.dataframe(display_avg, use_container_width=True, hide_index=True)
    else:
        st.info("No average data found yet (sensor_avg table is empty).")

with col_right:
    st.subheader(" Recent Alerts")
    alert_df = df[df["alert"] == 1].head(10)
    if not alert_df.empty:
        alert_display = alert_df[
            ["timestamp", "sensor_id", "temperature", "humidity"]
        ].copy()
        alert_display["timestamp"] = alert_display["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        st.dataframe(alert_display, use_container_width=True)
    else:
        st.success(" No recent alerts - all readings within normal range!")

# Raw data table (optional)
if show_raw_data:
    st.subheader(" Raw Data Table")
    display_df = df.head(100).copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(display_df, use_container_width=True)

# Footer with stats
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.caption(
        f" Last DB Update: {df.iloc[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
    )
with col_footer2:
    st.caption(f" Total Records: {len(df):,}")
with col_footer3:
    st.caption(f" Dashboard Refresh: {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh trigger
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
