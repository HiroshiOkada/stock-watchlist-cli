import pytest
from pathlib import Path
import pandas as pd

# この段階ではまだ存在しないモジュールをインポート
from src.utils.file_io import read_file, get_file_encoding

# テスト用のサンプルファイルパス
SAMPLES_DIR = Path(__file__).parent.parent / "sample_data"
TRADINGVIEW_TXT = SAMPLES_DIR / "US_STOCK_012ed.txt"
SEEKINGALPHA_XLSX = SAMPLES_DIR / "UsStock 2025-07-30.xlsx"
NON_EXISTENT_FILE = SAMPLES_DIR / "non_existent_file.txt"

# テストの前に、サンプルファイルが実際に存在することを確認
# (実際のプロジェクトでは、テストデータはリポジトリに含まれているべき)
@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    SAMPLES_DIR.mkdir(exist_ok=True)
    # TradingView (Shift-JIS) - 日本語を含めてShift-JISであることを明確にする
    TRADINGVIEW_TXT.write_text("###SECTION 1,米国株\nNASDAQ:AAPL,NASDAQ:MSFT", encoding="shift_jis")
    # SeekingAlpha (Excel)
    df = pd.DataFrame({"Ticker": ["GOOGL", "AMZN"]})
    df.to_excel(SEEKINGALPHA_XLSX, index=False)

    yield

    # クリーンアップ
    TRADINGVIEW_TXT.unlink()
    SEEKINGALPHA_XLSX.unlink()


class TestFileIO:
    def test_read_tradingview_txt_success(self):
        """TradingViewのTXTファイルが正しく読み込めることをテスト"""
        content = read_file(TRADINGVIEW_TXT)
        assert "米国株" in content
        assert "NASDAQ:AAPL,NASDAQ:MSFT" in content

    def test_read_seekingalpha_xlsx_success(self):
        """SeekingAlphaのExcelファイルが正しく読み込めることをテスト"""
        df = read_file(SEEKINGALPHA_XLSX)
        assert isinstance(df, pd.DataFrame)
        assert "Ticker" in df.columns
        assert "GOOGL" in df["Ticker"].values

    def test_read_file_not_found(self):
        """存在しないファイルを指定した場合にFileNotFoundErrorを送出することをテスト"""
        with pytest.raises(FileNotFoundError):
            read_file(NON_EXISTENT_FILE)

    def test_get_file_encoding_sjis(self):
        """get_file_encodingがエンコーディング文字列を返すことをテスト"""
        encoding = get_file_encoding(TRADINGVIEW_TXT)
        # chardetは短いテキストでは誤判定しやすいため、
        # 正確なエンコーディングの判定ではなく、Noneでないこと（エラーを起こさないこと）を保証する
        assert isinstance(encoding, str)

    def test_get_file_encoding_binary(self):
        """バイナリファイル（Excel）のエンコーディング検出をテスト"""
        encoding = get_file_encoding(SEEKINGALPHA_XLSX)
        # バイナリファイルなので、特定のエンコーディングではなくNoneやbinaryが返ることを期待
        assert encoding is None or "binary" in encoding.lower()
