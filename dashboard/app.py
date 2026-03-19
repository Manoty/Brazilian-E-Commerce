import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Config ---
st.set_page_config(
    page_title="Olist Logistics Analytics",
    page_icon="📦",
    layout="wide"
)

# --- Connection ---
@st.cache_resource
def get_conn():
    return duckdb.connect("dev.duckdb", read_only=True)

@st.cache_data
def query(sql):
    conn = get_conn()
    return conn.execute(sql).df()

# --- Sidebar ---
st.sidebar.title("📦 Olist Analytics")
page = st.sidebar.radio("Navigate", [
    "Revenue Analysis",
    "Delivery Performance",
    "Customer LTV",
    "Seller Performance"
])

# --- Pages ---

if page == "Revenue Analysis":
    st.title("📈 Revenue Analysis")

    df = query("SELECT * FROM mart_revenue_analysis ORDER BY order_month")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"R$ {df['total_revenue'].sum():,.0f}")
    col2.metric("Total Orders", f"{df['total_orders'].sum():,.0f}")
    col3.metric("Avg Order Value", f"R$ {df['avg_order_value'].mean():,.2f}")

    st.subheader("Monthly Revenue")
    fig = px.bar(df, x="order_month", y="total_revenue",
                 labels={"order_month": "Month", "total_revenue": "Revenue (BRL)"},
                 color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Monthly Orders")
        fig2 = px.line(df, x="order_month", y="total_orders",
                       markers=True,
                       labels={"order_month": "Month", "total_orders": "Orders"})
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Avg Order Value Over Time")
        fig3 = px.line(df, x="order_month", y="avg_order_value",
                       markers=True,
                       labels={"order_month": "Month", "avg_order_value": "AOV (BRL)"},
                       color_discrete_sequence=["#EF553B"])
        st.plotly_chart(fig3, use_container_width=True)


elif page == "Delivery Performance":
    st.title("🚚 Delivery Performance")

    df = query("SELECT * FROM mart_delivery_performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", f"{df['total_orders'].sum():,.0f}")
    col2.metric("Avg Days to Deliver", f"{df['avg_days_to_deliver'].mean():,.1f}")
    col3.metric("Overall Late Rate", f"{df['late_orders'].sum() / df['total_orders'].sum() * 100:,.1f}%")

    st.subheader("Late Delivery Rate by Customer State")
    state_df = df.groupby("customer_state").agg(
        total_orders=("total_orders", "sum"),
        late_orders=("late_orders", "sum")
    ).reset_index()
    state_df["late_rate_pct"] = (state_df["late_orders"] / state_df["total_orders"] * 100).round(2)
    state_df = state_df.sort_values("late_rate_pct", ascending=False)

    fig = px.bar(state_df, x="customer_state", y="late_rate_pct",
                 labels={"customer_state": "State", "late_rate_pct": "Late Rate (%)"},
                 color="late_rate_pct", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Actual vs Estimated Delivery Days by State")
    delivery_df = df.groupby("customer_state").agg(
        avg_days_to_deliver=("avg_days_to_deliver", "mean"),
        avg_days_estimated=("avg_days_estimated", "mean")
    ).reset_index().sort_values("avg_days_to_deliver", ascending=False).head(15)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Actual", x=delivery_df["customer_state"], y=delivery_df["avg_days_to_deliver"]))
    fig2.add_trace(go.Bar(name="Estimated", x=delivery_df["customer_state"], y=delivery_df["avg_days_estimated"]))
    fig2.update_layout(barmode="group", xaxis_title="State", yaxis_title="Days")
    st.plotly_chart(fig2, use_container_width=True)


elif page == "Customer LTV":
    st.title("👥 Customer Lifetime Value")

    df = query("SELECT * FROM mart_customer_ltv")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{len(df):,.0f}")
    col2.metric("Avg Total Spent", f"R$ {df['total_spent'].mean():,.2f}")
    col3.metric("Avg Review Score", f"{df['avg_review_score'].mean():,.2f}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("LTV Segment Distribution")
        seg_df = df["ltv_segment"].value_counts().reset_index()
        seg_df.columns = ["segment", "count"]
        fig = px.pie(seg_df, names="segment", values="count",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Customers by Spend")
        top_df = df.nlargest(10, "total_spent")[["customer_unique_id", "state", "total_spent", "total_orders"]]
        st.dataframe(top_df, use_container_width=True)

    st.subheader("Spend Distribution")
    fig2 = px.histogram(df, x="total_spent", nbins=50,
                        labels={"total_spent": "Total Spent (BRL)"},
                        color_discrete_sequence=["#00CC96"])
    st.plotly_chart(fig2, use_container_width=True)


elif page == "Seller Performance":
    st.title("🏪 Seller Performance")

    df = query("SELECT * FROM mart_seller_performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sellers", f"{len(df):,.0f}")
    col2.metric("Avg Revenue per Seller", f"R$ {df['total_revenue'].mean():,.0f}")
    col3.metric("Avg Late Delivery Rate", f"{df['late_delivery_rate_pct'].mean():,.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Seller Tier Distribution")
        tier_df = df["seller_tier"].value_counts().reset_index()
        tier_df.columns = ["tier", "count"]
        fig = px.pie(tier_df, names="tier", values="count",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Sellers by Revenue")
        top_df = df.nlargest(10, "total_revenue")[["seller_id", "seller_state", "total_revenue", "late_delivery_rate_pct"]]
        st.dataframe(top_df, use_container_width=True)

    st.subheader("Revenue vs Late Delivery Rate")
    fig2 = px.scatter(df, x="total_revenue", y="late_delivery_rate_pct",
                      color="seller_tier", hover_data=["seller_id", "seller_state"],
                      labels={"total_revenue": "Revenue (BRL)", "late_delivery_rate_pct": "Late Rate (%)"},
                      color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig2, use_container_width=True)