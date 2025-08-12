import re
from typing import List, Dict, Tuple, Union, Optional
from pathlib import Path

from src.models.stock import StockData, TradingViewData
from src.utils.file_io import read_file
from src.parsers.base_parser import BaseParser
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class TradingViewParser(BaseParser):
    """TradingView テキストファイルパーサー（セクション対応）"""
    
    def __init__(self):
        self.supported_exchanges = ['NASDAQ', 'NYSE', 'AMEX', 'TSE', 'LSE', 'FRA']
        # '###<name>' も '###SECTION <name>' も許容
        self.section_pattern = r'^###(?:SECTION\s*)?(.+)$'
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
        
        # セクションごとに銘柄を一時的に保持する辞書
        # キーはセクション名 (Noneを含む), 値は銘柄リスト
        grouped_items: Dict[Optional[str], List[str]] = {None: []}
        current_section: Optional[str] = None
        
        for line in lines:
            items = [item.strip() for item in line.split(',') if item.strip()]
            
            for item in items:
                logger.debug(f"Processing item: '{item}', Current section before processing: '{current_section}'")
                section_match = re.match(self.section_pattern, item)
                if section_match:
                    current_section = section_match.group(1).strip()
                    logger.debug(f"Section found: {current_section}") # ログ出力追加
                    if current_section not in grouped_items:
                        grouped_items[current_section] = []
                    continue

                # 現在のセクションに銘柄を追加
                if current_section is None:
                    grouped_items[None].append(item)
                else:
                    grouped_items[current_section].append(item)

        # グループ化されたアイテムからTradingViewDataを作成
        for section_name, symbols_in_section in grouped_items.items():
            for item_symbol in symbols_in_section:
                symbol_match = re.match(self.symbol_pattern, item_symbol)
                if symbol_match:
                    exchange = symbol_match.group('exchange').upper()
                    symbol = symbol_match.group('symbol').upper()
                    
                    if exchange in self.supported_exchanges:
                        tradingview_data = TradingViewData(
                            symbol=symbol,
                            exchange=exchange,
                            section=section_name # グループ化されたセクションを割り当てる
                        )
                        tradingview_data_list.append(tradingview_data)
                        logger.debug(f"Parsed: {tradingview_data}") # ログ出力追加
                    else:
                        logger.warning(f"Unsupported exchange for item: {item_symbol}")
                else:
                    logger.warning(f"Invalid symbol format for item: {item_symbol}")
                            
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
