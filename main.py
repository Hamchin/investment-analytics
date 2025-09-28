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

PERIOD_NAME_TO_SYMBOL = {
    "1 Year": "1y",
    "5 Years": "5y",
    "10 Years": "10y",
    "Max": "max",
}

# === Streamlit アプリケーションの開始 ===

st.title("Investment Analyzer")

# 入力: 銘柄の選択
ticker_name = st.selectbox("Ticker", list(TICKER_NAME_TO_SYMBOL.keys()), index=0)
ticker_symbol = TICKER_NAME_TO_SYMBOL[ticker_name]

# 入力: 期間の選択
period_name = st.selectbox("Period", list(PERIOD_NAME_TO_SYMBOL.keys()), index=0)
period_symbol = PERIOD_NAME_TO_SYMBOL[period_name]

df = yf.Ticker(ticker_symbol).history(period=period_symbol)

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
weekly_df = weekly_df.rename(columns={"Close": "Closing Price"})

weekly_df.index = weekly_df.index - pd.Timedelta(days=6)
weekly_df.index = weekly_df.index.date
weekly_df.index.name = "Date"


def apply_color(row: pd.Series) -> pd.Series:
    color = "color: green" if row["Return"] >= 0 else "color: red"
    styles = pd.Series("", index=row.index)
    styles["Closing Price"] = color
    styles["Return"] = color
    return styles


styled_weekly_df = weekly_df.style.apply(apply_color, axis=1).format({"Closing Price": "{:.2f}", "Return": "{:+.2f}%"})

st.dataframe(styled_weekly_df)
