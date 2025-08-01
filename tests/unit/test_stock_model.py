import pytest
from typing import Union

from src.models.stock import StockData, TradingViewData, SeekingAlphaData, PlatformData


class TestStockDataModel:
    def test_stock_data_creation(self):
        """基本的なStockDataオブジェクトの作成テスト"""
        # TradingViewデータでの作成
        tv_data = TradingViewData(section="###SECTION 1")
        stock_tv = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            platform_data=tv_data
        )
        
        assert stock_tv.symbol == "AAPL"
        assert stock_tv.exchange == "NASDAQ"
        assert stock_tv.full_symbol == "NASDAQ:AAPL"
        assert stock_tv.name == "Apple Inc."
        assert stock_tv.sector == "Technology"
        assert stock_tv.industry == "Consumer Electronics"
        assert isinstance(stock_tv.platform_data, TradingViewData)
        assert stock_tv.platform_data.section == "###SECTION 1"
        
        # SeekingAlphaデータでの作成
        sa_data = SeekingAlphaData(
            price=150.0,
            valuation_grade="B+",
            profitability_grade="A",
            dividend_safety="Safe"
        )
        stock_sa = StockData(
            symbol="AAPL",
            exchange=None,
            full_symbol="AAPL",
            name="Apple Inc.",
            platform_data=sa_data
        )
        
        assert stock_sa.symbol == "AAPL"
        assert stock_sa.exchange is None
        assert stock_sa.full_symbol == "AAPL"
        assert stock_sa.name == "Apple Inc."
        assert isinstance(stock_sa.platform_data, SeekingAlphaData)
        assert stock_sa.platform_data.price == 150.0
        assert stock_sa.platform_data.valuation_grade == "B+"
    
    def test_platform_data_type_validation(self):
        """platform_dataの型バリデーションテスト"""
        # 正しい型（TradingViewData）
        tv_data = TradingViewData(section="###SECTION 1")
        stock = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            platform_data=tv_data
        )
        assert isinstance(stock.platform_data, TradingViewData)
        
        # 正しい型（SeekingAlphaData）
        sa_data = SeekingAlphaData(price=150.0)
        stock = StockData(
            symbol="AAPL",
            exchange=None,
            full_symbol="AAPL",
            platform_data=sa_data
        )
        assert isinstance(stock.platform_data, SeekingAlphaData)
        
        # 不正な型（文字列）
        with pytest.raises(ValueError):
            StockData(
                symbol="AAPL",
                exchange="NASDAQ",
                full_symbol="NASDAQ:AAPL",
                platform_data="invalid_data"  # 文字列は不正な型
            )
    
    def test_symbol_validation(self):
        """シンボル名のバリデーションテスト"""
        # 正しいシンボル
        tv_data = TradingViewData()
        stock = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            platform_data=tv_data
        )
        assert stock.symbol == "AAPL"
        
        # 空のシンボル
        with pytest.raises(ValueError):
            StockData(
                symbol="",
                exchange="NASDAQ",
                full_symbol="NASDAQ:",
                platform_data=tv_data
            )
        
        # 特殊文字を含むシンボル（許可されるべき）
        stock = StockData(
            symbol="BRK.B",
            exchange="NYSE",
            full_symbol="NYSE:BRK.B",
            platform_data=tv_data
        )
        assert stock.symbol == "BRK.B"
    
    def test_data_normalization(self):
        """データ正規化機能のテスト"""
        # シンボルの大文字変換
        tv_data = TradingViewData()
        stock = StockData(
            symbol="aapl",  # 小文字で入力
            exchange="nasdaq",  # 小文字で入力
            full_symbol="nasdaq:aapl",  # 小文字で入力
            platform_data=tv_data
        )
        
        # 正規化後は大文字になっているはず
        assert stock.symbol == "AAPL"
        assert stock.exchange == "NASDAQ"
        assert stock.full_symbol == "NASDAQ:AAPL"
    
    def test_platform_data_conversion(self):
        """プラットフォーム間のデータ変換テスト"""
        # TradingView → SeekingAlpha
        tv_data = TradingViewData(section="###SECTION 1")
        stock_tv = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            name="Apple Inc.",
            platform_data=tv_data
        )
        
        # TradingViewからSeekingAlphaへの変換
        sa_data = stock_tv.convert_platform_data(SeekingAlphaData)
        assert isinstance(sa_data, SeekingAlphaData)
        
        # SeekingAlpha → TradingView
        sa_data = SeekingAlphaData(
            price=150.0,
            valuation_grade="B+",
            profitability_grade="A"
        )
        stock_sa = StockData(
            symbol="AAPL",
            exchange=None,
            full_symbol="AAPL",
            platform_data=sa_data
        )
        
        # SeekingAlphaからTradingViewへの変換
        tv_data = stock_sa.convert_platform_data(TradingViewData)
        assert isinstance(tv_data, TradingViewData)
    
    def test_stock_data_equality(self):
        """StockDataオブジェクトの比較テスト"""
        # 同じデータを持つ2つのオブジェクト
        tv_data1 = TradingViewData(section="###SECTION 1")
        stock1 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            platform_data=tv_data1
        )
        
        tv_data2 = TradingViewData(section="###SECTION 1")
        stock2 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            platform_data=tv_data2
        )
        
        # 等価性チェック
        assert stock1 == stock2
        
        # 異なるデータを持つオブジェクト
        tv_data3 = TradingViewData(section="###SECTION 2")
        stock3 = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            platform_data=tv_data3
        )
        
        # 等価性チェック（セクションが異なるため不一致）
        assert stock1 != stock3
    
    def test_stock_data_merge(self):
        """StockDataオブジェクトのマージテスト"""
        # TradingViewデータ
        tv_data = TradingViewData(section="###SECTION 1")
        stock_tv = StockData(
            symbol="AAPL",
            exchange="NASDAQ",
            full_symbol="NASDAQ:AAPL",
            name=None,  # 名前なし
            platform_data=tv_data
        )
        
        # SeekingAlphaデータ
        sa_data = SeekingAlphaData(
            price=150.0,
            valuation_grade="B+"
        )
        stock_sa = StockData(
            symbol="AAPL",
            exchange=None,
            full_symbol="AAPL",
            name="Apple Inc.",  # 名前あり
            platform_data=sa_data
        )
        
        # マージ（TradingViewをベースにSeekingAlphaのデータを追加）
        merged_stock = stock_tv.merge(stock_sa)
        
        # マージ結果の検証
        assert merged_stock.symbol == "AAPL"
        assert merged_stock.exchange == "NASDAQ"  # TradingViewの値が優先
        assert merged_stock.full_symbol == "NASDAQ:AAPL"  # TradingViewの値が優先
        assert merged_stock.name == "Apple Inc."  # SeekingAlphaの値で補完
        
        # プラットフォームデータは元のまま
        assert isinstance(merged_stock.platform_data, TradingViewData)
        assert merged_stock.platform_data.section == "###SECTION 1"
        
        # SeekingAlphaデータへのアクセス方法
        sa_data = merged_stock.get_platform_data(SeekingAlphaData)
        assert sa_data is not None
        assert sa_data.price == 150.0
        assert sa_data.valuation_grade == "B+"


class TestPlatformDataInterface:
    def test_platform_data_interface(self):
        """PlatformDataインターフェースの実装テスト"""
        # TradingViewDataがPlatformDataを実装していることを確認
        tv_data = TradingViewData()
        assert isinstance(tv_data, PlatformData)
        
        # SeekingAlphaDataがPlatformDataを実装していることを確認
        sa_data = SeekingAlphaData()
        assert isinstance(sa_data, PlatformData)
        
        # 共通インターフェースメソッドのテスト
        assert hasattr(tv_data, "to_dict")
        assert hasattr(sa_data, "to_dict")
        
        # to_dictメソッドの動作確認
        tv_dict = tv_data.to_dict()
        assert isinstance(tv_dict, dict)
        assert "section" in tv_dict
        
        sa_dict = sa_data.to_dict()
        assert isinstance(sa_dict, dict)
        assert "price" in sa_dict


class TestDataConversion:
    def test_trading_view_to_seeking_alpha(self):
        """TradingViewからSeekingAlphaへの変換テスト"""
        tv_data = TradingViewData(section="###SECTION 1")
        sa_data = tv_data.to_seeking_alpha()
        
        assert isinstance(sa_data, SeekingAlphaData)
        # セクション情報は変換できないのでNone
        assert sa_data.price is None
        assert sa_data.valuation_grade is None
    
    def test_seeking_alpha_to_trading_view(self):
        """SeekingAlphaからTradingViewへの変換テスト"""
        sa_data = SeekingAlphaData(
            price=150.0,
            valuation_grade="B+",
            profitability_grade="A"
        )
        tv_data = sa_data.to_trading_view()
        
        assert isinstance(tv_data, TradingViewData)
        # SeekingAlphaにはセクション情報がないのでNone
        assert tv_data.section is None