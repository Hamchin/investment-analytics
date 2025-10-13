import datetime
import uuid

import plotly.express as px
import streamlit as st
import yfinance as yf
from constants import TICKER_NAME_TO_HOURS
from constants import TICKER_NAME_TO_SYMBOL
from streamlit_autorefresh import st_autorefresh


# 1 分ごとに自動更新
st_autorefresh(interval=60000)

# ========== 各コンテナに入力ウィジェットを表示 ==========

st.title("リアルタイム分析")


def append_ticker_data(ticker_name: str = "S&P500") -> None:
    id = str(uuid.uuid4())
    st.session_state["realtime_ticker_data"][id] = ticker_name


def update_ticker_data(id: str, key: str) -> None:
    st.session_state["realtime_ticker_data"][id] = st.session_state[key]


def remove_ticker_data(id: str) -> None:
    del st.session_state["realtime_ticker_data"][id]


if "realtime_ticker_data" not in st.session_state:
    st.session_state["realtime_ticker_data"] = {}
    append_ticker_data("S&P500")
    append_ticker_data("NASDAQ100")
    append_ticker_data("QLD")
    append_ticker_data("SOXL")
    append_ticker_data("BTC")
    append_ticker_data("ETH")

id_to_container = {}

global_columns = st.columns(3)

for index, (id, ticker_name) in enumerate(st.session_state["realtime_ticker_data"].items()):
    global_column = global_columns[index % 3]
    container = global_column.container(border=True)
    container.selectbox(
        "銘柄",
        list(TICKER_NAME_TO_SYMBOL),
        index=list(TICKER_NAME_TO_SYMBOL).index(ticker_name),
        key=f"realtime_ticker_{id}",
        on_change=update_ticker_data,
        args=(id, f"realtime_ticker_{id}"),
    )
    inner_container = container.container()
    container.button(
        ":material/delete:",
        key=f"remove_ticker_{id}",
        on_click=remove_ticker_data,
        args=(id,),
    )
    id_to_container[id] = inner_container

st.button(":material/add_2:", on_click=append_ticker_data)

# ========== 各コンテナにリアルタイム情報を表示 ==========

for id, container in id_to_container.items():
    ticker_name = st.session_state["realtime_ticker_data"][id]
    ticker = yf.Ticker(TICKER_NAME_TO_SYMBOL[ticker_name])

    # 現在値と前日比の表示
    df = ticker.history(period="3d")
    previous_price = df["Close"].iloc[0]
    current_price = df["Close"].iloc[1]
    change = (current_price - previous_price) / previous_price * 100
    color = "green" if change >= 0 else "red"
    container.subheader(f"{current_price:.2f} :{color}[({change:.2f}%)]")

    # チャートの表示
    df = ticker.history(period="1d", interval="1m").reset_index()

    if df.empty:
        continue

    df["Datetime"] = df["Datetime"].dt.tz_convert("Asia/Tokyo")
    start_time = df["Datetime"].iloc[0]
    end_time = start_time + datetime.timedelta(hours=TICKER_NAME_TO_HOURS[ticker_name])

    fig = px.line(df, x="Datetime", y="Close")
    fig.add_hline(y=previous_price, line_dash="dot", line_color="gray")
    fig.update_layout(xaxis_title=None, yaxis_title=None, height=300, hovermode="x unified")
    fig.update_xaxes(range=[start_time, end_time])
    fig.update_traces(line_color=color, hovertemplate="時間: %{x|%Y-%m-%d %H:%M}<br>価格: %{y:.2f} USD<extra></extra>")
    container.plotly_chart(fig, key=f"realtime_chart_{id}")
