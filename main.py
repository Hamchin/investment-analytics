import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


st_autorefresh(interval=60000)

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

st.title("投資分析ツール")

# 入力: 銘柄の選択
ticker_name = st.selectbox("銘柄", list(TICKER_NAME_TO_SYMBOL.keys()), index=0)
ticker_symbol = TICKER_NAME_TO_SYMBOL[ticker_name]

# 入力: 期間の指定方法
period_mode = st.radio("期間の指定方法", ("直近 N 年間", "開始年 / 終了年"), horizontal=True)

period = None
start_date = None
end_date = None

# 入力: 直近 N 年間の選択
if period_mode == "直近 N 年間":
    period_name_to_period = {f"{i + 1} 年": f"{i + 1}y" for i in range(30)}
    period_name = st.selectbox("期間", list(period_name_to_period.keys()), index=0)
    period = period_name_to_period[period_name]

# 入力: 開始年 / 終了年の選択
if period_mode == "開始年 / 終了年":
    col_start_year, col_end_year = st.columns(2)
    years_range = range(TICKER_NAME_TO_START_YEAR[ticker_name], datetime.date.today().year + 1)

    start_year_to_date = {f"{year} 年": f"{year}-01-01" for year in reversed(years_range)}
    start_year = col_start_year.selectbox("開始年", list(start_year_to_date.keys()), index=0)
    start_date = start_year_to_date[start_year]

    end_year_to_date = {f"{year} 年": f"{year}-12-31" for year in reversed(years_range)}
    end_year = col_end_year.selectbox("終了年", list(end_year_to_date.keys()), index=0)
    end_date = end_year_to_date[end_year]

    if start_year > end_year:
        st.error("開始年は終了年より前の年または同じ年を選択してください。")
        st.stop()

# 日次データの作成
daily_df = yf.Ticker(ticker_symbol).history(period=period, start=start_date, end=end_date)
daily_df["Return"] = daily_df["Close"].pct_change() * 100
daily_df = daily_df.dropna()

# 週次データの作成
weekly_df = daily_df["Close"].resample("W").last().to_frame()
weekly_df["Return"] = weekly_df["Close"].pct_change() * 100
weekly_df = weekly_df.dropna()
weekly_df.index = weekly_df.index - pd.Timedelta(days=6)

# === チャートの表示 ===

st.subheader("チャート")

col_threshold, col_condition = st.columns(2)

threshold = col_threshold.number_input("強調表示の閾値 (%)", min_value=0.0, value=5.0, step=0.1)
condition = col_condition.selectbox("強調表示の条件", ("上昇", "下落"), index=1)

st.caption(f"赤色のエリアは 1 週間で {threshold:.2f}% 以上の{condition}があった週を示します。")

fig = px.line(daily_df.reset_index(), x="Date", y="Close")

fig.update_layout(xaxis_title="日付", yaxis_title="終値", hovermode="x unified")

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

fig.update_traces(hovertemplate="日付: %{x|%Y-%m-%d}<br>終値: %{y:.2f} USD<extra></extra>")

multiplier = 1 if condition == "上昇" else -1 if condition == "下落" else 0

for date, row in weekly_df[weekly_df["Return"] * multiplier >= threshold].iterrows():
    fig.add_vrect(
        x0=date,
        x1=(date + pd.Timedelta(days=6)),
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
    )

st.plotly_chart(fig, use_container_width=True)

# === 日次データの表示 ===

st.subheader("日次データ")

# 入力: 移動平均の期間
ma_period = st.number_input("移動平均の期間 (日)", min_value=1, max_value=200, value=100, step=1)

daily_df["MA"] = daily_df["Close"].rolling(window=ma_period).mean()
daily_df["MAD"] = ((daily_df["Close"] - daily_df["MA"]) / daily_df["MA"]) * 100

formatted_daily_df = daily_df[["Close", "Return", "MAD"]]
formatted_daily_df = formatted_daily_df.sort_index(ascending=False)

renamer = {"Close": "終値 (USD)", "Return": "騰落率 (%)", "MAD": "移動平均乖離率 (%)"}
formatted_daily_df = formatted_daily_df.rename(columns=renamer)

formatted_daily_df.index = formatted_daily_df.index.date
formatted_daily_df.index.name = "日付"


def apply_color_daily(row: pd.Series) -> pd.Series:
    color_return = "color: green" if row["騰落率 (%)"] >= 0 else "color: red"
    color_deviation = "color: green" if row["移動平均乖離率 (%)"] >= 0 else "color: red"
    styles = pd.Series("", index=row.index)
    styles["終値 (USD)"] = color_return
    styles["騰落率 (%)"] = color_return
    styles["移動平均乖離率 (%)"] = color_deviation
    return styles


formatter = {"終値 (USD)": "{:.2f}", "騰落率 (%)": "{:+.2f}%", "移動平均乖離率 (%)": "{:+.2f}%"}
styled_daily_df = formatted_daily_df.style.apply(apply_color_daily, axis=1).format(formatter)

st.dataframe(styled_daily_df)

# === 週次データの表示 ===

st.subheader("週次データ")

formatted_weekly_df = weekly_df.sort_index(ascending=False)

renamer = {"Close": "終値 (USD)", "Return": "騰落率 (%)"}
formatted_weekly_df = formatted_weekly_df.rename(columns=renamer)

formatted_weekly_df.index = formatted_weekly_df.index.date
formatted_weekly_df.index.name = "日付"


def apply_color_weekly(row: pd.Series) -> pd.Series:
    color_return = "color: green" if row["騰落率 (%)"] >= 0 else "color: red"
    styles = pd.Series("", index=row.index)
    styles["終値 (USD)"] = color_return
    styles["騰落率 (%)"] = color_return
    return styles


formatter = {"終値 (USD)": "{:.2f}", "騰落率 (%)": "{:+.2f}%"}
styled_weekly_df = formatted_weekly_df.style.apply(apply_color_weekly, axis=1).format(formatter)

st.dataframe(styled_weekly_df)
