from pathlib import Path
from typing import List, Union, Any, Optional
import pandas as pd

from src.models.stock import StockData, SeekingAlphaData
from src.utils.file_io import read_file

def _safe_float(value: Any) -> Optional[float]:
    """安全なfloat変換（'-'や空値を処理）"""
    if pd.isna(value) or value == '-' or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def _safe_str(value: Any) -> Optional[str]:
    """安全なstring変換"""
    if pd.isna(value) or value == '-' or value == '':
        return None
    return str(value).strip()

def parse_seekingalpha_portfolio(file_path: Union[str, Path]) -> List[StockData]:
    """
    SeekingAlphaのポートフォリオファイル（Excel）を解析する

    Args:
        file_path: ファイルパス

    Returns:
        StockDataオブジェクトのリスト
    """
    excel_data = pd.read_excel(file_path, sheet_name=None, engine='calamine')
    
    required_sheets = ['Summary', 'Ratings', 'Holdings', 'Dividends']
    missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data]
    if missing_sheets:
        raise ValueError(f"必要なシートが見つかりません: {missing_sheets}")

    summary_df = excel_data['Summary']
    if 'Symbol' not in summary_df.columns:
        raise ValueError("Summaryシートに'Symbol'列が見つかりません")
        
    stocks = []
    for symbol in summary_df['Symbol'].dropna().tolist():
        platform_data = {}
        
        # 各シートからデータを抽出
        summary_row = excel_data['Summary'][excel_data['Summary']['Symbol'] == symbol].iloc[0]
        ratings_row = excel_data['Ratings'][excel_data['Ratings']['Symbol'] == symbol].iloc[0]
        holdings_row = excel_data['Holdings'][excel_data['Holdings']['Symbol'] == symbol].iloc[0]
        dividends_row = excel_data['Dividends'][excel_data['Dividends']['Symbol'] == symbol].iloc[0]
        
        seeking_alpha_data = SeekingAlphaData(
            price=_safe_float(summary_row.get('Price')),
            valuation_grade=_safe_str(ratings_row.get('Valuation Grade')),
            profitability_grade=_safe_str(ratings_row.get('Profitability Grade')),
            shares=_safe_float(holdings_row.get('Shares')),
            cost=_safe_float(holdings_row.get('Cost')),
            value=_safe_float(holdings_row.get('Value')),
            dividend_safety=_safe_str(dividends_row.get('Safety')),
        )

        stock_data = StockData(
            symbol=symbol,
            exchange=None,  # Seeking Alphaのデータには取引所情報がない
            full_symbol=symbol,
            platform_data=seeking_alpha_data
        )
        stocks.append(stock_data)
        
    return stocks
