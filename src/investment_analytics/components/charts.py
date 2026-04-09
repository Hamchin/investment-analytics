import pandas as pd
from matplotlib import colors


def _create_area_gradient(color: str) -> dict:
    """
    チャートのエリアグラデーションを生成する.

    Args:
        color (str): ベースとなる色.

    Returns:
        dict: グラデーションの設定.
    """
    red, green, blue = [int(value * 255) for value in colors.to_rgb(color)]

    return {
        "type": "linear",
        "x": 0,
        "y": 0,
        "x2": 0,
        "y2": 1,
        "colorStops": [
            {"offset": 0, "color": f"rgba({red}, {green}, {blue}, 0.35)"},
            {"offset": 1, "color": f"rgba({red}, {green}, {blue}, 0.05)"},
        ],
    }


def create_history_chart_options(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame,
    highlight_threshold: float,
    highlight_condition: str,
    color: str,
) -> dict:
    """
    時系列チャートの ECharts オプションを生成する.

    - 週次の騰落率が閾値を超えた期間をハイライトする.
    - 現在値を基準線として表示する.

    Args:
        daily_df (pd.DataFrame): 日次の価格データ.
        weekly_df (pd.DataFrame): 週次の価格データ.
        highlight_threshold (float): ハイライトする騰落率の閾値 (%).
        highlight_condition (str): ハイライトの条件 ("上昇" または "下落").
        color (str): チャートの色.

    Returns:
        dict: ECharts オプション.
    """
    daily_df = daily_df.copy()
    daily_df = daily_df.dropna(subset=["Close"])
    daily_df.index = pd.to_datetime(daily_df.index)

    current_price = daily_df["Close"].iloc[-1]
    min_visible_price = daily_df["Close"].min()
    max_visible_price = daily_df["Close"].max()
    y_axis_padding = (max_visible_price - min_visible_price) * 0.05

    highlight_area_list: list[list[dict]] = []

    multiplier = 1 if highlight_condition == "上昇" else -1 if highlight_condition == "下落" else 0
    filtered_weekly_df = weekly_df[weekly_df["Change"] * multiplier >= highlight_threshold]

    for date in filtered_weekly_df.index:
        week_start = pd.Timestamp(date)
        week_end = pd.Timestamp(date) + pd.Timedelta(days=6)

        start_date = max(date for date in daily_df.index if date < week_start)
        end_date = max(date for date in daily_df.index if date <= week_end)

        highlight_area_list.append(
            [
                {"xAxis": start_date.strftime("%Y-%m-%d"), "itemStyle": {"color": "rgba(255, 0, 0, 0.2)"}},
                {"xAxis": end_date.strftime("%Y-%m-%d")},
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
            "data": daily_df.index.strftime("%Y-%m-%d").tolist(),
            "boundaryGap": False,
        },
        "yAxis": {
            "type": "value",
            "min": min_visible_price - y_axis_padding,
            "max": max_visible_price + y_axis_padding,
            "axisLabel": {"showMinLabel": False, "showMaxLabel": False},
        },
        "series": [
            {
                "type": "line",
                "smooth": False,
                "showSymbol": False,
                "lineStyle": {"width": 2, "color": color},
                "areaStyle": {"color": _create_area_gradient(color)},
                "data": daily_df["Close"].round(2).tolist(),
                "markArea": {
                    "silent": True,
                    "data": highlight_area_list,
                },
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"type": "dashed", "color": "#9ca3af", "width": 1},
                    "data": [{"yAxis": current_price}],
                },
            },
        ],
    }


def create_realtime_chart_options(
    df: pd.DataFrame,
    trading_hours: float,
    previous_price: float,
    color: str,
) -> dict:
    """
    リアルタイムチャートの ECharts オプションを生成する.

    - 前日終値を基準線として表示する.
    - 取引時間の範囲で X 軸を設定する.

    Args:
        df (pd.DataFrame): 日中の価格データ.
        trading_hours (float): 取引時間.
        previous_price (float): 前日終値.
        color (str): チャートの色.

    Returns:
        dict: ECharts オプション.
    """
    df = df.copy()
    df = df.dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index).tz_convert("Asia/Tokyo")

    start_time = df.index[0]
    end_time = start_time + pd.Timedelta(hours=trading_hours)

    min_visible_price = min(df["Close"].min(), previous_price)
    max_visible_price = max(df["Close"].max(), previous_price)
    y_axis_padding = (max_visible_price - min_visible_price) * 0.05

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
            "min": min_visible_price - y_axis_padding,
            "max": max_visible_price + y_axis_padding,
            "axisLabel": {"showMinLabel": False, "showMaxLabel": False},
            "axisPointer": {"label": {"show": False}},
        },
        "series": [
            {
                "type": "line",
                "smooth": False,
                "showSymbol": False,
                "lineStyle": {"width": 2, "color": color},
                "areaStyle": {"color": _create_area_gradient(color)},
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
