import uuid

import streamlit as st

from investment_analytics.models.ticker import NAME_TO_TICKER

DEFAULT_TICKER_SYMBOLS = [
    "^GSPC",
    "^NDX",
    "QLD",
    "TQQQ",
    "BTC-USD",
    "BTC-JPY",
    "ETH-USD",
    "ETH-JPY",
    "GC=F",
    "JPY=X",
]


def append_ticker_data(ticker_symbol: str = "^GSPC") -> None:
    """
    銘柄カードを追加する.

    Args:
        ticker_symbol (str): 銘柄のシンボル.
    """
    id = str(uuid.uuid4())
    st.session_state["realtime_ticker_data"][id] = ticker_symbol


def update_ticker_data(id: str, key: str) -> None:
    """
    銘柄カードの銘柄を変更する.

    Args:
        id (str): 変更対象のカード ID.
        key (str): 銘柄名が保存されているセッションステートのキー.
    """
    ticker_name = st.session_state[key]
    ticker_symbol = NAME_TO_TICKER[ticker_name].symbol
    st.session_state["realtime_ticker_data"][id] = ticker_symbol


def move_ticker_data(id: str, direction: str) -> None:
    """
    銘柄カードの表示順を移動する.

    Args:
        id (str): 移動対象のカード ID.
        direction (str): 移動方向 ("back" または "forward").
    """
    id_list = list(st.session_state["realtime_ticker_data"].keys())
    index = id_list.index(id)

    if direction == "back" and index > 0:
        id_list[index], id_list[index - 1] = id_list[index - 1], id_list[index]

    if direction == "forward" and index < len(id_list) - 1:
        id_list[index], id_list[index + 1] = id_list[index + 1], id_list[index]

    st.session_state["realtime_ticker_data"] = {id: st.session_state["realtime_ticker_data"][id] for id in id_list}


def remove_ticker_data(id: str) -> None:
    """
    銘柄カードを削除する.

    Args:
        id (str): 削除対象のカード ID.
    """
    del st.session_state["realtime_ticker_data"][id]


def init_ticker_data() -> None:
    """
    銘柄カードのセッションステートを初期化する.
    """
    if "realtime_ticker_data" not in st.session_state:
        st.session_state["realtime_ticker_data"] = {}
        for ticker_symbol in DEFAULT_TICKER_SYMBOLS:
            append_ticker_data(ticker_symbol)
