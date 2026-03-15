import pandas as pd
from pandas.io.formats.style import Styler


def style_daily_dataframe(df: pd.DataFrame) -> Styler:
    """
    日次データの DataFrame をスタイル付きで整形する.

    列を日本語名に変換し, 値の正負に応じて緑色・赤色で色分けする.

    Args:
        df (pd.DataFrame): 日次 DataFrame.

    Returns:
        Styler: スタイル・フォーマットが適用された Styler オブジェクト.
    """
    formatted_df = df[["Close", "Change", "MAD"]]
    formatted_df = formatted_df.sort_index(ascending=False)

    renamer = {"Close": "終値 (USD)", "Change": "騰落率 (%)", "MAD": "移動平均乖離率 (%)"}
    formatted_df = formatted_df.rename(columns=renamer)

    formatted_df.index = formatted_df.index.date
    formatted_df.index.name = "日付"

    def apply_color(row: pd.Series) -> pd.Series:
        color_return = "color: green" if row["騰落率 (%)"] >= 0 else "color: red"
        color_deviation = "color: green" if row["移動平均乖離率 (%)"] >= 0 else "color: red"
        styles = pd.Series("", index=row.index)
        styles["終値 (USD)"] = color_return
        styles["騰落率 (%)"] = color_return
        styles["移動平均乖離率 (%)"] = color_deviation
        return styles

    formatter = {"終値 (USD)": "{:.2f}", "騰落率 (%)": "{:+.2f}%", "移動平均乖離率 (%)": "{:+.2f}%"}
    return formatted_df.style.apply(apply_color, axis=1).format(formatter)


def style_weekly_dataframe(df: pd.DataFrame) -> Styler:
    """
    週次データの DataFrame をスタイル付きで整形する.

    列を日本語名に変換し, 値の正負に応じて緑色・赤色で色分けする.

    Args:
        df (pd.DataFrame): 週次 DataFrame.

    Returns:
        Styler: スタイル・フォーマットが適用された Styler オブジェクト.
    """
    formatted_df = df.sort_index(ascending=False)

    renamer = {"Close": "終値 (USD)", "Change": "騰落率 (%)"}
    formatted_df = formatted_df.rename(columns=renamer)

    formatted_df.index = formatted_df.index.date
    formatted_df.index.name = "日付"

    def apply_color(row: pd.Series) -> pd.Series:
        color_return = "color: green" if row["騰落率 (%)"] >= 0 else "color: red"
        styles = pd.Series("", index=row.index)
        styles["終値 (USD)"] = color_return
        styles["騰落率 (%)"] = color_return
        return styles

    formatter = {"終値 (USD)": "{:.2f}", "騰落率 (%)": "{:+.2f}%"}
    return formatted_df.style.apply(apply_color, axis=1).format(formatter)
