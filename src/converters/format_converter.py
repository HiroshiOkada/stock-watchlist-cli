from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.stock import StockData, TradingViewData, SeekingAlphaData, PlatformData
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class FormatConverter:
    """
    異なるプラットフォームの株式データを相互に変換するクラス。
    TradingViewDataとSeekingAlphaDataをStockDataに統合し、
    またStockDataから各プラットフォーム固有のデータ形式に変換する機能を提供する。
    """

    def __init__(self):
        pass

    def to_stock_data(self, platform_data: PlatformData) -> StockData:
        """
        TradingViewDataまたはSeekingAlphaDataをStockDataに変換する。
        """
        if isinstance(platform_data, TradingViewData):
            return self._from_tradingview_to_stock_data(platform_data)
        elif isinstance(platform_data, SeekingAlphaData):
            return self._from_seekingalpha_to_stock_data(platform_data)
        else:
            raise ValueError(f"サポートされていないデータ型です: {type(platform_data)}")

    def _from_tradingview_to_stock_data(self, tv_data: TradingViewData) -> StockData:
        """
        TradingViewDataをStockDataに変換する内部メソッド。
        """
        logger.info(f"TradingViewDataをStockDataに変換中: {tv_data.symbol}")
        full_symbol = f"{tv_data.exchange}:{tv_data.symbol}" if tv_data.exchange else tv_data.symbol
        return StockData(
            symbol=tv_data.symbol,
            exchange=tv_data.exchange,
            full_symbol=full_symbol,
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now(),
            tradingview_section=tv_data.section,
            # SeekingAlpha関連のフィールドはNoneで初期化
            name=None,
            current_price=None,
            change=None,
            change_percent=None,
            volume=None,
            avg_volume=None,
            day_low=None,
            day_high=None,
            week52_low=None,
            week52_high=None,
            quant_rating=None,
            sa_analyst_rating=None,
            wall_street_rating=None,
            valuation_grade=None,
            growth_grade=None,
            profitability_grade=None,
            momentum_grade=None,
            eps_revision_grade=None,
            shares=None,
            cost=None,
            todays_gain=None,
            todays_gain_percent=None,
            total_change=None,
            total_change_percent=None,
            value=None,
            dividend_safety=None,
            dividend_growth=None,
            dividend_yield_grade=None,
            dividend_consistency=None,
            ex_dividend_date=None,
            payout_date=None,
            frequency=None,
            yield_ttm=None,
            yield_forward=None,
            dividend_rate_ttm=None,
            dividend_rate_forward=None,
            payout_ratio=None,
            dividend_growth_3y=None,
            dividend_growth_5y=None,
            beta_24m=None,
            notes=None,
            status="active"
        )

    def _from_seekingalpha_to_stock_data(self, sa_data: SeekingAlphaData) -> StockData:
        """
        SeekingAlphaDataをStockDataに変換する内部メソッド。
        """
        logger.info(f"SeekingAlphaDataをStockDataに変換中: {sa_data.symbol}")
        full_symbol = f"{sa_data.exchange}:{sa_data.symbol}" if sa_data.exchange else sa_data.symbol
        # SeekingAlphaDataの全てのフィールドを辞書として取得し、StockDataに渡す
        # StockDataに存在しないフィールドは無視される
        stock_data_dict = sa_data.model_dump(exclude_none=False)
        # company_nameをnameにマッピング
        if 'company_name' in stock_data_dict:
            stock_data_dict['name'] = stock_data_dict.pop('company_name')
        # priceをcurrent_priceにマッピング
        if 'price' in stock_data_dict:
            stock_data_dict['current_price'] = stock_data_dict.pop('price')

        stock_data_dict.update({
            "full_symbol": full_symbol,
            "source_platform": "seekingalpha",
            "date_added": datetime.now(),
            "date_updated": datetime.now(),
            "notes": None,
            "status": "active",
            "tradingview_section": None
        })
        return StockData(**stock_data_dict)

    def to_platform_data(self, stock_data: StockData, target_platform: str) -> PlatformData:
        """
        StockDataを特定のプラットフォームデータ形式に変換する。
        """
        if target_platform.lower() == "tradingview":
            return self._from_stock_data_to_tradingview(stock_data)
        elif target_platform.lower() == "seekingalpha":
            return self._from_stock_data_to_seekingalpha(stock_data)
        else:
            raise ValueError(f"サポートされていないターゲットプラットフォームです: {target_platform}")

    def _from_stock_data_to_tradingview(self, stock_data: StockData) -> TradingViewData:
        """
        StockDataをTradingViewDataに変換する内部メソッド。
        """
        logger.info(f"StockDataをTradingViewDataに変換中: {stock_data.symbol}")
        return TradingViewData(
            symbol=stock_data.symbol,
            exchange=stock_data.exchange,
            section=stock_data.tradingview_section
        )

    def _from_stock_data_to_seekingalpha(self, stock_data: StockData) -> SeekingAlphaData:
        """
        StockDataをSeekingAlphaDataに変換する内部メソッド。
        """
        logger.info(f"StockDataをSeekingAlphaDataに変換中: {stock_data.symbol}")
        logger.info(f"StockDataをSeekingAlphaDataに変換中: {stock_data.symbol}")
        sa_data_dict = stock_data.model_dump(exclude_none=True)
        # nameをcompany_nameにマッピング
        if 'name' in sa_data_dict:
            sa_data_dict['company_name'] = sa_data_dict.pop('name')
        # current_priceをpriceにマッピング
        if 'current_price' in sa_data_dict:
            sa_data_dict['price'] = sa_data_dict.pop('current_price')
        
        # StockDataのフィールドでSeekingAlphaDataに存在しないものを削除
        # SeekingAlphaDataのフィールドリストを取得
        seekingalpha_fields = set(SeekingAlphaData.model_fields.keys())
        filtered_sa_data_dict = {k: v for k, v in sa_data_dict.items() if k in seekingalpha_fields}

        return SeekingAlphaData(**filtered_sa_data_dict)

    def convert_list(self, data_list: List[PlatformData], target_platform: str) -> List[PlatformData]:
        """
        PlatformDataのリストを別のPlatformDataのリストに変換する。
        """
        converted_list = []
        for item in data_list:
            stock_data = self.to_stock_data(item)
            converted_list.append(self.to_platform_data(stock_data, target_platform))
        return converted_list

    def convert_to_csv(self, data_list: List[SeekingAlphaData]) -> str:
        """
        SeekingAlphaDataのリストをCSV形式の文字列に変換する。
        """
        if not data_list:
            return ""

        # ヘッダー行を生成
        # SeekingAlphaDataのフィールドを全て含める
        headers = list(SeekingAlphaData.model_fields.keys())
        csv_lines = [",".join(headers)]

        # データ行を生成
        for item in data_list:
            values = []
            for field in headers:
                value = getattr(item, field)
                if value is None:
                    values.append("")
                elif isinstance(value, (float, int)):
                    values.append(str(value))
                elif isinstance(value, datetime):
                    values.append(value.strftime("%Y-%m-%d"))
                else:
                    values.append(str(value))
            csv_lines.append(",".join(values))
        
        return "\n".join(csv_lines)

    def convert_to_tradingview_txt(self, data_list: List[TradingViewData], preserve_sections: bool = True) -> str:
        """
        TradingViewDataのリストをTradingViewテキスト形式の文字列に変換する。
        """
        if not data_list:
            return ""

        output_lines = []
        current_section = None
        
        # セクションごとに銘柄をグループ化
        grouped_by_section = {}
        for item in data_list:
            section_key = item.section if preserve_sections and item.section else "No Section"
            if section_key not in grouped_by_section:
                grouped_by_section[section_key] = []
            grouped_by_section[section_key].append(item)
        
        # セクション名でソート（"No Section"は最後）
        sorted_sections = sorted(grouped_by_section.keys(), key=lambda x: (x == "No Section", x))

        for section_name in sorted_sections:
            if preserve_sections and section_name != "No Section":
                output_lines.append(f"###{section_name}")
            
            symbols = []
            for item in grouped_by_section[section_name]:
                symbol_with_exchange = f"{item.exchange}:{item.symbol}" if item.exchange else item.symbol
                symbols.append(symbol_with_exchange)
            
            output_lines.append(",".join(symbols))
        
        return "\n".join(output_lines)