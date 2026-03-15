import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_price_chart(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame,
    unit: str,
    threshold: float,
    condition: str,
) -> go.Figure:
    """
    時系列の価格チャートを生成する.

    週次の騰落率が閾値を超えた期間を赤色で強調表示する.

    Args:
        daily_df (pd.DataFrame): 日次の価格データを含む DataFrame.
        weekly_df (pd.DataFrame): 週次の価格・騰落率データを含む DataFrame.
        unit (str): 価格の通貨単位.
        threshold (float): 強調表示する騰落率の閾値 (%).
        condition (str): 強調表示の条件 ("上昇" または "下落").

    Returns:
        go.Figure: Plotly の Figure オブジェクト.
    """
    fig = px.line(daily_df.reset_index(), x="Date", y="Close")

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

    fig.update_traces(hovertemplate=f"日付: %{{x|%Y-%m-%d}}<br>終値: %{{y:.2f}} {unit}<extra></extra>")

    multiplier = 1 if condition == "上昇" else -1 if condition == "下落" else 0

    for date, _ in weekly_df[weekly_df["Change"] * multiplier >= threshold].iterrows():
        fig.add_vrect(
            x0=date,
            x1=(date + pd.Timedelta(days=6)),
            fillcolor="red",
            opacity=0.2,
            layer="below",
            line_width=0,
        )

    return fig


def create_realtime_chart(
    df: pd.DataFrame,
    previous_price: float,
    trading_hours: float,
    unit: str,
    color: str,
) -> go.Figure:
    """
    リアルタイムの日中チャートを生成する.

    前日終値を基準線として表示し, 取引時間の範囲で X 軸を設定する.

    Args:
        df (pd.DataFrame): 日中の価格データを含む DataFrame.
        previous_price (float): 前日終値.
        trading_hours (float): 取引時間.
        unit (str): 価格の通貨単位.
        color (str): チャートの線色.

    Returns:
        go.Figure: Plotly の Figure オブジェクト.
    """
    df["Datetime"] = df["Datetime"].dt.tz_convert("Asia/Tokyo")
    start_time = df["Datetime"].iloc[0]
    end_time = start_time + datetime.timedelta(hours=trading_hours)

    fig = px.line(df, x="Datetime", y="Close")
    fig.add_hline(y=previous_price, line_dash="dot", line_color="gray")
    fig.update_xaxes(range=[start_time, end_time])
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        height=200,
        hovermode="x unified",
        margin={"t": 0, "b": 0},
    )
    fig.update_traces(
        line_color=color,
        hovertemplate=f"時間: %{{x|%Y-%m-%d %H:%M}}<br>価格: %{{y:.2f}} {unit}<extra></extra>",
    )

    return fig
