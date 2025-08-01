import pytest
from pathlib import Path
import pandas as pd

# この段階ではまだ存在しないモジュール
from src.parsers.seekingalpha import SeekingAlphaParser
from src.models.stock import StockData, SeekingAlphaData

# テスト用のサンプルファイルパス
SAMPLE_FILE = Path(__file__).parent.parent.parent / "sample" / "UsStock 2025-07-30.xlsx"

class TestSeekingAlphaParser:
    @pytest.fixture(scope="class")
    def parsed_data(self):
        """テスト用のパース済みデータを返すフィクスチャ"""
        if not SAMPLE_FILE.exists():
            pytest.fail(f"サンプルファイルが見つかりません: {SAMPLE_FILE}")
        return SeekingAlphaParser().parse(SAMPLE_FILE)

    def test_all_sheets_parsed(self, parsed_data):
        """4つのシートすべてが解析され、データが統合されていることをテスト"""
        # サンプルとしてAAPLのデータを確認
        aapl_data = next((s for s in parsed_data if s.symbol == "AAPL"), None)
        assert aapl_data is not None
        
        # 各シートに存在するはずのデータ項目をチェック
        # Summary
        assert aapl_data.price is not None
        # Ratings
        assert aapl_data.valuation_grade is not None
        # Holdings (サンプルでは空のはず)
        assert aapl_data.shares is None
        # Dividends
        assert aapl_data.dividend_safety is not None

    def test_empty_values_handled(self, parsed_data):
        """'-'や空値がNoneに変換されることをテスト"""
        # Holdingsシートのデータはほぼすべて'-'なので、Noneになっているはず
        aapl_data = next((s for s in parsed_data if s.symbol == "AAPL"), None)
        assert aapl_data.cost is None
        assert aapl_data.value is None

    def test_rating_values_retained(self, parsed_data):
        """レーティング（A+, Fなど）が正しく文字列として保持されることをテスト"""
        aapl_data = next((s for s in parsed_data if s.symbol == "AAPL"), None)
        assert aapl_data.valuation_grade == "F"
        assert aapl_data.profitability_grade == "A+"

    def test_data_model_structure(self, parsed_data):
        """データモデルの構造が正しいことをテスト"""
        sample_stock = parsed_data[0]
        assert isinstance(sample_stock, SeekingAlphaData) # SeekingAlphaDataを直接返すため
        assert sample_stock.symbol is not None
        # Seeking Alphaのデータには取引所情報がないためNone
        assert sample_stock.exchange is None # SeekingAlphaDataにはexchangeフィールドがない
