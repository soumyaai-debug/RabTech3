import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Executive Retail Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('clean_dataset.csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Order_Date'].min(), df['Order_Date'].max()),
    min_value=df['Order_Date'].min(),
    max_value=df['Order_Date'].max()
)

categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Filter Dataset
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[(df['Order_Date'] >= start_date) & (df['Order_Date'] <= end_date) & (df['Category'].isin(categories))]
else:
    filtered_df = df[df['Category'].isin(categories)]

# Dashboard Title
st.title("📊 Executive Retail & E-Commerce KPI Dashboard")
st.markdown("Real-time operational metrics, profit performance, and category dynamics.")

# Top Executive KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = filtered_df['Total_Revenue'].sum()
total_orders = filtered_df['Order_ID'].nunique()
avg_order_val = filtered_df['Total_Revenue'].mean()
total_profit = filtered_df['Gross_Profit'].sum()
avg_margin = filtered_df['Profit_Margin_Pct'].mean()

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Avg Order Value (AOV)", f"${avg_order_val:,.2f}")
col4.metric("Gross Profit", f"${total_profit:,.2f}")
col5.metric("Avg Profit Margin", f"{avg_margin:.1f}%")

st.markdown("---")

# Row 1: Revenue Trend Area Chart & Profitability by Category
col_a, col_b = st.columns([2, 1])

with col_a:
    st.subheader("📈 Monthly Revenue & Profit Trend")
    monthly_df = filtered_df.groupby(filtered_df['Order_Date'].dt.to_period('M'))[['Total_Revenue', 'Gross_Profit']].sum().reset_index()
    monthly_df['Order_Date'] = monthly_df['Order_Date'].dt.to_timestamp()
    
    fig_trend = px.area(
        monthly_df, 
        x='Order_Date', 
        y=['Total_Revenue', 'Gross_Profit'],
        labels={'value': 'Amount ($)', 'Order_Date': 'Month', 'variable': 'Metric'},
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_b:
    st.subheader("🏷️ Category Revenue Share")
    cat_df = filtered_df.groupby('Category')['Total_Revenue'].sum().reset_index()
    fig_pie = px.pie(
        cat_df, 
        names='Category', 
        values='Total_Revenue',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Category Breakdown & Order Quantity Distribution
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("📊 Category Gross Profit Performance")
    cat_profit = filtered_df.groupby('Category')[['Gross_Profit', 'Total_Cost']].sum().reset_index()
    fig_bar = px.bar(
        cat_profit, 
        x='Category', 
        y=['Gross_Profit', 'Total_Cost'],
        barmode='group',
        labels={'value': 'Amount ($)', 'Category': 'Product Category'},
        color_discrete_sequence=['#2ca02c', '#d62728']
    )
    fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_d:
    st.subheader("📦 Quantity per Order Distribution")
    fig_hist = px.histogram(
        filtered_df, 
        x='Quantity', 
        nbins=10,
        color='Category',
        labels={'Quantity': 'Items per Order', 'count': 'Transaction Count'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_hist.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_hist, use_container_width=True)

# Detailed Data Table
st.subheader("📋 Drill-Down Transaction Explorer")
st.dataframe(filtered_df.sort_values(by='Order_Date', ascending=False).head(100), use_container_width=True)
