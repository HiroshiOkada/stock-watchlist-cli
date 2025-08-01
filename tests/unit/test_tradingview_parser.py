import pytest
from pathlib import Path

# この段階ではまだ存在しないモジュール
from src.parsers.tradingview import TradingViewParser
from src.models.stock import StockData, TradingViewData

# テスト用のサンプルファイルパス
SAMPLE_FILE = Path(__file__).parent.parent.parent / "sample" / "US_STOCK_012ed.txt"

class TestTradingViewParser:
    @pytest.fixture(scope="class")
    def parsed_data(self):
        """テスト用のパース済みデータを返すフィクスチャ"""
        if not SAMPLE_FILE.exists():
            pytest.fail(f"サンプルファイルが見つかりません: {SAMPLE_FILE}")
        return TradingViewParser().parse(SAMPLE_FILE)

    def test_total_stocks_count(self, parsed_data):
        """合計36銘柄が正しく抽出されることをテスト"""
        assert len(parsed_data) == 36

    def test_section_information_retained(self, parsed_data):
        """セクション情報が正しく保持されることをテスト"""
        section_1_stocks = [s for s in parsed_data if s.section == "SECTION 1"]
        section_2_stocks = [s for s in parsed_data if s.section == "SECTION 2"]
        # サンプルファイルの構造上、SECTION 1 に属する銘柄はない
        assert len(section_1_stocks) == 0
        assert len(section_2_stocks) > 0
        # セクションを持つ銘柄と持たない銘柄の合計が36になることを確認
        section_none_stocks = [s for s in parsed_data if s.section is None]
        assert len(section_none_stocks) + len(section_2_stocks) == 36

    def test_exchange_statistics(self, parsed_data):
        """取引所別の統計情報が正しいことをテスト"""
        stats = {"NASDAQ": 0, "NYSE": 0, "AMEX": 0}
        for stock in parsed_data:
            if stock.exchange in stats:
                stats[stock.exchange] += 1
        
        assert stats["NASDAQ"] == 22
        assert stats["NYSE"] == 13
        assert stats["AMEX"] == 1

    def test_special_symbol_handling(self, parsed_data):
        """BRK.Bのような特殊シンボルが正しく処理されることをテスト"""
        brk_b = next((s for s in parsed_data if s.symbol == "BRK.B"), None)
        assert brk_b is not None
        assert brk_b.exchange == "NYSE"
        # TradingViewDataにはfull_symbol属性がないため、直接比較
        assert f"{brk_b.exchange}:{brk_b.symbol}" == "NYSE:BRK.B"

    def test_data_model_structure(self, parsed_data):
        """データモデルの構造が正しいことをテスト"""
        sample_stock = parsed_data[0]
        assert isinstance(sample_stock, TradingViewData) # TradingViewDataを直接返すため
        assert sample_stock.symbol is not None
        assert sample_stock.exchange is not None
