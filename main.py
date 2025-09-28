import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


# === 選択肢の定義 ===

TICKER_NAME_TO_SYMBOL = {
    "S&P500": "^GSPC",
    "NASDAQ100": "^NDX",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}

TICKER_NAME_TO_START_YEAR = {
    "S&P500": 1928,
    "NASDAQ100": 1985,
    "BTC": 2014,
    "ETH": 2017,
}

# === Streamlit アプリケーションの開始 ===

st.title("Investment Analyzer")

# 入力: 銘柄の選択
ticker_name = st.selectbox("Ticker", list(TICKER_NAME_TO_SYMBOL.keys()), index=0)
ticker_symbol = TICKER_NAME_TO_SYMBOL[ticker_name]

# 入力: 期間の指定方法
period_mode = st.radio("How to Specify the Period", ("Period", "Start Year / End Year"), horizontal=True)

period = None
start_date = None
end_date = None

# 入力: 期間の選択
if period_mode == "Period":
    period_name_to_period = {f"{i + 1} Years": f"{i + 1}y" for i in range(30)} | {"Max": "max"}
    period_name = st.selectbox("Period", list(period_name_to_period.keys()), index=0)
    period = period_name_to_period[period_name]

# 入力: 開始年・終了年の選択
if period_mode == "Start Year / End Year":
    col_start_year, col_end_year = st.columns(2)
    years_range = range(TICKER_NAME_TO_START_YEAR[ticker_name], datetime.date.today().year + 1)

    start_year_to_date = {f"{year}": f"{year}-01-01" for year in reversed(years_range)}
    start_year = col_start_year.selectbox("Start Year", list(start_year_to_date.keys()), index=0)
    start_date = start_year_to_date[start_year]

    end_year_to_date = {f"{year}": f"{year}-12-31" for year in reversed(years_range)}
    end_year = col_end_year.selectbox("End Year", list(end_year_to_date.keys()), index=0)
    end_date = end_year_to_date[end_year]

    if start_year > end_year:
        st.error("Start Year must be less than or equal to End Year.")
        st.stop()

history_kwargs = {"period": period, "start": start_date, "end": end_date}

df = yf.Ticker(ticker_symbol).history(**history_kwargs)

weekly_df = df["Close"].resample("W").last().to_frame()
weekly_df["Return"] = weekly_df["Close"].pct_change() * 100
weekly_df = weekly_df.dropna()

# === チャートの表示 ===

st.subheader("Chart")

st.caption("Red shaded areas indicate weeks with a drop of 5% or more.")

fig = px.line(df.reset_index(), x="Date", y="Close")

fig.update_layout(xaxis_title="Date", yaxis_title="Closing Price", hovermode="x unified")

fig.update_xaxes(
    rangeslider_visible=True,
    showline=True,
    showgrid=True,
    showspikes=True,
    spikemode="across",
    spikesnap="cursor",
)

fig.update_yaxes(
    showline=True,
    showgrid=True,
    showspikes=True,
    spikemode="across",
    spikesnap="cursor",
)

fig.update_traces(hovertemplate="Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f} USD<extra></extra>")

for date, row in weekly_df.iterrows():
    if row["Return"] <= -5:
        week_start = date - pd.Timedelta(days=6)
        week_end = date
        fig.add_vrect(
            x0=week_start,
            x1=week_end,
            fillcolor="red",
            opacity=0.2,
            layer="below",
            line_width=0,
        )

st.plotly_chart(fig, use_container_width=True)

# === 週次データの表示 ===

st.subheader("Weekly Historical Data")

weekly_df = weekly_df.sort_index(ascending=False)
weekly_df = weekly_df.rename(columns={"Close": "Closing Price (USD)", "Return": "Return (%)"})

weekly_df.index = weekly_df.index - pd.Timedelta(days=6)
weekly_df.index = weekly_df.index.date
weekly_df.index.name = "Date"


def apply_color(row: pd.Series) -> pd.Series:
    color = "color: green" if row["Return (%)"] >= 0 else "color: red"
    styles = pd.Series("", index=row.index)
    styles["Closing Price (USD)"] = color
    styles["Return (%)"] = color
    return styles


styled_weekly_df = weekly_df.style.apply(apply_color, axis=1).format(
    {"Closing Price (USD)": "{:.2f}", "Return (%)": "{:+.2f}%"}
)

st.dataframe(styled_weekly_df)
