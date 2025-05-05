# app.py (Streamlit main app)
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import parse_csv
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Bank Statement Analyzer - Automated Insights", layout="wide")
st.title("Bank Statement Analyzer - Automated Insights")

uploaded_file = st.file_uploader("Upload your bank statement CSV", type=["csv"])
if not uploaded_file:
    st.info("Please upload a bank statement CSV to begin.")
    st.stop()

# Parse and preview data
df = parse_csv(uploaded_file)
st.subheader(" Raw Data Preview")
st.dataframe(df, use_container_width=True)

# Sidebar filters
st.sidebar.header("Filters")
all_columns = list(df.columns)

# Date column selection and filtering
date_column = st.sidebar.selectbox("Date column", all_columns)
df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
df = df.dropna(subset=[date_column])

date_min, date_max = df[date_column].min(), df[date_column].max()
datetime_range = st.sidebar.date_input("Select Date Range", [date_min.date(), date_max.date()])
if len(datetime_range) == 2:
    start_date = pd.to_datetime(datetime_range[0])
    end_date = pd.to_datetime(datetime_range[1])
    df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

# Identify numeric and categorical columns
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
if not numeric_cols:
    st.error("No numeric columns found for analysis.")
    st.stop()
categorical_cols = [c for c in all_columns if c not in numeric_cols + [date_column]]

# Automated Analysis Section
st.header("Automated Analysis")

# 1. Summary Statistics
st.subheader("1. Summary Statistics")
st.write(df[numeric_cols].describe().T)

# 2. Total Credits vs Debits
if "Type" in df.columns or "type" in df.columns:
    type_col = "Type" if "Type" in df.columns else "type"
    credits = df[df[type_col].str.lower() == "credit"][numeric_cols].sum()
    debits = df[df[type_col].str.lower() == "debit"][numeric_cols].sum()
    summary = pd.DataFrame({"Credit": credits, "Debit": debits})
    st.subheader("2. Total Credits vs Debits")
    st.write(summary)



# 3. Monthly Aggregation
st.subheader("3. Monthly Aggregation")
a_mount_col = st.sidebar.selectbox("Amount column for monthly aggregation", numeric_cols, key="month_amt")
df['AggMonth'] = df[date_column].dt.month
grouped = df.groupby('AggMonth', as_index=False)[[a_mount_col]].sum()
grouped.rename(columns={a_mount_col: f"Total_{a_mount_col}"}, inplace=True)
st.dataframe(grouped)

# 4. Top 5 Largest Transactions
st.subheader("4. Top 5 Largest Transactions")
top5 = df.nlargest(5, numeric_cols[0])[[date_column] + [numeric_cols[0]] + categorical_cols]
st.dataframe(top5)

# 5. Category Breakdown
if categorical_cols:
    st.subheader("5. Category Breakdown")
    for cat in categorical_cols:
        fig = px.bar(df.groupby(cat)[numeric_cols[0]].sum().reset_index(), x=cat, y=numeric_cols[0], title=f"Spending by {cat}")
        st.plotly_chart(fig)

# 6. Anomaly Detection (Z-Score)
st.subheader("6. Anomaly Detection (Z-Score)")
from scipy import stats
z_scores = stats.zscore(df[numeric_cols[0]].fillna(0))
df['z_score'] = z_scores
anomalies = df[abs(df['z_score']) > 3][[date_column, numeric_cols[0], 'z_score'] + categorical_cols]
st.write(anomalies)

# 7. Visualization Dashboard
st.header("Visualization Dashboard")
col1, col2 = st.columns(2)

# Available chart types
types = ["Bar", "Line", "Pie", "Scatter", "Area", "Histogram", "Box"]

with col1:
    st.markdown("**Chart Panel 1**")
    chart1 = st.selectbox("Chart 1 type", types, key="chart1_type")
    x1 = st.selectbox("X-axis Chart 1", all_columns, key='x1')
    y1 = st.selectbox("Y-axis Chart 1", numeric_cols, key='y1')
    # Build selected chart
    if chart1 == "Bar":
        fig1 = px.bar(df, x=x1, y=y1)
    elif chart1 == "Line":
        fig1 = px.line(df, x=x1, y=y1)
    elif chart1 == "Pie":
        fig1 = px.pie(df, names=x1, values=y1)
    elif chart1 == "Scatter":
        fig1 = px.scatter(df, x=x1, y=y1)
    elif chart1 == "Area":
        fig1 = px.area(df, x=x1, y=y1)
    elif chart1 == "Histogram":
        fig1 = px.histogram(df, x=x1)
    elif chart1 == "Box":
        fig1 = px.box(df, x=x1, y=y1)
    st.plotly_chart(fig1, use_container_width=True, key="vis1")

with col2:
    st.markdown("**Chart Panel 2**")
    chart2 = st.selectbox("Chart 2 type", types, key="chart2_type")
    x2 = st.selectbox("X-axis Chart 2", all_columns, key='x2')
    y2 = st.selectbox("Y-axis Chart 2", numeric_cols, key='y2')
    # Build selected chart
    if chart2 == "Bar":
        fig2 = px.bar(df, x=x2, y=y2)
    elif chart2 == "Line":
        fig2 = px.line(df, x=x2, y=y2)
    elif chart2 == "Pie":
        fig2 = px.pie(df, names=x2, values=y2)
    elif chart2 == "Scatter":
        fig2 = px.scatter(df, x=x2, y=y2)
    elif chart2 == "Area":
        fig2 = px.area(df, x=x2, y=y2)
    elif chart2 == "Histogram":
        fig2 = px.histogram(df, x=x2)
    elif chart2 == "Box":
        fig2 = px.box(df, x=x2, y=y2)
    st.plotly_chart(fig2, use_container_width=True, key="vis2")

