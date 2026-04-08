import datetime

import pandas as pd


def compute_daily_metrics(df: pd.DataFrame, ma_period: int, start_date: datetime.date) -> pd.DataFrame:
    """
    日次データに騰落率・移動平均・移動平均乖離率を追加する.

    Args:
        df (pd.DataFrame): 日次の価格データ.
        ma_period (int): 移動平均の期間 (日数).
        start_date (datetime.date): フィルタリングする開始日.

    Returns:
        pd.DataFrame: 追加後の日次の価格データ.
    """
    df["Change"] = df["Close"].pct_change() * 100
    df["MA"] = df["Close"].rolling(window=ma_period).mean()
    df["MAD"] = ((df["Close"] - df["MA"]) / df["MA"]) * 100
    return df[df.index.date >= start_date]


def compute_weekly_metrics(daily_df: pd.DataFrame, start_date: datetime.date) -> pd.DataFrame:
    """
    日次データから週次の終値と騰落率を算出する.

    Args:
        daily_df (pd.DataFrame): 日次の価格データ.
        start_date (datetime.date): フィルタリングする開始日.

    Returns:
        pd.DataFrame: 週次の価格データ.
    """
    weekly_df = daily_df["Close"].resample("W").last().to_frame()
    weekly_df["Change"] = weekly_df["Close"].pct_change() * 100
    weekly_df.index = weekly_df.index - pd.Timedelta(days=6)
    return weekly_df[weekly_df.index.date >= start_date]


def compute_realtime_change(df: pd.DataFrame) -> tuple[float, float, float]:
    """
    直近の価格データから現在値・前日終値・騰落率を算出する.

    Args:
        df (pd.DataFrame): 日次の価格データ.

    Returns:
        tuple[float, float, float]: 現在値, 前日終値, 騰落率.
    """
    df = df.sort_index()
    current_price = df["Close"].iloc[-1]
    previous_price = df["Close"].iloc[-2]
    change = (current_price - previous_price) / previous_price * 100
    return current_price, previous_price, change
