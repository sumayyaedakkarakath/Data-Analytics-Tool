import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.markdown("## Seasonality")

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

from utils.data_utils import get_custom_color_scale,get_styled_chart
custom_range, custom_domain = get_custom_color_scale()


month_labels = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}



# SECTION 1
#  DISTRIBUTOR LEVEL
st.markdown("### Distributor level")


# distributor filter
dists = sorted(df2['Distributor Code'].unique().tolist())
selected_dists = st.pills(
    "Select A distributor",
    dists,
    default=[dists[0]],
    key='distselect'
)

if len(selected_dists) == 0:
    st.warning("Select a distributor")
    st.stop()


df_dist = df2[df2["Distributor Code"] == selected_dists]


monthly_dist_data = (
    df_dist
    .groupby(['Year', 'Month'], as_index=False)['Revenue']
    .sum()
)

monthly_dist_data['Month Name'] = monthly_dist_data['Month'].map(month_labels)


# CHART 1
with st.container(border=True):
    st.markdown("##### Monthly Trends")
    
    chart = (
        alt.Chart(monthly_dist_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Month Name:N", 
                sort=alt.SortField(field="Month", order='ascending'), 
                title="Month", 
                axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y(
                "Revenue:Q",
                title="Revenue",
                scale=alt.Scale(domain=[monthly_dist_data['Revenue'].min() * 0.9, monthly_dist_data['Revenue'].max() * 1.1])
            ),
            color=alt.Color("Year:N", title="Year"),
            tooltip=["Year", "Month Name", "Revenue" ]
        )
    )
    
    st.altair_chart(get_styled_chart(chart), use_container_width=True)

# Daily Trends: drill down
st.markdown("#### Daily Trends")

years = sorted(df2['Year'].unique().tolist())
select_years = st.pills("Select a year to compare", years, default=[years[0]], key='dist_year')

if not select_years:
    st.warning('Select a year')
    st.stop()

months = sorted(df2['Month'].unique().tolist())
select_months = st.pills("Select a month to compare", months, default=[months[0]],  key='dist_mon')

if not select_months:
    st.warning('Select a month')
    st.stop()


dist_comb_df = df_dist[
    (df_dist['Year'].isin([select_years])&
     df_dist['Month'].isin([select_months]))
]

daily_rev = (
    dist_comb_df.groupby('Date')['Revenue']
    .sum()
    .reset_index()
    .sort_values('Date')
)


# CHART 2 
with st.container(border=True):
    chart = (
        alt.Chart(daily_rev)
        .mark_line(point=True)
        .encode(
        x=alt.X('Date:T', title='Day of Month', axis=alt.Axis(format='%d')), 
        y=alt.Y('Revenue:Q', title='Daily Revenue', scale=alt.Scale(zero=False)),
        tooltip=['Date:T', 'Revenue:Q']
        )
        .properties(
        height=400
        )
    )
    st.altair_chart(get_styled_chart(chart), use_container_width=True)

st.divider()




# SECTION 2  - SELLER LEVEL
st.markdown("### Seller level")
sellers = sorted(df_dist["Seller Name"].unique().tolist())

selected_sellers = st.pills(
    "Select a Seller",
    sellers,
    default=[sellers[0]],
    key='sellselect'
)

if not selected_sellers:
    st.warning("Select a Seller")
    st.stop()

df_s = df_dist[df_dist["Seller Name"].isin([selected_sellers])] # from df_dist

monthly_sell_data = (
    df_s
    .groupby(['Year', 'Month'], as_index=False)['Revenue']
    .sum()
)

monthly_sell_data['Month Name'] = monthly_sell_data['Month'].map(month_labels)


# CHART 1 
with st.container(border=True):
    st.markdown("##### Monthly Trends")
    
    chart = (
        alt.Chart(monthly_sell_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Month Name:N", 
                sort=alt.SortField(field="Month", order='ascending'), 
                title="Month", 
                axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y(
                "Revenue:Q",
                title="Revenue",
                scale=alt.Scale(domain=[monthly_sell_data['Revenue'].min() * 0.9, monthly_sell_data['Revenue'].max() * 1.1])
            ),
            color=alt.Color("Year:N", title="Year"),
            tooltip=["Year", "Month Name", "Revenue" ]
        )
    )
    
    st.altair_chart(get_styled_chart(chart), use_container_width=True)


# Daily Trends: drill down
st.markdown("#### Daily Trends")

years_s = sorted(df2['Year'].unique().tolist())
select_years_s = st.pills("Select a year to compare", years_s, default=[years_s[0]], key='sell_year')

if not select_years_s:
    st.warning('Select a year')
    st.stop()

months_s = sorted(df2['Month'].unique().tolist())
select_months_s = st.pills("Select a month to compare", months_s, default=[months_s[0]], key='sell_mon')

if not select_months_s:
    st.warning('Select a month')
    st.stop()


sell_comb_df = df_s[
    (df_s['Year'].isin([select_years_s])&
     df_s['Month'].isin([select_months_s]))
]

daily_revs = (
    sell_comb_df.groupby('Date')['Revenue']
    .sum()
    .reset_index()
    .sort_values('Date')
)

# CHART 2 
with st.container(border=True):

    chart = (
        alt.Chart(daily_revs)
        .mark_line(point=True)
        .encode(
            x=alt.X('Date:T', title='Day of Month', axis=alt.Axis(format='%d')), 
            y=alt.Y('Revenue:Q', title='Daily Revenue', scale=alt.Scale(zero=False)),
            tooltip=['Date:T', 'Revenue:Q']
        )
        .properties(
            height=400
        )
    )
    st.altair_chart(get_styled_chart(chart), use_container_width=True)