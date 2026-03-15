from urllib.parse import quote

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

NUM_COLUMNS = 4

st.title("リアルタイム分析")

ticker_names = list(NAME_TO_TICKER)

init_ticker_data()

id_to_container = {}

global_columns = st.columns(NUM_COLUMNS)

# 各カードに入力ウィジェットを表示

for index, (id, ticker_name) in enumerate(st.session_state["realtime_ticker_data"].items()):
    global_column = global_columns[index % NUM_COLUMNS]
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

    # フッター
    footer = container.columns(4)

    # カードを左に移動するボタン
    footer[0].button(
        ":material/arrow_back_ios_new:",
        key=f"move_back_ticker_{id}",
        on_click=move_ticker_data,
        args=(id, "back"),
        use_container_width=True,
    )

    # カードを右に移動するボタン
    footer[1].button(
        ":material/arrow_forward_ios:",
        key=f"move_forward_ticker_{id}",
        on_click=move_ticker_data,
        args=(id, "forward"),
        use_container_width=True,
    )

    # 時系列分析へのリンクボタン
    footer[2].link_button(
        ":material/finance:",
        f"history?ticker={quote(ticker_name)}",
        use_container_width=True,
    )

    # カードを削除するボタン
    footer[3].button(
        ":material/delete:",
        key=f"remove_ticker_{id}",
        on_click=remove_ticker_data,
        args=(id,),
        use_container_width=True,
    )

st.button(":material/add_2:", on_click=append_ticker_data)

# 各カードにリアルタイム情報を表示

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
