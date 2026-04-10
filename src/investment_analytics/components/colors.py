COLOR_TO_RGB = {
    "green": (34, 197, 94),
    "red": (239, 68, 68),
}


def to_rgb_format(color: str, alpha: float | None = None) -> str:
    """
    RGB または RGBA 形式の文字列に変換する.

    Args:
        color (str): 色.
        alpha (float | None, optional): 透明度. (Default: None)

    Returns:
        str: RGB または RGBA 形式の文字列.
    """
    rgb = COLOR_TO_RGB[color]

    if alpha is None:
        return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
