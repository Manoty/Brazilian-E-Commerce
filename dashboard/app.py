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

# --- Load base data once ---
@st.cache_data
def load_all():
    revenue_df     = query("SELECT * FROM mart_revenue_analysis ORDER BY order_month")
    delivery_df    = query("SELECT * FROM mart_delivery_performance")
    ltv_df         = query("SELECT * FROM mart_customer_ltv")
    seller_df      = query("SELECT * FROM mart_seller_performance")
    orders_df      = query("SELECT order_id, order_status, ordered_at FROM fct_orders")
    return revenue_df, delivery_df, ltv_df, seller_df, orders_df

revenue_df, delivery_df, ltv_df, seller_df, orders_df = load_all()

# --- Sidebar ---
st.sidebar.image("https://img.icons8.com/color/96/box.png", width=60)
st.sidebar.title("Filters")
st.sidebar.markdown("---")

# --- Top nav ---
st.title("📦 Olist Logistics Analytics")
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Revenue",
    "🚚 Delivery Performance",
    "👥 Customer LTV",
    "🏪 Seller Performance"
])


# ============================================================
# TAB 1 — REVENUE
# ============================================================
with tab1:

    # sidebar filters for this tab
    st.sidebar.markdown("### 📈 Revenue Filters")
    min_date = revenue_df["order_month"].min()
    max_date = revenue_df["order_month"].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="rev_date"
    )

    # apply filter
    df = revenue_df.copy()
    if len(date_range) == 2:
        df = df[(df["order_month"] >= pd.Timestamp(date_range[0])) &
                (df["order_month"] <= pd.Timestamp(date_range[1]))]

    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"R$ {df['total_revenue'].sum():,.0f}")
    col2.metric("Total Orders", f"{df['total_orders'].sum():,.0f}")
    col3.metric("Unique Customers", f"{df['unique_customers'].sum():,.0f}")
    col4.metric("Avg Order Value", f"R$ {df['avg_order_value'].mean():,.2f}")

    st.divider()

    st.subheader("Monthly Revenue")
    fig = px.bar(df, x="order_month", y="total_revenue",
                 labels={"order_month": "Month", "total_revenue": "Revenue (BRL)"},
                 color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Order Volume")
    fig2 = px.line(df, x="order_month", y="total_orders", markers=True,
                   labels={"order_month": "Month", "total_orders": "Orders"},
                   color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Average Order Value Over Time")
    fig3 = px.line(df, x="order_month", y="avg_order_value", markers=True,
                   labels={"order_month": "Month", "avg_order_value": "AOV (BRL)"},
                   color_discrete_sequence=["#00CC96"])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Revenue per Customer Over Time")
    fig4 = px.line(df, x="order_month", y="revenue_per_customer", markers=True,
                   labels={"order_month": "Month", "revenue_per_customer": "Rev per Customer (BRL)"},
                   color_discrete_sequence=["#AB63FA"])
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Unique Customers per Month")
    fig5 = px.bar(df, x="order_month", y="unique_customers",
                  labels={"order_month": "Month", "unique_customers": "Customers"},
                  color_discrete_sequence=["#FFA15A"])
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Revenue vs Order Volume Correlation")
    fig6 = px.scatter(df, x="total_orders", y="total_revenue",
                      size="unique_customers", hover_data=["order_month"],
                      labels={"total_orders": "Orders", "total_revenue": "Revenue (BRL)"},
                      color_discrete_sequence=["#19D3F3"])
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Monthly Revenue Data")
    st.dataframe(df, use_container_width=True)


# ============================================================
# TAB 2 — DELIVERY PERFORMANCE
# ============================================================
with tab2:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚚 Delivery Filters")

    all_customer_states = sorted(delivery_df["customer_state"].dropna().unique().tolist())
    selected_customer_states = st.sidebar.multiselect(
        "Customer State",
        options=all_customer_states,
        default=all_customer_states,
        key="del_cust_state"
    )

    all_seller_states = sorted(delivery_df["seller_state"].dropna().unique().tolist())
    selected_seller_states = st.sidebar.multiselect(
        "Seller State",
        options=all_seller_states,
        default=all_seller_states,
        key="del_sell_state"
    )

    # apply filters
    df = delivery_df.copy()
    df = df[df["customer_state"].isin(selected_customer_states)]
    df = df[df["seller_state"].isin(selected_seller_states)]

    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{df['total_orders'].sum():,.0f}")
    col2.metric("Total Late Orders", f"{df['late_orders'].sum():,.0f}")
    col3.metric("Overall Late Rate",
                f"{df['late_orders'].sum() / df['total_orders'].sum() * 100:,.1f}%" if df['total_orders'].sum() > 0 else "N/A")
    col4.metric("Avg Days to Deliver", f"{df['avg_days_to_deliver'].mean():,.1f}")

    st.divider()

    # aggregate by customer state
    state_df = df.groupby("customer_state").agg(
        total_orders=("total_orders", "sum"),
        late_orders=("late_orders", "sum"),
        avg_days_to_deliver=("avg_days_to_deliver", "mean"),
        avg_days_estimated=("avg_days_estimated", "mean")
    ).reset_index()
    state_df["late_rate_pct"] = (state_df["late_orders"] / state_df["total_orders"] * 100).round(2)
    state_df["delivery_gap"] = (state_df["avg_days_to_deliver"] - state_df["avg_days_estimated"]).round(2)

    st.subheader("Late Delivery Rate by Customer State")
    fig = px.bar(state_df.sort_values("late_rate_pct", ascending=False),
                 x="customer_state", y="late_rate_pct",
                 color="late_rate_pct", color_continuous_scale="Reds",
                 labels={"customer_state": "State", "late_rate_pct": "Late Rate (%)"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Total Orders by Customer State")
    fig2 = px.bar(state_df.sort_values("total_orders", ascending=False),
                  x="customer_state", y="total_orders",
                  color_discrete_sequence=["#636EFA"],
                  labels={"customer_state": "State", "total_orders": "Orders"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Actual vs Estimated Delivery Days by State (Top 20)")
    top20 = state_df.sort_values("avg_days_to_deliver", ascending=False).head(20)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Actual Days", x=top20["customer_state"], y=top20["avg_days_to_deliver"]))
    fig3.add_trace(go.Bar(name="Estimated Days", x=top20["customer_state"], y=top20["avg_days_estimated"]))
    fig3.update_layout(barmode="group", xaxis_title="State", yaxis_title="Days")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Delivery Gap — Actual minus Estimated Days")
    fig4 = px.bar(state_df.sort_values("delivery_gap", ascending=False),
                  x="customer_state", y="delivery_gap",
                  color="delivery_gap", color_continuous_scale="RdYlGn_r",
                  labels={"customer_state": "State", "delivery_gap": "Gap (Days)"})
    st.plotly_chart(fig4, use_container_width=True)

    # aggregate by seller state
    seller_state_df = df.groupby("seller_state").agg(
        total_orders=("total_orders", "sum"),
        late_orders=("late_orders", "sum"),
    ).reset_index()
    seller_state_df["late_rate_pct"] = (seller_state_df["late_orders"] / seller_state_df["total_orders"] * 100).round(2)

    st.subheader("Late Delivery Rate by Seller State")
    fig5 = px.bar(seller_state_df.sort_values("late_rate_pct", ascending=False),
                  x="seller_state", y="late_rate_pct",
                  color="late_rate_pct", color_continuous_scale="Oranges",
                  labels={"seller_state": "Seller State", "late_rate_pct": "Late Rate (%)"})
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Order Volume by Seller State")
    fig6 = px.bar(seller_state_df.sort_values("total_orders", ascending=False),
                  x="seller_state", y="total_orders",
                  color_discrete_sequence=["#EF553B"],
                  labels={"seller_state": "Seller State", "total_orders": "Orders"})
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Late Orders Heatmap — Customer State vs Seller State")
    pivot = df.pivot_table(index="customer_state", columns="seller_state",
                           values="late_delivery_rate_pct", aggfunc="mean").fillna(0)
    fig7 = px.imshow(pivot, color_continuous_scale="Reds",
                     labels={"color": "Late Rate (%)"})
    fig7.update_layout(height=600)
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Raw Delivery Data")
    st.dataframe(df, use_container_width=True)


# ============================================================
# TAB 3 — CUSTOMER LTV
# ============================================================
with tab3:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👥 Customer LTV Filters")

    all_states = sorted(ltv_df["state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect(
        "Customer State",
        options=all_states,
        default=all_states,
        key="ltv_state"
    )

    all_segments = sorted(ltv_df["ltv_segment"].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "LTV Segment",
        options=all_segments,
        default=all_segments,
        key="ltv_seg"
    )

    # apply filters
    df = ltv_df.copy()
    df = df[df["state"].isin(selected_states)]
    df = df[df["ltv_segment"].isin(selected_segments)]

    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{len(df):,.0f}")
    col2.metric("Total Revenue", f"R$ {df['total_spent'].sum():,.0f}")
    col3.metric("Avg Spend", f"R$ {df['total_spent'].mean():,.2f}")
    col4.metric("Avg Review Score", f"{df['avg_review_score'].mean():,.2f}")

    st.divider()

    st.subheader("LTV Segment Distribution")
    seg_df = df["ltv_segment"].value_counts().reset_index()
    seg_df.columns = ["segment", "count"]
    fig = px.pie(seg_df, names="segment", values="count",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Total Spend Distribution")
    fig2 = px.histogram(df, x="total_spent", nbins=80,
                        labels={"total_spent": "Total Spent (BRL)"},
                        color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Orders per Customer Distribution")
    fig3 = px.histogram(df, x="total_orders", nbins=20,
                        labels={"total_orders": "Number of Orders"},
                        color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Avg Spend by State")
    state_ltv = df.groupby("state").agg(
        avg_spent=("total_spent", "mean"),
        total_customers=("customer_id", "count")
    ).reset_index().sort_values("avg_spent", ascending=False)
    fig4 = px.bar(state_ltv, x="state", y="avg_spent",
                  color="avg_spent", color_continuous_scale="Blues",
                  labels={"state": "State", "avg_spent": "Avg Spend (BRL)"})
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Customer Count by State")
    fig5 = px.bar(state_ltv.sort_values("total_customers", ascending=False),
                  x="state", y="total_customers",
                  color_discrete_sequence=["#00CC96"],
                  labels={"state": "State", "total_customers": "Customers"})
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Spend vs Review Score")
    fig6 = px.scatter(df, x="total_spent", y="avg_review_score",
                      color="ltv_segment", opacity=0.5,
                      labels={"total_spent": "Total Spent (BRL)", "avg_review_score": "Avg Review Score"})
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Spend vs Total Orders")
    fig7 = px.scatter(df, x="total_orders", y="total_spent",
                      color="ltv_segment", opacity=0.5,
                      labels={"total_orders": "Total Orders", "total_spent": "Total Spent (BRL)"})
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Customer Lifespan Distribution (Days)")
    fig8 = px.histogram(df[df["customer_lifespan_days"] > 0], x="customer_lifespan_days", nbins=50,
                        labels={"customer_lifespan_days": "Lifespan (Days)"},
                        color_discrete_sequence=["#AB63FA"])
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Top 20 Customers by Spend")
    top_df = df.nlargest(20, "total_spent")[
        ["customer_unique_id", "state", "total_spent", "total_orders", "avg_review_score", "ltv_segment"]
    ]
    st.dataframe(top_df, use_container_width=True)


# ============================================================
# TAB 4 — SELLER PERFORMANCE
# ============================================================
with tab4:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏪 Seller Filters")

    all_seller_states_sp = sorted(seller_df["seller_state"].dropna().unique().tolist())
    selected_seller_states_sp = st.sidebar.multiselect(
        "Seller State",
        options=all_seller_states_sp,
        default=all_seller_states_sp,
        key="sp_state"
    )

    all_tiers = sorted(seller_df["seller_tier"].dropna().unique().tolist())
    selected_tiers = st.sidebar.multiselect(
        "Seller Tier",
        options=all_tiers,
        default=all_tiers,
        key="sp_tier"
    )

    # apply filters
    df = seller_df.copy()
    df = df[df["seller_state"].isin(selected_seller_states_sp)]
    df = df[df["seller_tier"].isin(selected_tiers)]

    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sellers", f"{len(df):,.0f}")
    col2.metric("Total Revenue", f"R$ {df['total_revenue'].sum():,.0f}")
    col3.metric("Avg Revenue per Seller", f"R$ {df['total_revenue'].mean():,.0f}")
    col4.metric("Avg Late Delivery Rate", f"{df['late_delivery_rate_pct'].mean():,.1f}%")

    st.divider()

    st.subheader("Seller Tier Distribution")
    tier_df = df["seller_tier"].value_counts().reset_index()
    tier_df.columns = ["tier", "count"]
    fig = px.pie(tier_df, names="tier", values="count",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Revenue Distribution Across Sellers")
    fig2 = px.histogram(df, x="total_revenue", nbins=60,
                        labels={"total_revenue": "Revenue (BRL)"},
                        color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Late Delivery Rate Distribution")
    fig3 = px.histogram(df, x="late_delivery_rate_pct", nbins=40,
                        labels={"late_delivery_rate_pct": "Late Rate (%)"},
                        color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Revenue vs Late Delivery Rate")
    fig4 = px.scatter(df, x="total_revenue", y="late_delivery_rate_pct",
                      color="seller_tier",
                      hover_data=["seller_id", "seller_state"],
                      opacity=0.6,
                      labels={"total_revenue": "Revenue (BRL)", "late_delivery_rate_pct": "Late Rate (%)"})
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Total Revenue by Seller State")
    state_seller = df.groupby("seller_state").agg(
        total_revenue=("total_revenue", "sum"),
        total_sellers=("seller_id", "count"),
        avg_late_rate=("late_delivery_rate_pct", "mean")
    ).reset_index().sort_values("total_revenue", ascending=False)
    fig5 = px.bar(state_seller, x="seller_state", y="total_revenue",
                  color="total_revenue", color_continuous_scale="Greens",
                  labels={"seller_state": "State", "total_revenue": "Revenue (BRL)"})
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Seller Count by State")
    fig6 = px.bar(state_seller.sort_values("total_sellers", ascending=False),
                  x="seller_state", y="total_sellers",
                  color_discrete_sequence=["#FFA15A"],
                  labels={"seller_state": "State", "total_sellers": "Sellers"})
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Avg Late Delivery Rate by Seller State")
    fig7 = px.bar(state_seller.sort_values("avg_late_rate", ascending=False),
                  x="seller_state", y="avg_late_rate",
                  color="avg_late_rate", color_continuous_scale="Oranges",
                  labels={"seller_state": "State", "avg_late_rate": "Avg Late Rate (%)"})
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Items Sold vs Revenue per Seller")
    fig8 = px.scatter(df, x="total_items_sold", y="total_revenue",
                      color="seller_tier",
                      hover_data=["seller_id", "seller_state"],
                      opacity=0.6,
                      labels={"total_items_sold": "Items Sold", "total_revenue": "Revenue (BRL)"})
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Avg Item Price vs Avg Freight Value")
    fig9 = px.scatter(df, x="avg_item_price", y="avg_freight_value",
                      color="seller_tier",
                      hover_data=["seller_id", "seller_state"],
                      opacity=0.6,
                      labels={"avg_item_price": "Avg Item Price (BRL)", "avg_freight_value": "Avg Freight (BRL)"})
    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Top 20 Sellers by Revenue")
    top_df = df.nlargest(20, "total_revenue")[
        ["seller_id", "seller_state", "total_revenue", "total_orders", "late_delivery_rate_pct", "seller_tier"]
    ]
    st.dataframe(top_df, use_container_width=True)