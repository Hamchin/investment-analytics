import pandas as pd


def create_history_chart_options(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame,
    threshold: float,
    condition: str,
) -> dict:
    """
    時系列チャートの ECharts オプションを生成する.

    週次の騰落率が閾値を超えた期間を赤色で強調表示する.

    Args:
        daily_df (pd.DataFrame): 日次の価格データ.
        weekly_df (pd.DataFrame): 週次の価格データ.
        threshold (float): 強調表示する騰落率の閾値 (%).
        condition (str): 強調表示の条件 ("上昇" または "下落").

    Returns:
        dict: ECharts オプション.
    """
    dates = daily_df.index.strftime("%Y-%m-%d").tolist()
    prices = daily_df["Close"].round(2).tolist()

    mark_area_data: list[list[dict]] = []

    multiplier = 1 if condition == "上昇" else -1 if condition == "下落" else 0
    filtered_weekly_df = weekly_df[weekly_df["Change"] * multiplier >= threshold]

    for date, _ in filtered_weekly_df.iterrows():
        week_start = pd.Timestamp(date).strftime("%Y-%m-%d")
        week_end = (pd.Timestamp(date) + pd.Timedelta(days=6)).strftime("%Y-%m-%d")

        start_date = max(date for date in dates if date < week_start)
        end_date = max(date for date in dates if date <= week_end)

        mark_area_data.append(
            [
                {"xAxis": start_date, "itemStyle": {"color": "rgba(255, 0, 0, 0.2)"}},
                {"xAxis": end_date},
            ]
        )

    return {
        "animation": False,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
        },
        "xAxis": {
            "type": "category",
            "data": dates,
            "boundaryGap": False,
        },
        "yAxis": {
            "type": "value",
            "scale": True,
        },
        "dataZoom": [
            {
                "type": "inside",
                "xAxisIndex": 0,
            },
            {
                "type": "slider",
                "xAxisIndex": 0,
                "height": 24,
                "bottom": 10,
            },
        ],
        "series": [
            {
                "type": "line",
                "smooth": False,
                "showSymbol": False,
                "lineStyle": {"width": 2, "color": "#2563eb"},
                "data": prices,
                "markArea": {
                    "silent": True,
                    "data": mark_area_data,
                },
            },
        ],
    }


def create_realtime_chart_options(
    df: pd.DataFrame,
    previous_price: float,
    trading_hours: float,
    color: str,
) -> dict:
    """
    リアルタイムチャートの ECharts オプションを生成する.

    前日終値を基準線として表示し, 取引時間の範囲で X 軸を設定する.

    Args:
        df (pd.DataFrame): 日中の価格データ.
        previous_price (float): 前日終値.
        trading_hours (float): 取引時間.
        color (str): チャートの線色.

    Returns:
        dict: ECharts オプション.
    """
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_convert("Asia/Tokyo")

    start_time = df.index[0]
    end_time = start_time + pd.Timedelta(hours=trading_hours)
    chart_data = [[index.isoformat(), round(price, 2)] for index, price in df["Close"].items()]

    return {
        "animation": False,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
        },
        "grid": {"left": 0, "right": 0, "top": 0, "bottom": 0},
        "xAxis": {
            "type": "time",
            "min": start_time.isoformat(),
            "max": end_time.isoformat(),
            "boundaryGap": False,
            "axisLabel": {"formatter": "{HH}:{mm}"},
            "axisPointer": {"label": {"show": False}},
        },
        "yAxis": {
            "type": "value",
            "scale": True,
            "axisPointer": {"label": {"show": False}},
        },
        "series": [
            {
                "type": "line",
                "smooth": False,
                "showSymbol": False,
                "lineStyle": {"width": 2, "color": color},
                "data": chart_data,
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"type": "dashed", "color": "#9ca3af", "width": 1},
                    "label": {"show": False},
                    "data": [{"yAxis": previous_price}],
                },
            }
        ],
    }
