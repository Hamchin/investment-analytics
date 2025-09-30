import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from dateutil.relativedelta import relativedelta
from streamlit_autorefresh import st_autorefresh


st_autorefresh(interval=60000)

# ========== 選択肢の定義 ==========

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

# ========== Streamlit アプリケーションの開始 ==========

st.title("投資分析ツール")

# 入力: 銘柄の選択
ticker_name = st.selectbox(
    "銘柄",
    list(TICKER_NAME_TO_SYMBOL),
    index=list(TICKER_NAME_TO_SYMBOL).index(st.query_params.get("ticker", "S&P500")),
    key="ticker",
    on_change=lambda: st.query_params.update({"ticker": st.session_state["ticker"]}),
)
ticker_symbol = TICKER_NAME_TO_SYMBOL[ticker_name]

# 入力: 期間の指定方法
period_mode = st.radio("期間の指定方法", ("期間", "開始年・終了年"), horizontal=True)

start_date = None
end_date = None

# 入力: 期間の選択
if period_mode == "期間":
    period_name_to_period = {f"{i + 1} 年": i + 1 for i in range(30)}
    period_name = st.selectbox("期間", list(period_name_to_period), index=0)
    period = period_name_to_period[period_name]
    end_date = datetime.date.today() + datetime.timedelta(days=1)
    start_date = end_date - relativedelta(years=period)

# 入力: 開始年・終了年の選択
if period_mode == "開始年・終了年":
    col_start_year, col_end_year = st.columns(2)
    years_range = range(TICKER_NAME_TO_START_YEAR[ticker_name], datetime.date.today().year + 1)

    start_year_to_date = {f"{year} 年": datetime.date(year, 1, 1) for year in reversed(years_range)}
    start_year = col_start_year.selectbox("開始年", list(start_year_to_date), index=0)
    start_date = start_year_to_date[start_year]

    end_year_to_date = {f"{year} 年": datetime.date(year + 1, 1, 1) for year in reversed(years_range)}
    end_year = col_end_year.selectbox("終了年", list(end_year_to_date), index=0)
    end_date = end_year_to_date[end_year]

    if start_year > end_year:
        st.error("開始年は終了年より前の年または同じ年を選択してください。")
        st.stop()

if start_date is None or end_date is None:
    raise ValueError("Both start_date and end_date must be set.")

# 日次データの作成
daily_df = yf.Ticker(ticker_symbol).history(start=(start_date - datetime.timedelta(days=200)), end=end_date)
daily_df["Change"] = daily_df["Close"].pct_change() * 100
daily_df = daily_df.dropna()

# 週次データの作成
weekly_df = daily_df["Close"].resample("W").last().to_frame()
weekly_df["Change"] = weekly_df["Close"].pct_change() * 100
weekly_df = weekly_df.dropna()
weekly_df.index = weekly_df.index - pd.Timedelta(days=6)
weekly_df = weekly_df[weekly_df.index.date >= start_date]

# ========== チャートの表示 ==========

st.subheader("チャート")

chart_settings_expander = st.expander("設定")

col_threshold, col_condition = chart_settings_expander.columns(2)

# 入力: 強調表示の閾値と条件
threshold = col_threshold.number_input("強調表示の閾値 (%)", min_value=0.0, value=5.0, step=0.1)
condition = col_condition.selectbox("強調表示の条件", ("上昇", "下落"), index=1)

st.caption(f"赤色のエリアは 1 週間で {threshold:.2f}% 以上の{condition}があった週を示します。")

plotted_daily_df = daily_df[daily_df.index.date >= start_date].reset_index()
fig = px.line(plotted_daily_df, x="Date", y="Close")

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

for date, row in weekly_df[weekly_df["Change"] * multiplier >= threshold].iterrows():
    fig.add_vrect(
        x0=date,
        x1=(date + pd.Timedelta(days=6)),
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
    )

st.plotly_chart(fig, use_container_width=True)

# ========== 日次データの表示 ==========

st.subheader("日次データ")

daily_settings_expander = st.expander("設定")

# 入力: 移動平均の期間
ma_period = daily_settings_expander.number_input("移動平均の期間 (日)", min_value=1, max_value=200, value=100, step=1)

daily_df["MA"] = daily_df["Close"].rolling(window=ma_period).mean()
daily_df["MAD"] = ((daily_df["Close"] - daily_df["MA"]) / daily_df["MA"]) * 100
daily_df = daily_df[daily_df.index.date >= start_date]

formatted_daily_df = daily_df[["Close", "Change", "MAD"]]
formatted_daily_df = formatted_daily_df.sort_index(ascending=False)

renamer = {"Close": "終値 (USD)", "Change": "騰落率 (%)", "MAD": "移動平均乖離率 (%)"}
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

# ========== 週次データの表示 ==========

st.subheader("週次データ")

formatted_weekly_df = weekly_df.sort_index(ascending=False)

renamer = {"Close": "終値 (USD)", "Change": "騰落率 (%)"}
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
