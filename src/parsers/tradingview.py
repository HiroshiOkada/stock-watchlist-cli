import re
from typing import List, Dict, Tuple, Union
from pathlib import Path

from src.models.stock import StockData, TradingViewData
from src.utils.file_io import read_file
from src.parsers.base_parser import BaseParser

class TradingViewParser(BaseParser):
    """TradingView テキストファイルパーサー（セクション対応）"""
    
    def __init__(self):
        self.supported_exchanges = ['NASDAQ', 'NYSE', 'AMEX', 'TSE', 'LSE', 'FRA']
        self.section_pattern = r'^###SECTION\s*(.+)$'
        self.symbol_pattern = r'^(?P<exchange>[A-Z]+):(?P<symbol>[A-Z0-9\.\-]+)$'
    
    def parse(self, file_path: Union[str, Path]) -> List[TradingViewData]:
        """
        TradingViewのウォッチリストファイルを解析する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            TradingViewDataオブジェクトのリスト
        """
        content = read_file(file_path)
        lines = content.strip().split('\n')
        
        tradingview_data_list: List[TradingViewData] = []
        current_section: Optional[str] = None
        
        # 全ての行を結合し、カンマで分割
        all_items = []
        for line in lines:
            all_items.extend([item.strip() for item in line.split(',')])

        for item in all_items:
            if not item:
                continue

            section_match = re.match(self.section_pattern, item)
            if section_match:
                current_section = section_match.group(1).strip()
                continue

            symbol_match = re.match(self.symbol_pattern, item)
            if symbol_match:
                exchange = symbol_match.group('exchange').upper()
                symbol = symbol_match.group('symbol').upper()
                
                if exchange in self.supported_exchanges:
                    tradingview_data = TradingViewData(
                        symbol=symbol,
                        exchange=exchange,
                        section=current_section
                    )
                    tradingview_data_list.append(tradingview_data)
                else:
                    # サポートされていない取引所はスキップまたはログ出力
                    pass # ロギングは呼び出し元で行う
            else:
                # シンボル形式が不正な場合はスキップまたはログ出力
                pass # ロギングは呼び出し元で行う
                    
        return tradingview_data_list

    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            content = read_file(file_path)
            # 少なくとも1つのシンボルまたはセクションマーカーがあればTrue
            return bool(re.search(self.symbol_pattern, content) or re.search(self.section_pattern, content))
        except Exception:
            return False

    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子"""
        return ['.txt']
