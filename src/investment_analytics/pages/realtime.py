import streamlit as st

from investment_analytics.components.charts import create_realtime_chart
from investment_analytics.models.ticker import NAME_TO_TICKER
from investment_analytics.services.analysis import compute_realtime_change
from investment_analytics.services.market_data import fetch_history
from investment_analytics.services.realtime_state import append_ticker_data
from investment_analytics.services.realtime_state import init_ticker_data
from investment_analytics.services.realtime_state import move_ticker_data
from investment_analytics.services.realtime_state import remove_ticker_data
from investment_analytics.services.realtime_state import update_ticker_data

st.title("リアルタイム分析")

ticker_names = list(NAME_TO_TICKER)

init_ticker_data()

id_to_container = {}

global_columns = st.columns(3)

# 各コンテナに入力ウィジェットを表示

for index, (id, ticker_name) in enumerate(st.session_state["realtime_ticker_data"].items()):
    global_column = global_columns[index % 3]
    container = global_column.container(border=True)

    # 銘柄のセレクトボックス
    container.selectbox(
        "銘柄",
        ticker_names,
        index=ticker_names.index(ticker_name),
        key=f"realtime_ticker_{id}",
        on_change=update_ticker_data,
        args=(id, f"realtime_ticker_{id}"),
    )

    # リアルタイム情報を表示するコンテナ
    inner_container = container.container()
    id_to_container[id] = inner_container

    # コンテナを移動・削除するボタン
    button_columns = container.columns([1, 1, 1, 3])
    button_columns[0].button(
        ":material/arrow_back_ios_new:",
        key=f"move_back_ticker_{id}",
        on_click=move_ticker_data,
        args=(id, "back"),
    )
    button_columns[1].button(
        ":material/arrow_forward_ios:",
        key=f"move_forward_ticker_{id}",
        on_click=move_ticker_data,
        args=(id, "forward"),
    )
    button_columns[2].button(
        ":material/delete:",
        key=f"remove_ticker_{id}",
        on_click=remove_ticker_data,
        args=(id,),
    )

st.button(":material/add_2:", on_click=append_ticker_data)

# 各コンテナにリアルタイム情報を表示

for id, container in id_to_container.items():
    ticker_name = st.session_state["realtime_ticker_data"][id]
    ticker = NAME_TO_TICKER[ticker_name]

    # 現在値と前日比の表示
    recent_df = fetch_history(ticker.symbol, period="3d")
    current_price, previous_price, change = compute_realtime_change(recent_df)
    color = "green" if change >= 0 else "red"
    container.subheader(f"{current_price:.2f} :{color}[({change:+.2f}%)]")

    # チャートの表示
    df = fetch_history(ticker.symbol, period="1d", interval="1m").reset_index()

    if df.empty:
        continue

    fig = create_realtime_chart(df, previous_price, ticker.trading_hours, color)
    container.plotly_chart(fig, key=f"realtime_chart_{id}")
