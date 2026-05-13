import streamlit as st
import pandas as pd
import altair as alt

    
st.set_page_config(layout="wide")

page_col = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #EDEDED;
}
.stAppHeader {
    background-color: #00488e;
}
.stAppHeader * {
    color: white !important;
}
</style>
"""

st.markdown(page_col, unsafe_allow_html=True)

if (
    st.session_state.get("dataset_1") is None
    and st.session_state.get("dataset_2") is None
):
    st.warning("Upload datasets")
    st.stop()

from utils.data_utils import data_loading
df1, df2 = data_loading()

from utils.data_utils import add_columns
df2 = add_columns(df2)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
    .stApp { 
        font-family: 'Inter', sans-serif; 
    }
    [data-testid="stMetric"], 
    .element-container:has(iframe) {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stMetricLabel"] {
        color: #31333F !important; /* Dark grey for readability */
    }

    /* Green 'Pills' (Selection buttons) */
    div[data-testid="stPills"] button[aria-checked="true"] {
        background-color: #28a745 !important;
        color: white !important;
    }
    div[data-testid="stPills"] button[aria-checked="true"]:hover,
    div[data-testid="stPills"] button[aria-checked="true"]:focus {
        background-color: #218838 !important;
        color: white !important;
    }
    /* Metric Layout Classes */
    .metric-container { display: flex; flex-direction: column; padding: 5px 0; }
    .metric-label { font-size: 0.87rem !important; font-weight: 350 !important; white-space: normal; }
    .metric-value { font-size: 1.5rem !important; font-weight: 380 !important; color: #333 !important; }
    .delta-positive { color: #28a745 !important; font-size: 0.85rem; font-weight: 500; }
    .delta-negative { color: #dc3545 !important; font-size: 0.85rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


def get_delta_html(value):
    """Formats percentage growth for display."""
    if value > 0:
        return f'<span class="delta-positive">↑ {value:.1f}%</span>'
    elif value < 0:
        return f'<span class="delta-negative">↓ {abs(value):.1f}%</span>'
    return f'<span style="color:gray; font-size:0.85rem;">0.0%</span>'


curr_days = curr_rev = curr_units = curr_rev_per_cust = 0
curr_dist = curr_sellers = curr_cust = cust_cat_count = 0
rev_growth = unit_growth = rev_per_cust_growth = dist_growth = seller_growth = cust_growth = 0
delta_days = 0

years = sorted(df2['Year'].unique())

if len(years) >= 1:
    curr_yr = years[-1]
    df_curr = df2[df2['Year'] == curr_yr]
    
    # Current Year 
    curr_days = df_curr['Date'].nunique()
    curr_rev = df_curr['Revenue'].sum()
    curr_units = df_curr['Sale Quantity'].sum()
    curr_cust = df_curr['Customer Code'].nunique()
    curr_dist = df_curr['Distributor Code'].nunique()
    curr_sellers = df_curr['Seller Code'].nunique()
    cust_cat_count = df_curr['Customer Category'].nunique()
    curr_rev_per_cust = curr_rev / curr_cust if curr_cust > 0 else 0

    if len(years) >= 2:
        prev_yr = years[-2]
        df_prev = df2[df2['Year'] == prev_yr]
        
        # Previous Year 
        prev_days = df_prev['Date'].nunique()
        prev_rev = df_prev['Revenue'].sum()
        prev_units = df_prev['Sale Quantity'].sum()
        prev_cust = df_prev['Customer Code'].nunique()
        prev_dist = df_prev['Distributor Code'].nunique()
        prev_sellers = df_prev['Seller Code'].nunique()
        prev_rev_per_cust = prev_rev / prev_cust if prev_cust > 0 else 0
        

        delta_days = curr_days - prev_days
        rev_growth = ((curr_rev - prev_rev) / prev_rev) * 100 if prev_rev > 0 else 0
        unit_growth = ((curr_units - prev_units) / prev_units) * 100 if prev_units > 0 else 0
        rev_per_cust_growth = ((curr_rev_per_cust - prev_rev_per_cust) / prev_rev_per_cust) * 100 if prev_rev_per_cust > 0 else 0
        dist_growth = ((curr_dist - prev_dist) / prev_dist) * 100 if prev_dist > 0 else 0
        seller_growth = ((curr_sellers - prev_sellers) / prev_sellers) * 100 if prev_sellers > 0 else 0
        cust_growth = ((curr_cust - prev_cust) / prev_cust) * 100 if prev_cust > 0 else 0


display_year = years[-1] if years else "NA"
f"""
## {display_year} Summary
"""

# Row 1
c1, c2, c3, c4 = st.columns(4)
with c1:
    day_color = "delta-positive" if delta_days >= 0 else "delta-negative"
    st.markdown(f'<div class="metric-container"><div class="metric-label">Sales Days</div><div class="metric-value">{curr_days}</div><div class="{day_color}">{"↑" if delta_days>=0 else "↓"} {abs(delta_days)} days</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Revenue</div><div class="metric-value">₹{curr_rev:,.0f}</div>{get_delta_html(rev_growth)}</div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Units</div><div class="metric-value">{curr_units:,.0f}</div>{get_delta_html(unit_growth)}</div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Revenue / Customer</div><div class="metric-value">₹{curr_rev_per_cust:,.0f}</div>{get_delta_html(rev_per_cust_growth)}</div>', unsafe_allow_html=True)


# Row 2
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Distributors</div><div class="metric-value">{curr_dist}</div>{get_delta_html(dist_growth)}</div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Sellers</div><div class="metric-value">{curr_sellers}</div>{get_delta_html(seller_growth)}</div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Customers</div><div class="metric-value">{curr_cust}</div>{get_delta_html(cust_growth)}</div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="metric-container"><div class="metric-label">Categories</div><div class="metric-value">{cust_cat_count}</div></div>', unsafe_allow_html=True)


f"""
####  Compare sales over different years
"""

# Year selector 
YEARS = sorted(df2["Year"].unique())

selected_years = st.pills(
    "Select years to compare",
    YEARS,
    default=YEARS,
    selection_mode="multi"
)

if not selected_years:
    st.warning("Please select at least one year to view the trend.")
    st.stop()


# Filter by selected years 
filtered_year_df = df2[df2["Year"].isin(selected_years)]


from utils.data_utils import get_custom_color_scale,get_styled_chart
custom_range, custom_domain = get_custom_color_scale()



# CHARTS SECTION

# top row
# 1. REVENUE BY MONTH 
daily_sales = (
    filtered_year_df
    .groupby("Date", as_index=False)
    .agg(daily_revenue=("Revenue", "sum"))
)
with st.container(border=True):
    chart = (
        alt.Chart(daily_sales)
        .mark_line(strokeWidth=1.5, interpolate='monotone')
        .encode(
            alt.X("Date:T", 
                timeUnit="monthdate", 
                title="Month",
                axis=alt.Axis(
                    format="%b %d",       
                    tickCount="month",    
                    labelFlush=False,     
                    grid=True
                )
            ),
            alt.Y("daily_revenue:Q", 
                  aggregate="sum", 
                  title="Revenue", 
                  scale=alt.Scale(zero=True)),
            alt.Color("year(Date):N", 
                title="year",
                scale=alt.Scale(domain=custom_domain, range=custom_range)
            ),
            tooltip=[
                alt.Tooltip("monthdate(Date):T", title="Date"), 
                alt.Tooltip("sum(daily_revenue):Q", title="Revenue", format=",.0f")
            ]
        )
        .properties(
            title=alt.TitleParams(
                text="Revenue per Month",
                anchor="start",
                fontSize=19  
            ),
            height=350,
            background="transparent"
        )
        .configure_axis(
            gridColor="#ccd0d7", 
            titleColor="#333333",
            labelFontSize=11
        )
    )

    st.altair_chart(chart, use_container_width=True)


# bottom row
cols = st.columns([2, 2])

# 2.Revenue/dist or Revenue/seller
distributor_count = filtered_year_df['Distributor Code'].nunique()
with cols[0].container(border=True):

    is_distributor = distributor_count > 1
    if is_distributor: 
        chart = (
            alt.Chart(filtered_year_df)
            .mark_bar()
            .encode(
                alt.X("Year:N", title="Year"),
                alt.Y("Revenue:Q", aggregate="sum", title="Revenue"),
                alt.Color("Distributor Code:N", title="Distributor"),
                tooltip=["Year", "Distributor Code", alt.Tooltip("Revenue:Q", aggregate="sum", title='Revenue', format=",.2f")]
            )
            .properties(width='container', height=400, title="Revenue by Distributor")
        )
        st.altair_chart(get_styled_chart(chart, "Revenue per distributor"), use_container_width=True)
    else:
        chart = (
            alt.Chart(filtered_year_df)
            .mark_bar()
            .encode(
                alt.X("Year:N", title="Year"),
                alt.Y("Revenue:Q", aggregate="sum", title="Revenue"),
                alt.Color("Seller Code:N", title="Sellers"),
                tooltip=["Year", "Seller Code", alt.Tooltip("Revenue:Q", aggregate="sum", format=",.2f")]
            )
            .properties(width='container', height=400, title="Revenue per Seller teams")
        )
        st.altair_chart(get_styled_chart(chart, "Revenue per Seller teams"), use_container_width=True)

# 3. customer category chart
with cols[1].container(border=True):
    chart_cat = (
        alt.Chart(filtered_year_df)
        .mark_bar()
        .encode(
            alt.X("Customer Category:N", title="Customer Category"),
            alt.Y("Revenue:Q", aggregate="sum", title="Revenue"),
            alt.XOffset("Year:N"), 
            alt.Color("Year:N", scale=alt.Scale(domain=custom_domain, range=custom_range))
        )
        .properties(height=350, title="Revenue per customer category")
    )
    st.altair_chart(get_styled_chart(chart_cat, "Revenue per customer category"), use_container_width=True)
    