"""
Customer Feedback Dashboard
----------------------------
A Streamlit dashboard that performs sentiment analysis on customer feedback
using TextBlob and visualizes results with Plotly.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from datetime import datetime
import io

# ------------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Feedback Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Custom CSS Styling
# ------------------------------------------------------------------
st.markdown("""
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Sentiment Analysis Function
# ------------------------------------------------------------------
def analyze_sentiment(text: str):
    """Return polarity, subjectivity, and label for a piece of text."""
    if not isinstance(text, str) or text.strip() == "":
        return 0.0, 0.0, "Neutral"

    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 3)
    subjectivity = round(blob.sentiment.subjectivity, 3)

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return polarity, subjectivity, label


@st.cache_data
def process_dataframe(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    """Apply sentiment analysis to every row of the dataframe."""
    results = df[text_col].apply(lambda x: pd.Series(analyze_sentiment(x)))
    results.columns = ["Polarity", "Subjectivity", "Sentiment"]
    return pd.concat([df.reset_index(drop=True), results], axis=1)


# ------------------------------------------------------------------
# Sidebar - Data Input
# ------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")
st.sidebar.markdown("### 1. Load Data")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Use sample data", "Upload CSV"],
)

df_raw = None

if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
else:
    df_raw = pd.read_csv("data/sample_feedback.csv", on_bad_lines="skip")

if df_raw is None:
    st.info("👈 Upload a CSV file from the sidebar, or select 'Use sample data' to get started.")
    st.stop()

st.sidebar.markdown("### 2. Column Mapping")
text_column = st.sidebar.selectbox(
    "Select the feedback/text column",
    options=df_raw.columns.tolist(),
    index=df_raw.columns.get_loc("feedback") if "feedback" in df_raw.columns else 0,
)

# ------------------------------------------------------------------
# Process Data
# ------------------------------------------------------------------
df = process_dataframe(df_raw, text_column)

st.sidebar.markdown("### 3. Filter")
sentiment_filter = st.sidebar.multiselect(
    "Filter by sentiment",
    options=["Positive", "Neutral", "Negative"],
    default=["Positive", "Neutral", "Negative"],
)
df_filtered = df[df["Sentiment"].isin(sentiment_filter)]

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown('<div class="main-header">📊 Customer Feedback Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Sentiment analysis of customer feedback using TextBlob '
    'and interactive visualizations powered by Plotly.</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# KPI Metrics Row
# ------------------------------------------------------------------
total = len(df_filtered)
pos = (df_filtered["Sentiment"] == "Positive").sum()
neu = (df_filtered["Sentiment"] == "Neutral").sum()
neg = (df_filtered["Sentiment"] == "Negative").sum()
avg_polarity = df_filtered["Polarity"].mean() if total else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Feedback", total)
col2.metric("😊 Positive", pos, f"{(pos/total*100):.1f}%" if total else "0%")
col3.metric("😐 Neutral", neu, f"{(neu/total*100):.1f}%" if total else "0%")
col4.metric("😞 Negative", neg, f"{(neg/total*100):.1f}%" if total else "0%")
col5.metric("Avg. Polarity", f"{avg_polarity:.2f}")

st.markdown("---")

# ------------------------------------------------------------------
# Charts Row 1 : Sentiment Distribution + Polarity Histogram
# ------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Sentiment Distribution")
    sentiment_counts = df_filtered["Sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["Sentiment", "Count"]

    color_map = {"Positive": "#22c55e", "Neutral": "#94a3b8", "Negative": "#ef4444"}

    fig_pie = px.pie(
        sentiment_counts,
        names="Sentiment",
        values="Count",
        color="Sentiment",
        color_discrete_map=color_map,
        hole=0.45,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.subheader("Polarity Score Distribution")
    fig_hist = px.histogram(
        df_filtered,
        x="Polarity",
        nbins=20,
        color="Sentiment",
        color_discrete_map=color_map,
    )
    fig_hist.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        bargap=0.05,
        xaxis_title="Polarity (-1 = Negative, +1 = Positive)",
        yaxis_title="Number of Feedback Entries",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ------------------------------------------------------------------
# Charts Row 2 : Product-wise sentiment (if column exists) + Polarity vs Subjectivity
# ------------------------------------------------------------------
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    possible_group_cols = [c for c in df_filtered.columns if c.lower() in ("product", "category", "department")]
    if possible_group_cols:
        group_col = possible_group_cols[0]
        st.subheader(f"Sentiment by {group_col.title()}")
        grouped = df_filtered.groupby([group_col, "Sentiment"]).size().reset_index(name="Count")
        fig_bar = px.bar(
            grouped,
            x=group_col,
            y="Count",
            color="Sentiment",
            color_discrete_map=color_map,
            barmode="stack",
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.subheader("Average Polarity")
        fig_bar = px.bar(
            x=["Average Polarity"],
            y=[avg_polarity],
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col4:
    st.subheader("Polarity vs Subjectivity")
    fig_scatter = px.scatter(
        df_filtered,
        x="Polarity",
        y="Subjectivity",
        color="Sentiment",
        color_discrete_map=color_map,
        hover_data=[text_column],
    )
    fig_scatter.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------------------------------
# Trend over time (if a date column exists)
# ------------------------------------------------------------------
date_cols = [c for c in df_filtered.columns if "date" in c.lower()]
if date_cols:
    date_col = date_cols[0]
    try:
        df_trend = df_filtered.copy()
        df_trend[date_col] = pd.to_datetime(df_trend[date_col])
        trend = df_trend.groupby([pd.Grouper(key=date_col, freq="D"), "Sentiment"]).size().reset_index(name="Count")

        st.subheader("Sentiment Trend Over Time")
        fig_trend = px.line(
            trend,
            x=date_col,
            y="Count",
            color="Sentiment",
            color_discrete_map=color_map,
            markers=True,
        )
        fig_trend.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_trend, use_container_width=True)
    except Exception:
        pass

st.markdown("---")

# ------------------------------------------------------------------
# Data Table + Download
# ------------------------------------------------------------------
st.subheader("📋 Detailed Feedback Table")
st.dataframe(
    df_filtered[[text_column, "Sentiment", "Polarity", "Subjectivity"] +
                [c for c in df_filtered.columns if c not in [text_column, "Sentiment", "Polarity", "Subjectivity"]]],
    use_container_width=True,
    height=350,
)

csv_buffer = io.StringIO()
df_filtered.to_csv(csv_buffer, index=False)

st.download_button(
    label="⬇️ Download Processed Data as CSV",
    data=csv_buffer.getvalue(),
    file_name=f"feedback_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.markdown("---")
st.caption("Built with Streamlit, TextBlob & Plotly | Customer Feedback Dashboard")
