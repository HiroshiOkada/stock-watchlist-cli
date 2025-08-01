import pytest
from typing import Union
from datetime import datetime

from src.models.stock import StockData, TradingViewData, SeekingAlphaData, PlatformData


class TestStockDataModel:
    def test_stock_data_creation(self):
        """基本的なStockDataオブジェクトの作成テスト"""
        # TradingViewデータでの作成
        tv_data = TradingViewData(symbol="AAPL", section="###SECTION 1", exchange="NASDAQ")
        stock_tv = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            tradingview_section=tv_data.section,
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        
        assert stock_tv.symbol == "AAPL"
        assert stock_tv.exchange == "NASDAQ"
        assert stock_tv.full_symbol == "NASDAQ:AAPL"
        assert stock_tv.name == "Apple Inc."
        assert stock_tv.sector == "Technology"
        assert stock_tv.industry == "Consumer Electronics"
        assert stock_tv.tradingview_section == "###SECTION 1"
        assert stock_tv.source_platform == "tradingview"
        
        # SeekingAlphaデータでの作成
        sa_data = SeekingAlphaData(
            symbol="AAPL",
            company_name="Apple Inc.",
            price=150.0,
            valuation_grade="B+",
            profitability_grade="A",
            dividend_safety="Safe"
        )
        stock_sa = StockData(
            symbol="AAPL",
            full_symbol="AAPL", # full_symbolを追加
            name="Apple Inc.",
            current_price=sa_data.price,
            valuation_grade=sa_data.valuation_grade,
            profitability_grade=sa_data.profitability_grade,
            dividend_safety=sa_data.dividend_safety,
            source_platform="seekingalpha",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        
        assert stock_sa.symbol == "AAPL"
        assert stock_sa.exchange is None
        assert stock_sa.full_symbol == "AAPL"
        assert stock_sa.name == "Apple Inc."
        assert stock_sa.current_price == 150.0
        assert stock_sa.valuation_grade == "B+"
        assert stock_sa.source_platform == "seekingalpha"
    
    def test_platform_data_type_validation(self):
        """platform_dataの型バリデーションテスト"""
        # 正しい型（TradingViewData）
        # 正しい型（TradingViewData）
        tv_data = TradingViewData(symbol="AAPL", section="###SECTION 1", exchange="NASDAQ")
        stock = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            tradingview_section=tv_data.section,
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        assert stock.tradingview_section == "###SECTION 1"
        
        # 正しい型（SeekingAlphaData）
        sa_data = SeekingAlphaData(symbol="AAPL", price=150.0)
        stock = StockData(
            symbol="AAPL",
            full_symbol="AAPL", # full_symbolを追加
            current_price=sa_data.price,
            source_platform="seekingalpha",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        assert stock.current_price == 150.0
        
        # StockDataはPlatformDataを直接保持しないため、このテストは不要
        # with pytest.raises(ValueError):
        #     StockData(
        #         symbol="AAPL",
        #         exchange="NASDAQ",
        #         full_symbol="NASDAQ:AAPL",
        #         platform_data="invalid_data"  # 文字列は不正な型
        #     )
    
    def test_symbol_validation(self):
        """シンボル名のバリデーションテスト"""
        # 正しいシンボル
        tv_data = TradingViewData(symbol="AAPL")
        stock = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        assert stock.symbol == "AAPL"
        
        # 空のシンボル
        with pytest.raises(ValueError):
            StockData(
                symbol="",
                exchange="NASDAQ",
                full_symbol="NASDAQ:", # full_symbolを追加
                source_platform="tradingview",
                date_added=datetime.now(),
                date_updated=datetime.now()
            )
        
        # 特殊文字を含むシンボル（許可されるべき）
        stock = StockData(
            symbol="BRK.B",
            exchange="NYSE",
            full_symbol="NYSE:BRK.B", # full_symbolを追加
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        assert stock.symbol == "BRK.B"
    
    def test_data_normalization(self):
        """データ正規化機能のテスト"""
        # シンボルの大文字変換
        tv_data = TradingViewData(symbol="aapl", exchange="nasdaq")
        stock = StockData(
            symbol="aapl",  # 小文字で入力
            exchange="nasdaq",  # 小文字で入力
            full_symbol="nasdaq:aapl", # full_symbolを追加
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now()
        )
        
        # 正規化後は大文字になっているはず
        assert stock.symbol == "AAPL"
        assert stock.exchange == "NASDAQ"
        assert stock.full_symbol == "NASDAQ:AAPL"
    
    
    def test_stock_data_equality(self):
        """StockDataオブジェクトの比較テスト"""
        # 同じデータを持つ2つのオブジェクト
        stock1 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            name="Apple Inc.",
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now(),
            tradingview_section="###SECTION 1"
        )
        
        stock2 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            name="Apple Inc.",
            source_platform="tradingview",
            date_added=stock1.date_added, # 同じ日付を使用
            date_updated=stock1.date_updated, # 同じ日付を使用
            tradingview_section="###SECTION 1"
        )
        
        # 等価性チェック
        assert stock1 == stock2
        
        # 異なるデータを持つオブジェクト
        stock3 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL", # full_symbolを追加
            name="Apple Inc.",
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now(),
            tradingview_section="###SECTION 2"
        )
        
        # 等価性チェック（セクションが異なるため不一致）
        assert stock1 != stock3
    

