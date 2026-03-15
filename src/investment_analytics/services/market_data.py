import datetime

import pandas as pd
import yfinance as yf


def fetch_history(
    symbol: str,
    period: str | None = None,
    interval: str = "1d",
    start: datetime.date | None = None,
    end: datetime.date | None = None,
) -> pd.DataFrame:
    """
    価格データを取得する.

    Args:
        symbol (str): ティッカーシンボル.
        period (str | None, optional): 取得期間. (Default: None)
        interval (str, optional): データの間隔. (Default: "1d")
        start (datetime.date | None, optional): 取得開始日. (Default: None)
        end (datetime.date | None, optional): 取得終了日. (Default: None)

    Returns:
        pd.DataFrame: 価格データ.
    """
    return yf.Ticker(symbol).history(period=period, interval=interval, start=start, end=end)
