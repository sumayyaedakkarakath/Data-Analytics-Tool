import pandas as pd
import streamlit as st
import altair as alt


st.set_page_config(layout="wide")
st.markdown("## Seller Summary")

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


# dist selector
dists = sorted(df2['Distributor Code'].unique().tolist())
selected_dists = st.pills("Select A distributor", dists, default=dists[0], key='dist_select')

if selected_dists is None:
    st.warning("Select a distributor")
    st.stop()

dist_filter = df2[df2["Distributor Code"]==selected_dists] 


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
    .stApp { 
        font-family: 'Inter', sans-serif; 
    }
    div[data-testid="stPills"] button[aria-checked="true"] {
        background-color: #28a745 !important;
        color: white !important;
    }
    div[data-testid="stPills"] button[aria-checked="true"]:hover {
        background-color: #218838 !important;
    }
    .metric-container { display: flex; flex-direction: column; padding: 5px 0; }
    .metric-label { font-size: 0.87rem !important; font-weight: 350 !important; white-space: normal; }
    .metric-value { font-size: 1.2rem !important; font-weight: 380 !important; color: #333 !important; }
    .delta-positive { color: #28a745 !important; font-size: 0.85rem; font-weight: 500; }
    .delta-negative { color: #dc3545 !important; font-size: 0.85rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


custcount = dist_filter['Customer Code'].nunique()
teamcount = dist_filter['Seller Code'].nunique()
total_rev = dist_filter['Revenue'].sum()

st.markdown("""
<style>
/* Metric Layout Classes */
    .metric-container { display: flex; flex-direction: column; padding: 5px 0; }
    .metric-label { font-size: 0.87rem !important; font-weight: 350 !important; white-space: normal; }
    .metric-value { font-size: 1.5rem !important; font-weight: 380 !important; color: #333 !important; }
    .delta-positive { color: #28a745 !important; font-size: 0.85rem; font-weight: 500; }
    .delta-negative { color: #dc3545 !important; font-size: 0.85rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# top row
from utils.calc import kpis, format_value
kpi_data = kpis(dist_filter)

if kpi_data:
    # add extra metrics
    kpi_data["Sellers"] = teamcount
    kpi_data["Customers"] = custcount


def render_kpi(col, item):
    name, value = item
    with col:
        st.markdown(f'<div class="metric-container"><div class="metric-label">{name}</div><div class="metric-value">{format_value(name, value)}</div></div>', unsafe_allow_html=True)

if kpi_data:
    kpi_items = list(kpi_data.items())

c1, c2, c3, c4 = st.columns(4)

render_kpi(c1, kpi_items[0])
render_kpi(c2, kpi_items[1])
render_kpi(c3, kpi_items[2])
render_kpi(c4, kpi_items[3])

c5, c6, c7, c8 = st.columns(4)
render_kpi(c5, kpi_items[4])
render_kpi(c6, kpi_items[5])
render_kpi(c7, kpi_items[6])


# year filter
YEARS = sorted(df2["Year"].unique().tolist())
selected_years = st.pills("Select years to compare", YEARS, default=YEARS, selection_mode="multi")

if not selected_years:
    st.warning("Please select at least one year")
    st.stop()

# filters combined
df = df2[
    (df2["Distributor Code"]==selected_dists) & 
    ((df2["Year"].isin(selected_years)))
]
if df.empty:
    st.info("No data found for the selected combination.")
    st.stop()


from utils.data_utils import get_styled_chart, get_custom_color_scale
custom_range, custom_domain = get_custom_color_scale()



# calculations for insights

#1.highest seller
df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
chart_data = df.groupby(
        ['Seller Name', 'Year', 'Distributor Code', 'Seller Code']
    )['Revenue'].sum().reset_index()
seller_rev = (
    chart_data
    .groupby(['Distributor Code','Seller Name'])['Revenue']
    .sum()
    .reset_index()
)
top_seller_detail = (
    seller_rev
    .sort_values(['Distributor Code','Revenue'], ascending=[True,False])
    .groupby('Distributor Code')
    .first()
    .reset_index()
)
top_seller = top_seller_detail.iloc[0]['Seller Name']

#2.largest contributor
dist_total = (
    seller_rev
    .groupby("Distributor Code")["Revenue"]
    .sum()
    .reset_index(name="Distributor Revenue")
)
seller_share = seller_rev.merge(dist_total, on="Distributor Code")
seller_share["Contribution %"] = (
    seller_share["Revenue"] / seller_share["Distributor Revenue"] * 100
)
top_contributor = (
    seller_share
    .sort_values("Contribution %", ascending=False)
    .iloc[0]
)
#st.write(seller_share)

#finding seller who have strong monthly growth
seller_monthly = (
    df.groupby(['Seller Name', 'Month'])['Revenue']
    .sum()
    .reset_index()
)
seller_monthly = seller_monthly.sort_values(['Seller Name', 'Month'])
seller_monthly['MoM Growth %'] = (
    seller_monthly.groupby('Seller Name')['Revenue']
    .pct_change() * 100
)

seller_monthly['MoM Growth %'] = seller_monthly['MoM Growth %'].fillna(0)


#3.sellers who consistently generate lower revenue
seller_avg_rev = (
    seller_monthly
    .groupby('Seller Name')['Revenue']
    .mean()
    .reset_index(name='Avg Monthly Revenue')
)
threshold = seller_avg_rev['Avg Monthly Revenue'].quantile(0.25)

underperforming = seller_avg_rev[
    seller_avg_rev['Avg Monthly Revenue'] <= threshold
]
names = ", ".join(underperforming["Seller Name"])
revenues = ", ".join([f"₹{rev:,.0f}" for rev in underperforming["Avg Monthly Revenue"]])
#to show
#st.dataframe(underperforming, use_container_width=True)



# CHARTS
with st.container():
    left, middle, right = st.columns([2,1,1], gap='small')

    # 1. Revenue by sellers
    with left.container(border=True):
        
        chart1 = (
            alt.Chart(chart_data)
            .mark_bar(stroke="white", strokeWidth=0.5)
            .encode(
                x=alt.X("Seller Name:N", title="Sellers", sort="-y"),
                y=alt.Y("Revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
                color=alt.Color(
                    "Year:N",
                    title="Year",
                    scale=alt.Scale(domain=custom_domain, range=custom_range)
                ),
                tooltip=[
                    "Year",
                    alt.Tooltip("Revenue:Q", title="Revenue", format=",.0f")
                ]
            )
            .properties(height=400, title="Revenue by Sellers")
        )

        if not chart_data.empty:
            st.altair_chart(get_styled_chart(chart1), use_container_width=True)
        else:
            st.warning("No data found for this selection.")

    # 2. Customers per Sellers
    with middle.container(border=True):

        seller_customer_count = (
            df.groupby(['Distributor Code', 'Seller Name'])['Customer Code']
            .nunique()
            .reset_index()
            .rename(columns={'Customer Code': 'Total Customers'})
        )

        seller_chart_df = seller_customer_count.sort_values(
            "Total Customers", ascending=False
        )

        
        chart2 = (
            alt.Chart(seller_chart_df)
            .mark_arc(innerRadius=80)
            .encode(
                theta=alt.Theta('Total Customers:Q'),
                color=alt.Color('Seller Name:N', scale=alt.Scale(scheme='blues') ),
                tooltip=['Distributor Code', 'Seller Name', 'Total Customers']
            )
            .properties(
                height=400,
                title='Customers per Seller Team',
                background="transparent"
            )
        )

        st.altair_chart(get_styled_chart(chart2), use_container_width=True)

    # 3. Insights display
    with right.container(border=True):
        st.info(f"{top_seller} is the Top performing seller")
        st.info(f"{top_contributor['Seller Name']} is the major seller contributor with {top_contributor['Contribution %']:.1f}% contribution")
        st.error(
        f"{names} consistently generate lower revenue with respective "
        f"average monthly revenue of {revenues}."
        )
        
# 3. Top and low performing sellers per year
with st.container(border=True):
    extremes_list = []
    available_years = sorted(df['Year'].unique())
    
    for year in available_years:
        year_data = df[df['Year'] == year]
        team_totals = year_data.groupby(['Seller Code'])['Revenue'].sum().reset_index()
        
        if not team_totals.empty:
            hi_idx = team_totals['Revenue'].idxmax()
            lo_idx = team_totals['Revenue'].idxmin()
            high = team_totals.loc[hi_idx].copy()
            low = team_totals.loc[lo_idx].copy()
            high['Seller Name'] = str(high['Seller Code']).split('-')[-1]
            low['Seller Name'] = str(low['Seller Code']).split('-')[-1]
            
            high['Ranking'], low['Ranking'] = 'high', 'low' 
            high['Year'], low['Year'] = year, year
            extremes_list.extend([high, low])

    if extremes_list:
        df_plot_year = pd.DataFrame(extremes_list)
        
        base = alt.Chart(df_plot_year).encode(
            x=alt.X("Year:N", title="Year", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
            color=alt.Color("Ranking:N", 
                            scale=alt.Scale(domain=['high','low'], range=["#0055A4", "#72CFF4",])),
            xOffset=alt.XOffset("Ranking:N"),
             tooltip=[
        alt.Tooltip("Year:N", title="Year"),
        alt.Tooltip("Seller Name:N", title="Seller"),
        alt.Tooltip("Revenue:Q", title="Revenue", format=",.0f")
    ] 
        )
        
        bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        text = base.mark_text(
            align='center', 
            baseline='bottom', 
            dy=-5, 
            fontSize=10,
            fontWeight='bold'
        ).encode(text='Seller Name:N')
        
        chart2 = (bars + text).properties(height=400, title="Top and low performing sellers per year")
        st.altair_chart(get_styled_chart(chart2), use_container_width=True)

st.divider()


# seller level

sellers = sorted(df["Seller Name"].unique().tolist())

selected_seller = st.pills(
    "Select A Seller",
    sorted(sellers),
    default=sellers[0],
    key="seller_select"
)

if selected_seller is None:
    st.warning("Select a Seller")
    st.stop()

sell_filter = df[df["Seller Name"] == selected_seller]

#insights calculation
product_rev = (
    sell_filter
    .groupby("Product Name")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Revenue", ascending=False)
)
top_products = product_rev.head(3)
product_names = ", ".join(top_products["Product Name"])

#customer contribution
sell_filter['Customers'] = sell_filter['Customer Code'].str.split('-').str[-1]
customer_rev = (
    sell_filter
    .groupby("Customers")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Revenue", ascending=False)
)
top_customers = customer_rev.head(3)
top_names = ", ".join(top_customers["Customers"])
top_share = (top_customers["Revenue"].sum() / customer_rev["Revenue"].sum()) * 100
#contributors table
#st.dataframe(customer_rev, use_container_width=True)


#underperforming customers
underperforming_customers = customer_rev.tail(3)
under_names = ", ".join(underperforming_customers["Customers"])



#kpis
custcount2 = sell_filter["Customer Code"].nunique()

kpi_data2 = kpis(sell_filter)
if kpi_data2:
    kpi_data2["Customers"] = custcount2

if kpi_data2:
    kpi_items2 = list(kpi_data2.items())



with st.container():
    left, right = st.columns([2,1], gap='small')

    with left:
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)

            render_kpi(c1, kpi_items2[0])
            render_kpi(c2, kpi_items2[1])
            render_kpi(c3, kpi_items2[2])


            c5, c6, c7 = st.columns(3)
            render_kpi(c5, kpi_items2[3])
            render_kpi(c6, kpi_items2[4])
            render_kpi(c7, kpi_items2[5])

    with right:
        with st.container(border=True):
            st.success(
                f"{product_names} are the products contributing the highest revenue to this seller."
            )
            st.info(
                f"{top_names} are the top customers contributing the highest revenue")
            st.error(
                f"{under_names} are the underperforming customers generating relatively lower revenue."
            )



# metrics Section
st.markdown("""
<style>
    .metric-card {
        background-color: white; 
        border: 1px solid #e6e9ef; 
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-label { color: #333; font-size: 0.9rem; font-weight: bold; }
    .metric-value { font-size: 1.2rem; margin-bottom: 10px; }
    .stats-text { font-size: 0.85rem; color: #333; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)


#function to get top by group in both sections
def get_top_by_group(df, group_cols, value_col, top_n=5):
    summary = (
        df.groupby(group_cols, as_index=False)[value_col]
        .sum()
    )
    
    return (
        summary
        .sort_values(value_col, ascending=False)
        .head(top_n)
    )


# 1: Top 5 products by rev
st.markdown("##### Top 5 products of sellers by revenue")

top_products_rev = get_top_by_group(
    sell_filter,
    group_cols=['Seller Name', 'Product Code'],
    value_col='Revenue',
).rename(columns={'Revenue': 'Total Revenue'})

cols = st.columns(5)

for i, (_, row) in enumerate(top_products_rev.head(5).iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Product</div>
            <div class="metric-value">{row['Product Code']}</div>
            <hr>
            <div class="stats-text">
                <strong>Revenue:</strong> ₹{row['Total Revenue']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)



# 2: Top 5 products by qty
st.markdown("##### Top 5 products of sellers by quantity")

top_products_q = get_top_by_group(
    sell_filter,
    group_cols=['Seller Name', 'Product Code'],
    value_col='Sale Quantity',
).rename(columns={'Sale Quantity': 'Total Quantity'})

cols = st.columns(5)

for i, (_, row) in enumerate(top_products_q.head(5).iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Product</div>
            <div class="metric-value">{row['Product Code']}</div>
            <hr>
            <div class="stats-text">
                <strong>Quantity:</strong> {row['Total Quantity']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)



# 3: Top 5 customers
st.markdown("##### Top 5 customers of sellers")

df['Customers'] = df['Customer Code'].str.split('-').str[-1]

top_custs = get_top_by_group(
    sell_filter,
    group_cols=['Seller Name', 'Customers'],
    value_col='Revenue',
).rename(columns={'Revenue': 'Total Revenue'})

cols = st.columns(5)

for i, (_, row) in enumerate(top_custs.head(5).iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{row['Seller Name']}</div>
            <div class="metric-value">{row['Customers']}</div>
            <hr style="border: 0.5px solid #eee; margin: 10px 0;">
            <div class="stats-text">
                <strong>Revenue:</strong> ₹{row['Total Revenue']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)