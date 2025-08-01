import pytest
from unittest.mock import MagicMock, patch

from src.google_sheets.client import GoogleSheetsClient
from src.google_sheets.auth import GoogleSheetsAuth
from src.models.stock import StockData
import gspread

@pytest.fixture
def mock_auth_manager():
    """モックされたGoogleSheetsAuthを返すフィクスチャ"""
    mock_auth = MagicMock(spec=GoogleSheetsAuth)
    mock_auth.get_gspread_client.return_value = MagicMock(spec=gspread.Client)
    return mock_auth

@pytest.fixture
def sheets_client(mock_auth_manager):
    """テスト用のGoogleSheetsClientインスタンスを返すフィクスチャ"""
    return GoogleSheetsClient(mock_auth_manager)

class TestGoogleSheetsClient:
    """GoogleSheetsClientクラスのテスト"""

    def test_create_spreadsheet(self, sheets_client):
        """スプレッドシート作成メソッドのテスト"""
        mock_spreadsheet = MagicMock(spec=gspread.Spreadsheet)
        sheets_client.client.create.return_value = mock_spreadsheet
        
        # setup_default_headersをモック化
        with patch.object(sheets_client, 'setup_default_headers') as mock_setup_headers:
            spreadsheet = sheets_client.create_spreadsheet("Test Sheet")
            
            sheets_client.client.create.assert_called_once_with("Test Sheet")
            mock_setup_headers.assert_called_once_with(mock_spreadsheet)
            assert spreadsheet == mock_spreadsheet

    def test_get_spreadsheet_by_id(self, sheets_client):
        """IDによるスプレッドシート取得メソッドのテスト"""
        sheets_client.client.open_by_key.return_value = "mock_spreadsheet"
        
        spreadsheet = sheets_client.get_spreadsheet_by_id("test_id")
        
        sheets_client.client.open_by_key.assert_called_once_with("test_id")
        assert spreadsheet == "mock_spreadsheet"

    def test_get_spreadsheet_not_found(self, sheets_client):
        """スプレッドシートが見つからない場合のテスト"""
        sheets_client.client.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound
        
        with pytest.raises(gspread.exceptions.SpreadsheetNotFound):
            sheets_client.get_spreadsheet_by_id("not_found_id")

    def test_setup_default_headers(self, sheets_client):
        """デフォルトヘッダー設定メソッドのテスト"""
        mock_spreadsheet = MagicMock(spec=gspread.Spreadsheet)
        mock_worksheet = MagicMock(spec=gspread.Worksheet)
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        
        sheets_client.setup_default_headers(mock_spreadsheet)
        
        mock_spreadsheet.get_worksheet.assert_called_once_with(0)
        mock_worksheet.update.assert_called_once()
        # updateに渡される引数のヘッダーリストを検証
        args, _ = mock_worksheet.update.call_args
        assert "Symbol" in args[1][0]
        assert "Date_Updated" in args[1][0]

    def test_update_sheet_with_data(self, sheets_client):
        """データによるシート更新メソッドのテスト"""
        mock_spreadsheet = MagicMock(spec=gspread.Spreadsheet)
        mock_worksheet = MagicMock(spec=gspread.Worksheet)
        sheets_client.client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # ヘッダー行のモック
        mock_worksheet.row_values.return_value = ["Symbol", "Exchange"]
        
        # テストデータ
        test_data = [
            StockData(symbol="AAPL", exchange="NASDAQ", full_symbol="NASDAQ:AAPL", source_platform="tradingview"),
            StockData(symbol="GOOG", exchange="NASDAQ", full_symbol="NASDAQ:GOOG", source_platform="tradingview")
        ]
        
        sheets_client.update_sheet_with_data("test_id", "TestSheet", test_data)
        
        mock_worksheet.update.assert_called_once()
        args, _ = mock_worksheet.update.call_args
        assert args[0] == 'A2' # 2行目から書き込み
        assert args[1] == [["AAPL", "NASDAQ"], ["GOOG", "NASDAQ"]] # 書き込むデータ