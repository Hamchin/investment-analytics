import datetime

import streamlit as st
from dateutil.relativedelta import relativedelta

from investment_analytics.components.charts import create_price_chart
from investment_analytics.components.styles import style_daily_dataframe
from investment_analytics.components.styles import style_weekly_dataframe
from investment_analytics.models.ticker import NAME_TO_TICKER
from investment_analytics.models.ticker import SYMBOL_TO_TICKER
from investment_analytics.services.analysis import compute_daily_metrics
from investment_analytics.services.analysis import compute_weekly_metrics
from investment_analytics.services.market_data import fetch_history

st.title("時系列分析")

# 入力: 銘柄
ticker_name = st.selectbox(
    "銘柄",
    list(NAME_TO_TICKER),
    index=list(SYMBOL_TO_TICKER).index(st.query_params.get("ticker", "^GSPC")),
    key="history_ticker",
    on_change=lambda: st.query_params.update({"ticker": NAME_TO_TICKER[st.session_state["history_ticker"]].symbol}),
)
ticker = NAME_TO_TICKER[ticker_name]

# 入力: 期間の指定方法
period_mode = st.radio("期間の指定方法", ("期間", "開始年・終了年"), horizontal=True)

start_date = None
end_date = None

# 入力: 期間
if period_mode == "期間":
    period_name_to_period = {f"{i + 1} 年": i + 1 for i in range(30)}
    period_name = st.selectbox("期間", list(period_name_to_period), index=0)
    period = period_name_to_period[period_name]
    end_date = datetime.date.today() + datetime.timedelta(days=1)
    start_date = end_date - relativedelta(years=period)

# 入力: 開始年・終了年
if period_mode == "開始年・終了年":
    col_start_year, col_end_year = st.columns(2)
    years_range = range(ticker.start_year, datetime.date.today().year + 1)

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

settings_expander = st.expander("設定")

# 入力: 移動平均の期間
ma_period = settings_expander.number_input("移動平均の期間 (日)", min_value=1, max_value=200, value=100, step=1)

# データの取得と加工
raw_df = fetch_history(ticker.symbol, start=(start_date - datetime.timedelta(days=200)), end=end_date)
daily_df = compute_daily_metrics(raw_df, ma_period, start_date)
weekly_df = compute_weekly_metrics(daily_df, start_date)

st.subheader("チャート")

chart_settings_expander = st.expander("設定")

col_threshold, col_condition = chart_settings_expander.columns(2)

# 入力: 強調表示の閾値と条件
threshold = col_threshold.number_input("強調表示の閾値 (%)", min_value=0.0, value=5.0, step=0.1)
condition = col_condition.selectbox("強調表示の条件", ("上昇", "下落"), index=1)

st.caption(f"赤色のエリアは 1 週間で {threshold:.2f}% 以上の{condition}があった週を示します。")

fig = create_price_chart(daily_df, weekly_df, ticker.unit, threshold, condition)
st.plotly_chart(fig)

col_daily, col_weekly = st.columns(2)

with col_daily:
    st.subheader("日次データ")
    st.dataframe(style_daily_dataframe(daily_df, ticker.unit))

with col_weekly:
    st.subheader("週次データ")
    st.dataframe(style_weekly_dataframe(weekly_df, ticker.unit))
