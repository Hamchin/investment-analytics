import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Ticker:
    """
    銘柄を表すデータクラス.

    Attributes:
        symbol (str): 銘柄のシンボル.
        name (str): 銘柄名.
        unit (str): 価格の通貨単位.
        start_year (int): データの取得可能な開始年.
        trading_hours (float): 1 日あたりの取引時間.
    """

    symbol: str
    name: str
    unit: str
    start_year: int
    trading_hours: float


def _load_tickers() -> dict[str, Ticker]:
    """
    銘柄情報を読み込む.

    Returns:
        dict[str, Ticker]: 銘柄のシンボルをキーとする Ticker の辞書.
    """
    path = Path(__file__).parent / "tickers.json"
    with path.open() as f:
        symbol_to_ticker = json.load(f)
    return {symbol: Ticker(symbol=symbol, **ticker) for symbol, ticker in symbol_to_ticker.items()}


SYMBOL_TO_TICKER: dict[str, Ticker] = _load_tickers()

NAME_TO_TICKER: dict[str, Ticker] = {ticker.name: ticker for ticker in SYMBOL_TO_TICKER.values()}
