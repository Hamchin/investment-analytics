import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Ticker:
    """
    銘柄を表すデータクラス.

    Attributes:
        name (str): 銘柄名.
        symbol (str): ティッカーシンボル.
        start_year (int): データの取得可能な開始年.
        trading_hours (float): 1 日あたりの取引時間.
    """

    name: str
    symbol: str
    start_year: int
    trading_hours: float


def _load_tickers() -> dict[str, Ticker]:
    """
    銘柄情報を読み込む.

    Returns:
        dict[str, Ticker]: 銘柄名をキーとする Ticker の辞書.
    """
    path = Path(__file__).parent / "tickers.json"
    with path.open() as f:
        name_to_ticker = json.load(f)
    return {name: Ticker(name=name, **ticker) for name, ticker in name_to_ticker.items()}


NAME_TO_TICKER: dict[str, Ticker] = _load_tickers()
