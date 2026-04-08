import pandas as pd
from pandas.io.formats.style import Styler


def style_daily_dataframe(df: pd.DataFrame, unit: str) -> Styler:
    """
    日次データの DataFrame をスタイル付きで整形する.

    - 列を日本語名に変換する.
    - 値の正負に応じて色分けする.

    Args:
        df (pd.DataFrame): 日次の価格データ.
        unit (str): 価格の通貨単位.

    Returns:
        Styler: スタイル・フォーマットが適用された Styler オブジェクト.
    """
    formatted_df = df[["Close", "Change", "MAD"]]
    formatted_df = formatted_df.sort_index(ascending=False)

    close_column = f"終値 ({unit})"
    change_column = "騰落率 (%)"
    mad_column = "移動平均乖離率 (%)"

    renamer = {"Close": close_column, "Change": change_column, "MAD": mad_column}
    formatted_df = formatted_df.rename(columns=renamer).round(2)

    formatted_df.index = formatted_df.index.date
    formatted_df.index.name = "日付"

    def apply_color(row: pd.Series) -> pd.Series:
        color_return = "color: green" if row[change_column] >= 0 else "color: red"
        color_deviation = "color: green" if row[mad_column] >= 0 else "color: red"
        styles = pd.Series("", index=row.index)
        styles[close_column] = color_return
        styles[change_column] = color_return
        styles[mad_column] = color_deviation
        return styles

    formatter = {close_column: "{:,.2f}", change_column: "{:+.2f}%", mad_column: "{:+.2f}%"}
    return formatted_df.style.apply(apply_color, axis=1).format(formatter)


def style_weekly_dataframe(df: pd.DataFrame, unit: str) -> Styler:
    """
    週次データの DataFrame をスタイル付きで整形する.

    - 列を日本語名に変換する.
    - 値の正負に応じて色分けする.

    Args:
        df (pd.DataFrame): 週次の価格データ.
        unit (str): 価格の通貨単位.

    Returns:
        Styler: スタイル・フォーマットが適用された Styler オブジェクト.
    """
    formatted_df = df.sort_index(ascending=False)

    close_column = f"終値 ({unit})"
    change_column = "騰落率 (%)"

    renamer = {"Close": close_column, "Change": change_column}
    formatted_df = formatted_df.rename(columns=renamer).round(2)

    formatted_df.index = formatted_df.index.date
    formatted_df.index.name = "日付"

    def apply_color(row: pd.Series) -> pd.Series:
        color_return = "color: green" if row[change_column] >= 0 else "color: red"
        styles = pd.Series("", index=row.index)
        styles[close_column] = color_return
        styles[change_column] = color_return
        return styles

    formatter = {close_column: "{:,.2f}", change_column: "{:+.2f}%"}
    return formatted_df.style.apply(apply_color, axis=1).format(formatter)
