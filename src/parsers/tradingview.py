from pathlib import Path
from typing import List, Union

from src.models.stock import StockData, TradingViewData
from src.utils.file_io import read_file

def parse_tradingview_watchlist(file_path: Union[str, Path]) -> List[StockData]:
    """
    TradingViewのウォッチリストファイルを解析する

    Args:
        file_path: ファイルパス

    Returns:
        StockDataオブジェクトのリスト
    """
    content = read_file(file_path)
    lines = content.strip().split('\n')
    
    stocks = []
    current_section = None
    
    # 全ての行を結合し、カンマで分割
    all_items = []
    for line in lines:
        all_items.extend([item.strip() for item in line.split(',')])

    for item in all_items:
        if not item:
            continue

        if item.startswith("###SECTION"):
            current_section = item
            continue

        parts = item.split(':', 1)
        if len(parts) == 2:
            exchange, symbol = parts
        else:
            # 取引所プレフィックスがない場合はスキップ
            continue

        stock_data = StockData(
            symbol=symbol,
            exchange=exchange,
            full_symbol=item,
            platform_data=TradingViewData(section=current_section)
        )
        stocks.append(stock_data)
            
    return stocks
