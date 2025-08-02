import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.main import cli

@pytest.fixture
def runner():
    """Click CliRunnerを返すフィクスチャ"""
    return CliRunner()

@patch('src.converters.format_converter.FormatConverter')
@patch('src.parsers.tradingview.TradingViewParser')
@patch('src.google_sheets.client.GoogleSheetsClient')
@patch('src.main.GoogleSheetsAuth') # mainの中で直接使われるため、これで正しい
def test_sheets_import_success(mock_auth, mock_client, mock_parser, mock_converter, runner, tmp_path):
    """sheets importコマンドの成功をテスト"""
    # モックの設定
    mock_parser.return_value.parse.return_value = [MagicMock()]
    mock_converter.return_value.to_stock_data.return_value = MagicMock()
    
    # ダミーの入力ファイルを作成
    input_file = tmp_path / "input.txt"
    input_file.write_text("DUMMY")

    result = runner.invoke(cli, [
        'sheets', 'import',
        '--file', str(input_file),
        '--format', 'tradingview',
        '--spreadsheet-id', 'dummy_id'
    ])

    assert result.exit_code == 0
    assert "正常にインポートが完了しました" in result.output
    mock_parser.return_value.parse.assert_called_once_with(str(input_file))
    mock_client.return_value.update_sheet_with_data.assert_called_once()

@patch('src.converters.format_converter.FormatConverter')
@patch('src.google_sheets.client.GoogleSheetsClient')
@patch('src.main.GoogleSheetsAuth') # mainの中で直接使われるため、これで正しい
def test_sheets_export_success(mock_auth, mock_client, mock_converter, runner, tmp_path):
    """sheets exportコマンドの成功をテスト"""
    # モックの設定
    mock_client.return_value.get_all_records.return_value = [{'Symbol': 'AAPL', 'Exchange': 'NASDAQ'}]
    mock_converter.return_value.from_records.return_value = [MagicMock()]
    mock_converter.return_value.convert_to_tradingview_txt.return_value = "NASDAQ:AAPL"

    output_file = tmp_path / "output.txt"

    result = runner.invoke(cli, [
        'sheets', 'export',
        '--spreadsheet-id', 'dummy_id',
        '--format', 'tradingview',
        '--output', str(output_file)
    ])

    assert result.exit_code == 0
    assert "正常にエクスポートが完了しました" in result.output
    assert output_file.read_text() == "NASDAQ:AAPL"
    mock_client.return_value.get_all_records.assert_called_once()
    mock_converter.return_value.from_records.assert_called_once_with([{'Symbol': 'AAPL', 'Exchange': 'NASDAQ'}])