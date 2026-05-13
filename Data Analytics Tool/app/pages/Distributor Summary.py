import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(layout="wide")
st.markdown("## Distributor Summary")


page_col = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #EDEDED;
}

.stAppHeader {
    background-color: #00488e;
}

/* This targets the text and icons within the header */
.stAppHeader * {
    color: white !important;
}
</style>
"""
st.markdown(page_col, unsafe_allow_html=True)

from utils.data_utils import data_loading
df1, df2 = data_loading()

from utils.data_utils import add_columns
df2 = add_columns(df2)

# filter
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

filtered_year_df = df2[df2["Year"].isin(selected_years)] 

from utils.data_utils import get_custom_color_scale,get_styled_chart
custom_range, custom_domain = get_custom_color_scale()

st.markdown("""
<style>
    div[data-testid="stPills"] button[aria-checked="true"],
    div[data-testid="stPills"] button[aria-checked="true"] > div,
    div[data-testid="stPills"] button[aria-checked="true"] span {
        background-color: rgb(40, 167, 69) !important;
        color: white !important;
    }
    div[data-testid="stPills"] [display="inline-flex"] button[aria-checked="true"] {
        background-color: #28a745 !important;
    }
    div[data-testid="stPills"] button:focus {
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
        border-color: #28a745 !important;
    }
    div[data-testid="stPills"] button[aria-checked="true"] p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# CHARTS SECTION

cols = st.columns([3,1])

# 1. total sales across distributors 
with cols[0].container(border=True, height='stretch'):
    "##### Total Sales by Distributor"
    chart1 = (
        alt.Chart(filtered_year_df)
        .mark_bar(size=40)
        .encode(
            alt.X("Distributor Code:N", title="Distributors", sort="-y"),
            alt.Y("Revenue:Q", aggregate="sum", title="Total Sales"),
            alt.Color("Year:N", scale=alt.Scale(domain=custom_domain, range=custom_range)),
            tooltip=["Distributor Code", "Year", alt.Tooltip("sum(Revenue):Q", format=",.0f")]
        )
        .configure_legend(orient='bottom')
    )
    st.altair_chart(get_styled_chart(chart1, "Total Sales by Distributor"), use_container_width=True)
    
    #insight
    sorted_df = (
    filtered_year_df
    .groupby("Distributor Code", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
    )
    top_distributor = sorted_df.iloc[0]["Distributor Code"]
    top_revenue = sorted_df.iloc[0]["Revenue"]

    st.info(f"{top_distributor} is the primary contributor to overall sales with ₹{top_revenue:,.0f}.")


# 2. Each distributor’s contribution 
with cols[1].container(border=True, height='stretch'):
    "##### Contribution to Overall Sales"
    chart2 = (
        alt.Chart(filtered_year_df)
        .mark_arc(innerRadius=60)
        .encode(
            alt.Theta("Revenue:Q").aggregate("sum"),
            alt.Color("Distributor Code:N", title="Distributors"),
            tooltip=["Distributor Code", alt.Tooltip("Revenue:Q", aggregate="sum", title='Revenue', format=",.0f")]
        )
        .configure_legend(orient='bottom')
    )
    st.altair_chart(get_styled_chart(chart2, "Contribution to Overall Sales"), use_container_width=True)
    
    #insight
    contrib_df = filtered_year_df.groupby("Distributor Code", as_index=False)["Revenue"].sum()
    total_revenue = contrib_df["Revenue"].sum()
    contrib_df["Share"] = contrib_df["Revenue"] / total_revenue * 100
    top_dist = contrib_df.sort_values("Share", ascending=False).iloc[0]

    st.info(
        f"{top_dist['Distributor Code']} contributes {top_dist['Share']:.1f}% of total revenue, "
        "indicating potential dependency on this distributor."
    )

    #view = contrib_df.sort_values("Share", ascending=False)
    #st.write(view)

cols = st.columns(2)

# 3. monthly trends
with cols[0].container(border=True, height="stretch"):
    '##### Monthly Sales Trends'
    monthly_dist_data = filtered_year_df.groupby(
        ['Month', 'Distributor Code'], as_index=False)['Revenue'].sum()

    chart3 = (
        alt.Chart(monthly_dist_data)
        .mark_line(point=True, interpolate='monotone')
        .encode(
            alt.X("Month:O", title="Month"), 
            alt.Y("Revenue:Q", title="Revenue"),
            alt.Color("Distributor Code:N", title="Distributor"),
            tooltip=["Distributor Code", "Month", alt.Tooltip("Revenue:Q", format=",.0f")]
        )
        .configure_legend(orient='bottom')
    )    
    st.altair_chart(get_styled_chart(chart3, "Monthly Sales Trends"), use_container_width=True)
    
    
    #insights
    monthly_total = filtered_year_df.groupby("Month", as_index=False)["Revenue"].sum()

    month_labels = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    monthly_total['Month'] = monthly_total['Month'].map(month_labels)


    spike_month = monthly_total.loc[monthly_total["Revenue"].idxmax()]
    dip_month = monthly_total.loc[monthly_total["Revenue"].idxmin()]
    
    st.success(f"Sales spike during **{spike_month['Month']}**")
    st.error(f"Sales dip during **{dip_month['Month']}**")



# 4. growth by month
with cols[1].container(border=True): 
    st.markdown("##### Monthly Growth of distributors")
    # calc
    dist_growth = filtered_year_df.groupby(['Month', 'Distributor Code'])['Revenue'].sum().reset_index()
    dist_growth = dist_growth.sort_values(['Distributor Code', 'Month'])
    dist_growth['MoM Growth %'] = dist_growth.groupby(['Distributor Code'])['Revenue'].pct_change() * 100
    dist_growth['MoM Growth %'] = dist_growth['MoM Growth %'].fillna(0)

    chart4 = (
        alt.Chart(dist_growth)
        .mark_line(point=True)
        .encode(
            alt.X("Month:O", title="Month", axis=alt.Axis(labelAngle=0)), 
            alt.Y("MoM Growth %:Q", title="Growth Rate (%)"),
            alt.Color("Distributor Code:N", legend=alt.Legend(orient='bottom', title="Distributor Code")),
            tooltip=[
                "Distributor Code", 
                "Month", 
                alt.Tooltip("MoM Growth %:Q", format=".1f", title="Growth %")
            ]
        )
        .properties(height=350)
    )
    
    st.altair_chart(get_styled_chart(chart4, "Monthly Growth of Distributors"), use_container_width=True)
    

    #insights
    revenue_by_dist = (
    filtered_year_df
    .groupby("Distributor Code")["Revenue"]
    .sum()
    .reset_index()
    )

    growth_by_dist = (
    dist_growth
    .groupby("Distributor Code")["MoM Growth %"]
    .mean()
    .reset_index()
    )

    growth_by_dist["MoM Growth %"] = growth_by_dist["MoM Growth %"] * 100
    growth_analysis = revenue_by_dist.merge(growth_by_dist, on="Distributor Code")
    top_growth = growth_analysis.sort_values("MoM Growth %", ascending=False).iloc[0]

    st.info(
    f"{top_growth['Distributor Code']} has the highest monthly growth momentum "
    f"with an average MoM growth of {top_growth['MoM Growth %']:.1f}%."
    )
    growth_analysis = growth_analysis.sort_values("Revenue", ascending=False)
    emerging_candidates = growth_analysis.iloc[1:]
    emerging_dist = emerging_candidates.sort_values("MoM Growth %", ascending=False).iloc[0]

    st.success(
    f"{emerging_dist['Distributor Code']} shows strong growth momentum "
    f"({emerging_dist['MoM Growth %']:.1f}%) despite having lower total revenue."
    )


    #momentum_df = growth_analysis.sort_values("MoM Growth %", ascending=False)
    #st.dataframe(momentum_df[["Distributor Code","MoM Growth %"]], use_container_width=True)