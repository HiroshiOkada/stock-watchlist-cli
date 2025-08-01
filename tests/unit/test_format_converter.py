import pytest
from datetime import datetime
from pydantic import BaseModel # BaseModelをインポート
from src.converters.format_converter import FormatConverter
from src.models.stock import StockData, TradingViewData, SeekingAlphaData

@pytest.fixture
def converter():
    """FormatConverterのインスタンスを提供するフィクスチャ"""
    return FormatConverter()

@pytest.fixture
def sample_tradingview_data():
    """TradingViewDataのサンプルリストを提供するフィクスチャ"""
    return [
        TradingViewData(symbol="AAPL", exchange="NASDAQ", section="SECTION 1"),
        TradingViewData(symbol="MSFT", exchange="NASDAQ", section="SECTION 1"),
        TradingViewData(symbol="GOOG", exchange="NASDAQ", section="SECTION 2"),
        TradingViewData(symbol="BRK.B", exchange="NYSE", section="SECTION 2"),
        TradingViewData(symbol="TSLA", exchange="NASDAQ", section=None),
    ]

@pytest.fixture
def sample_seekingalpha_data():
    """SeekingAlphaDataのサンプルリストを提供するフィクスチャ"""
    return [
        SeekingAlphaData(
            symbol="AAPL",
            company_name="Apple Inc.", # company_name を設定
            exchange="NASDAQ",
            price=211.27,
            quant_rating=3.32,
            shares=100.0,
            cost=150.0,
            dividend_safety="A"
        ),
        SeekingAlphaData(
            symbol="MSFT",
            company_name="Microsoft Corp.", # company_name を設定
            exchange="NASDAQ",
            price=450.0,
            quant_rating=4.0,
            shares=50.0,
            cost=400.0,
            dividend_safety="A+"
        ),
        SeekingAlphaData(
            symbol="GOOG",
            company_name="Alphabet Inc.", # company_name を設定
            exchange="NASDAQ",
            price=180.0,
            quant_rating=3.5,
            shares=None,
            cost=None,
            dividend_safety="B"
        ),
    ]

@pytest.fixture
def sample_stock_data_list(sample_tradingview_data, sample_seekingalpha_data):
    """StockDataのサンプルリストを提供するフィクスチャ"""
    stock_list = []
    for tv_data in sample_tradingview_data:
        stock_list.append(StockData(
            symbol=tv_data.symbol,
            exchange=tv_data.exchange,
            full_symbol=f"{tv_data.exchange}:{tv_data.symbol}" if tv_data.exchange else tv_data.symbol,
            tradingview_section=tv_data.section,
            source_platform="tradingview",
            date_added=datetime.now(),
            date_updated=datetime.now(),
            # SeekingAlpha関連のフィールドはNoneで初期化
            company_name=None,
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
        ))
    
    for sa_data in sample_seekingalpha_data:
        stock_list.append(StockData(
            symbol=sa_data.symbol,
            company_name=sa_data.company_name,
            exchange=sa_data.exchange,
            full_symbol=f"{sa_data.exchange}:{sa_data.symbol}" if sa_data.exchange else sa_data.symbol,
            current_price=sa_data.price,
            quant_rating=sa_data.quant_rating,
            shares=sa_data.shares,
            cost=sa_data.cost,
            dividend_safety=sa_data.dividend_safety,
            source_platform="seekingalpha",
            date_added=datetime.now(),
            date_updated=datetime.now(),
            # TradingView関連のフィールドはNoneで初期化
            tradingview_section=None,
            # SeekingAlphaの残りのフィールドも明示的に設定
            change=sa_data.change,
            change_percent=sa_data.change_percent,
            volume=sa_data.volume,
            avg_volume=sa_data.avg_volume,
            day_low=sa_data.day_low,
            day_high=sa_data.day_high,
            week52_low=sa_data.week52_low,
            week52_high=sa_data.week52_high,
            sa_analyst_rating=sa_data.sa_analyst_rating,
            wall_street_rating=sa_data.wall_street_rating,
            valuation_grade=sa_data.valuation_grade,
            growth_grade=sa_data.growth_grade,
            profitability_grade=sa_data.profitability_grade,
            momentum_grade=sa_data.momentum_grade,
            eps_revision_grade=sa_data.eps_revision_grade,
            todays_gain=sa_data.todays_gain,
            todays_gain_percent=sa_data.todays_gain_percent,
            total_change=sa_data.total_change,
            total_change_percent=sa_data.total_change_percent,
            value=sa_data.value,
            dividend_growth=sa_data.dividend_growth,
            dividend_yield_grade=sa_data.dividend_yield_grade,
            dividend_consistency=sa_data.dividend_consistency,
            ex_dividend_date=sa_data.ex_dividend_date,
            payout_date=sa_data.payout_date,
            frequency=sa_data.frequency,
            yield_ttm=sa_data.yield_ttm,
            yield_forward=sa_data.yield_forward,
            dividend_rate_ttm=sa_data.dividend_rate_ttm,
            dividend_rate_forward=sa_data.dividend_rate_forward,
            payout_ratio=sa_data.payout_ratio,
            dividend_growth_3y=sa_data.dividend_growth_3y,
            dividend_growth_5y=sa_data.dividend_growth_5y,
            beta_24m=sa_data.beta_24m,
            notes=None,
            status="active"
        ))
    return stock_list


class TestFormatConverter:
    """FormatConverterクラスの単体テスト"""

    def test_to_stock_data_from_tradingview(self, converter, sample_tradingview_data):
        """TradingViewDataからStockDataへの変換をテスト"""
        tv_data = sample_tradingview_data[0]
        stock_data = converter.to_stock_data(tv_data)
        assert isinstance(stock_data, StockData)
        assert stock_data.symbol == tv_data.symbol
        assert stock_data.exchange == tv_data.exchange
        assert stock_data.tradingview_section == tv_data.section
        assert stock_data.source_platform == "tradingview"

    def test_to_stock_data_from_seekingalpha(self, converter, sample_seekingalpha_data):
        """SeekingAlphaDataからStockDataへの変換をテスト"""
        sa_data = sample_seekingalpha_data[0]
        stock_data = converter.to_stock_data(sa_data)
        assert isinstance(stock_data, StockData)
        assert stock_data.symbol == sa_data.symbol
        assert getattr(stock_data, 'company_name', None) == sa_data.company_name
        assert stock_data.current_price == sa_data.price
        assert stock_data.quant_rating == sa_data.quant_rating
        assert stock_data.source_platform == "seekingalpha"
        assert stock_data.shares == sa_data.shares
        assert stock_data.cost == sa_data.cost
        assert stock_data.dividend_safety == sa_data.dividend_safety

    def test_to_platform_data_to_tradingview(self, converter, sample_stock_data_list):
        """StockDataからTradingViewDataへの変換をテスト"""
        # TradingView由来のStockDataを変換
        stock_data_tv = next(s for s in sample_stock_data_list if s.source_platform == "tradingview")
        tv_data = converter.to_platform_data(stock_data_tv, "tradingview")
        assert isinstance(tv_data, TradingViewData)
        assert tv_data.symbol == stock_data_tv.symbol
        assert tv_data.exchange == stock_data_tv.exchange
        assert tv_data.section == stock_data_tv.tradingview_section

        # SeekingAlpha由来のStockDataを変換
        stock_data_sa = next(s for s in sample_stock_data_list if s.source_platform == "seekingalpha")
        tv_data_from_sa = converter.to_platform_data(stock_data_sa, "tradingview")
        assert isinstance(tv_data_from_sa, TradingViewData)
        assert tv_data_from_sa.symbol == stock_data_sa.symbol
        assert tv_data_from_sa.exchange == stock_data_sa.exchange # SeekingAlphaDataにはexchangeがない場合があるが、StockDataで補完される
        assert tv_data_from_sa.section is None # SeekingAlphaDataにはsectionがない

    def test_to_platform_data_to_seekingalpha(self, converter, sample_stock_data_list):
        """StockDataからSeekingAlphaDataへの変換をテスト"""
        # SeekingAlpha由来のStockDataを変換
        stock_data_sa = next(s for s in sample_stock_data_list if s.source_platform == "seekingalpha")
        sa_data = converter.to_platform_data(stock_data_sa, "seekingalpha")
        assert isinstance(sa_data, SeekingAlphaData)
        assert sa_data.symbol == stock_data_sa.symbol
        assert getattr(sa_data, 'company_name', None) == getattr(stock_data_sa, 'company_name', None)
        assert sa_data.price == stock_data_sa.current_price
        assert sa_data.shares == stock_data_sa.shares
        assert sa_data.cost == stock_data_sa.cost
        assert sa_data.quant_rating == stock_data_sa.quant_rating

        # TradingView由来のStockDataを変換
        stock_data_tv = next(s for s in sample_stock_data_list if s.source_platform == "tradingview")
        sa_data_from_tv = converter.to_platform_data(stock_data_tv, "seekingalpha")
        assert isinstance(sa_data_from_tv, SeekingAlphaData)
        assert sa_data_from_tv.symbol == stock_data_tv.symbol
        assert sa_data_from_tv.company_name is None # TradingViewDataにはcompany_nameがない
        assert sa_data_from_tv.price is None # TradingViewDataにはpriceがない

    def test_convert_list(self, converter, sample_tradingview_data):
        """リスト変換のテスト"""
        converted_list = converter.convert_list(sample_tradingview_data, "seekingalpha")
        assert len(converted_list) == len(sample_tradingview_data)
        assert all(isinstance(item, SeekingAlphaData) for item in converted_list)
        assert converted_list[0].symbol == "AAPL"
        assert converted_list[1].symbol == "MSFT"

    def test_convert_to_csv(self, converter, sample_seekingalpha_data):
        """SeekingAlphaDataリストからCSVへの変換をテスト"""
        csv_output = converter.convert_to_csv(sample_seekingalpha_data)
        lines = csv_output.strip().split('\n')
        assert len(lines) == len(sample_seekingalpha_data) + 1 # ヘッダー行 + データ行
        # ヘッダーの各要素が存在するかどうかをチェック
        expected_headers = set(SeekingAlphaData.model_fields.keys())
        actual_headers = set(lines[0].split(','))
        assert expected_headers.issubset(actual_headers)
        
        # データ行の基本的な内容をチェック（順序に依存しない）
        assert "AAPL,Apple Inc.,NASDAQ,211.27" in lines[1]
        assert "MSFT,Microsoft Corp.,NASDAQ,450.0" in lines[2]
        assert "GOOG,Alphabet Inc.,NASDAQ,180.0" in lines[3]

    def test_convert_to_tradingview_txt(self, converter, sample_tradingview_data):
        """TradingViewDataリストからTradingViewテキストへの変換をテスト"""
        txt_output = converter.convert_to_tradingview_txt(sample_tradingview_data, preserve_sections=True)
        lines = txt_output.strip().split('\n')
        
        # セクションとシンボルの順序を考慮したテスト
        expected_lines = [
            "###SECTION 1",
            "NASDAQ:AAPL,NASDAQ:MSFT",
            "###SECTION 2",
            "NASDAQ:GOOG,NYSE:BRK.B",
            "NASDAQ:TSLA" # セクションなしは最後
        ]
        assert lines == expected_lines

    def test_convert_to_tradingview_txt_no_sections(self, converter, sample_tradingview_data):
        """セクションなしでTradingViewテキストへの変換をテスト"""
        txt_output = converter.convert_to_tradingview_txt(sample_tradingview_data, preserve_sections=False)
        lines = txt_output.strip().split('\n')
        
        expected_line = "NASDAQ:AAPL,NASDAQ:MSFT,NASDAQ:GOOG,NYSE:BRK.B,NASDAQ:TSLA"
        assert len(lines) == 1
        assert lines[0] == expected_line

    def test_unsupported_data_type(self, converter):
        """サポートされていないデータ型での変換をテスト"""
        class UnsupportedData(BaseModel):
            pass
        
        with pytest.raises(ValueError, match="サポートされていないデータ型です"):
            converter.to_stock_data(UnsupportedData())

    def test_unsupported_target_platform(self, converter, sample_stock_data_list):
        """サポートされていないターゲットプラットフォームでの変換をテスト"""
        stock_data = sample_stock_data_list[0]
        with pytest.raises(ValueError, match="サポートされていないターゲットプラットフォームです"):
            converter.to_platform_data(stock_data, "unsupported_platform")