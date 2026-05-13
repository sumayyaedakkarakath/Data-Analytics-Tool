import streamlit as st
import pandas as pd


def data_loading():
    if "dataset_1" not in st.session_state or "dataset_2" not in st.session_state:
        st.warning("Please upload data to proceed.")
        st.stop()  

    df1 = pd.DataFrame(st.session_state["dataset_1"])
    df2 = pd.DataFrame(st.session_state["dataset_2"])

    return df1, df2



FORMAT = "%d-%m-%Y"
def add_columns(df, date_col="Date"):
    df = df.copy()  

    df[date_col] = pd.to_datetime(
        df[date_col],
        format=FORMAT,
        errors="coerce"
    )
    df = df.dropna(subset=[date_col])
    df["Year"] = df[date_col].dt.year
    df["Month"] = df[date_col].dt.month
    df["Day"] = df[date_col].dt.day 
    if "Seller Code" in df.columns:
        df["Seller Name"] = df["Seller Code"].astype(str).str.split("-").str[-1]

    if "Sale Amount" in df.columns:
        df = df.rename(columns={"Sale Amount": "Revenue"})
    return df




def get_custom_color_scale():
    custom_range = ["#0055A4", "#72CFF4", "#FF3131"]
    custom_domain = [2023, 2024, 2025]
    return custom_range, custom_domain

def get_styled_chart(chart, title=None):
    return (
        chart
        .configure(background="transparent")   
        .configure_view(fill="transparent", strokeWidth=0)
        .configure_axis(
            gridColor="#ccd0d7", 
            domain=False,
            ticks=False,
            labelColor="#999999",
            titleColor="#333333",
            labelFontSize=11
        )
        .configure_title(
            anchor="start",
            fontSize=18,
            fontWeight=400,
            font="Inter, sans-serif",
            color="#333333"
        )
        .configure_legend(
            orient="bottom",
            labelColor="#999999",
            titleColor="#999999",
            symbolSize=100,
            columnPadding=20
        )
    )