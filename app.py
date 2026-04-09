import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(layout="wide")

# ----------------------------
# COMPACT UI + KPI STYLE
# ----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0rem;
}

h1 {
    margin-bottom: 0.3rem;
}

.element-container {
    margin-bottom: 0.4rem !important;
}

/* KPI CARD */
[data-testid="stMetric"] {
    background: #1F2937;
    border-radius: 10px;
    padding: 10px;
    border-left: 5px solid #3B82F6;
}

/* KPI TEXT */
[data-testid="stMetric"] label {
    color: #9CA3AF !important;
}

[data-testid="stMetric"] div {
    color: #F9FAFB !important;
    font-weight: 600;
}

/* KPI COLORS */
div[data-testid="stMetric"]:nth-child(1) {border-left: 5px solid #3B82F6;}
div[data-testid="stMetric"]:nth-child(2) {border-left: 5px solid #6366F1;}
div[data-testid="stMetric"]:nth-child(3) {border-left: 5px solid #F59E0B;}
div[data-testid="stMetric"]:nth-child(4) {border-left: 5px solid #10B981;}
div[data-testid="stMetric"]:nth-child(5) {border-left: 5px solid #8B5CF6;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Funnel Analytics Dashboard")

# ----------------------------
# LOAD DATA (FINAL FIX)
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("sample_data.csv")

df = load_data()

# ----------------------------
# CLEANING
# ----------------------------
df.columns = df.columns.str.lower()
df['event_time'] = pd.to_datetime(df['event_time'])
df['date'] = df['event_time'].dt.date
df['hour'] = df['event_time'].dt.hour

# ----------------------------
# METRICS
# ----------------------------
users = df['user_id'].nunique()
views = len(df[df.event_type == 'view'])
cart = len(df[df.event_type == 'cart'])
purchase = len(df[df.event_type == 'purchase'])

conversion = purchase / users if users else 0
cart_rate = cart / views if views else 0
purchase_rate = purchase / cart if cart else 0

revenue = df[df.event_type == 'purchase']['price'].sum()

# ----------------------------
# KPI ROW
# ----------------------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Users", f"{users:,}")
c2.metric("Views", f"{views:,}")
c3.metric("Cart Rate", f"{cart_rate:.2%}")
c4.metric("Purchase Rate", f"{purchase_rate:.2%}")
c5.metric("Revenue", f"${revenue:,.0f}")

# ----------------------------
# ROW 1
# ----------------------------
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    funnel_df = pd.DataFrame({
        "stage": ["Users", "Views", "Cart", "Purchase"],
        "count": [users, views, cart, purchase]
    })
    st.plotly_chart(
        px.funnel(funnel_df, x="count", y="stage",
                  height=220, template="plotly_dark"),
        use_container_width=True
    )

with r1c2:
    conv_df = pd.DataFrame({
        "stage": ["View → Cart", "Cart → Purchase"],
        "rate": [cart_rate, purchase_rate]
    })
    st.plotly_chart(
        px.bar(conv_df, x="stage", y="rate",
               height=220, template="plotly_dark"),
        use_container_width=True
    )

with r1c3:
    revenue_df = df[df.event_type == 'purchase'] \
        .groupby('date')['price'].sum().reset_index()
    st.plotly_chart(
        px.line(revenue_df, x="date", y="price",
                height=220, template="plotly_dark"),
        use_container_width=True
    )

# ----------------------------
# ROW 2
# ----------------------------
r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    hourly = df.groupby('hour')['user_id'].count().reset_index()
    st.plotly_chart(
        px.line(hourly, x="hour", y="user_id",
                height=220, template="plotly_dark"),
        use_container_width=True
    )

with r2c2:
    cat = df.groupby(['category_code', 'event_type']).size().unstack(fill_value=0)
    if 'purchase' in cat and 'view' in cat:
        cat['conversion'] = cat['purchase'] / cat['view']
        cat = cat.sort_values("conversion", ascending=False).head(5)
        st.plotly_chart(
            px.bar(cat, x='conversion', y=cat.index,
                   orientation='h',
                   height=220, template="plotly_dark"),
            use_container_width=True
        )

with r2c3:
    st.plotly_chart(
        px.histogram(df, x="price",
                     height=220, template="plotly_dark"),
        use_container_width=True
    )

# ----------------------------
# INSIGHTS
# ----------------------------
st.markdown(
    f"**Insights:** Overall Conversion = {conversion:.2%} | "
    f"High drop-off before purchase | Revenue = ${revenue:,.0f}"
)