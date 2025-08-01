import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from src.models.stock import SeekingAlphaData
from src.parsers.base_parser import BaseParser

class SeekingAlphaParser(BaseParser):
    """Seeking Alpha Excelファイルパーサー（4シート対応）"""
    
    def __init__(self):
        self.required_sheets = ['Summary', 'Ratings', 'Holdings', 'Dividends']
    
    def parse(self, file_path: Union[str, Path]) -> List[SeekingAlphaData]:
        """4シート構成のExcelファイルを解析"""
        try:
            # 全シートを読み込み
            excel_data = pd.read_excel(file_path, sheet_name=None, engine='calamine')
            
            # 必要なシートの存在確認
            missing_sheets = [sheet for sheet in self.required_sheets
                            if sheet not in excel_data.keys()]
            if missing_sheets:
                raise ValueError(f"必要なシートが見つかりません: {missing_sheets}")
            
            # 各シートのデータを統合
            symbols = self._get_symbols_list(excel_data)
            seeking_alpha_data = []
            
            for symbol in symbols:
                data = self._parse_symbol_data(symbol, excel_data)
                seeking_alpha_data.append(data)
            
            return seeking_alpha_data
            
        except Exception as e:
            raise ValueError(f"Seeking Alphaファイルの解析に失敗: {e}")
    
    def _get_symbols_list(self, excel_data: Dict) -> List[str]:
        """全シートから銘柄シンボルのリストを取得"""
        summary_df = excel_data['Summary']
        if 'Symbol' in summary_df.columns:
            return summary_df['Symbol'].dropna().tolist()
        else:
            raise ValueError("Summaryシートに'Symbol'列が見つかりません")
    
    def _parse_symbol_data(self, symbol: str, excel_data: Dict) -> SeekingAlphaData:
        """特定銘柄のデータを4シートから統合"""
        data = SeekingAlphaData(symbol=symbol)
        
        # Summaryシートからデータ取得
        summary_row = excel_data['Summary'][excel_data['Summary']['Symbol'] == symbol]
        if not summary_row.empty:
            row = summary_row.iloc[0]
            data.price = self._safe_float(row.get('Price'))
            data.change = self._safe_float(row.get('Change'))
            data.change_percent = self._safe_float(row.get('Change %'))
            data.volume = self._safe_int(row.get('Volume'))
            data.avg_volume = self._safe_float(row.get('Avg. Vol'))
            data.day_low = self._safe_float(row.get('Day Low'))
            data.day_high = self._safe_float(row.get('Day High'))
            data.week52_low = self._safe_float(row.get('52W Low'))
            data.week52_high = self._safe_float(row.get('52W High'))
            data.quant_rating = self._safe_float(row.get('Quant Rating'))
            data.sa_analyst_rating = self._safe_float(row.get('SA Analyst Ratings'))
            data.wall_street_rating = self._safe_float(row.get('Wall Street Ratings'))
        
        # Ratingsシートからデータ取得
        ratings_df = excel_data['Ratings']
        ratings_row = ratings_df[ratings_df['Symbol'] == symbol]
        if not ratings_row.empty:
            row = ratings_row.iloc[0]
            data.valuation_grade = self._safe_str(row.get('Valuation Grade'))
            data.growth_grade = self._safe_str(row.get('Growth Grade'))
            data.profitability_grade = self._safe_str(row.get('Profitability Grade'))
            data.momentum_grade = self._safe_str(row.get('Momentum Grade'))
            data.eps_revision_grade = self._safe_str(row.get('EPS Revision Grade'))
        
        # Holdingsシートからデータ取得
        holdings_df = excel_data['Holdings']
        holdings_row = holdings_df[holdings_df['Symbol'] == symbol]
        if not holdings_row.empty:
            row = holdings_row.iloc[0]
            data.shares = self._safe_float(row.get('Shares'))
            data.cost = self._safe_float(row.get('Cost'))
            data.todays_gain = self._safe_float(row.get("Today's Gain"))
            data.todays_gain_percent = self._safe_float(row.get("Today's % Gain"))
            data.total_change = self._safe_float(row.get('Total Change'))
            data.total_change_percent = self._safe_float(row.get('Total % Change'))
            data.value = self._safe_float(row.get('Value'))
        
        # Dividendsシートからデータ取得
        dividends_df = excel_data['Dividends']
        dividends_row = dividends_df[dividends_df['Symbol'] == symbol]
        if not dividends_row.empty:
            row = dividends_row.iloc[0]
            data.dividend_safety = self._safe_str(row.get('Safety'))
            data.dividend_growth = self._safe_str(row.get('Growth'))
            data.dividend_yield_grade = self._safe_str(row.get('Yield'))
            data.dividend_consistency = self._safe_str(row.get('Consistency'))
            data.ex_dividend_date = self._safe_date(row.get('Ex-Div Date'))
            data.payout_date = self._safe_date(row.get('Payout Date'))
            data.frequency = self._safe_str(row.get('Frequency'))
            data.yield_ttm = self._safe_float(row.get('Yield TTM'))
            data.yield_forward = self._safe_float(row.get('Yield FWD'))
            data.dividend_rate_ttm = self._safe_float(row.get('Div Rate TTM'))
            data.dividend_rate_forward = self._safe_float(row.get('Div Rate FWD'))
            data.payout_ratio = self._safe_float(row.get('Payout Ratio'))
            data.dividend_growth_3y = self._safe_float(row.get('Div Growth 3Y'))
            data.dividend_growth_5y = self._safe_float(row.get('Div Growth 5Y'))
            data.beta_24m = self._safe_float(row.get('24M Beta'))
        
        return data
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """安全なfloat変換（'-'や空値を処理）"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """安全なint変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_str(self, value: Any) -> Optional[str]:
        """安全なstring変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        return str(value).strip()
    
    def _safe_date(self, value: Any) -> Optional[str]:
        """安全な日付変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            # M/D/YYYY形式をYYYY-MM-DD形式に変換
            if isinstance(value, str) and '/' in value:
                parts = value.split('/')
                if len(parts) == 3:
                    month, day, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return str(value)
        except:
            return None
    
    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None, engine='calamine')
            # 必要なシートが存在するかチェック
            return all(sheet in excel_data.keys() for sheet in self.required_sheets)
        except:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子"""
        return ['.xlsx', '.xls']
