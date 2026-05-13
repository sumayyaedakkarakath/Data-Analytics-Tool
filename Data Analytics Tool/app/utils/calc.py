import streamlit as st
import pandas as pd
import numpy as np


df = st.session_state["dataset_2"].copy()

def kpis(df):
    if df is None or df.empty:
        return None

    totrev = df["Revenue"].sum()
    totqty = df["Sale Quantity"].sum()
    custcount = df["Customer Code"].nunique()
    rpc = totrev / custcount if custcount else 0

    df = df.copy()
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby("YearMonth")
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Sale Quantity", "sum"),
        )
        .reset_index()
    )

    monthly["Date"] = pd.to_datetime(monthly["YearMonth"])
    monthly = monthly.sort_values("Date")
    monthly["YoY"] = monthly["Revenue"].pct_change(12)
    monthly["MoM"] = monthly["Revenue"].pct_change(1)

    yoy_growth = monthly["YoY"].iloc[-1] * 100 if len(monthly) > 12 else 0
    mom_growth = monthly["MoM"].iloc[-1] * 100 if len(monthly) > 1 else 0

    return {
        "Total Revenue": totrev,
        "Total Quantity": totqty,
        "Revenue per Customer": rpc,
        "YoY Growth %": yoy_growth,
        "MoM Growth %": mom_growth,
    }

def format_value(name, value):
    if "Growth" in name:
        return f"{value:.2f}%"
    if name in ["Sellers", "Customers", "Total Quantity"]:
        return f"{int(value):,}"
    return f"{value:,.0f}"