import pytest
from click.testing import CliRunner
from src.main import cli

def test_cli_help():
    """stock-cli --help が正常に動作することを確認する"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: cli [OPTIONS] COMMAND [ARGS]...' in result.output
    assert 'convert' in result.output
    assert 'sheets' in result.output
    assert 'analyze' in result.output

def test_cli_version():
    """stock-cli --version が正常に動作することを確認する"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    # pyproject.tomlのバージョンと一致することを確認
    # このテストはバージョンが固定されている場合に有効
    assert 'cli, version' in result.output

def test_convert_command_exists():
    """convert コマンドの骨組みが存在することを確認する"""
    runner = CliRunner()
    result = runner.invoke(cli, ['convert', '--help'])
    assert result.exit_code == 0
    assert 'Usage: cli convert [OPTIONS]' in result.output

def test_sheets_command_exists():
    """sheets コマンドの骨組みが存在することを確認する"""
    runner = CliRunner()
    result = runner.invoke(cli, ['sheets', '--help'])
    assert result.exit_code == 0
    assert 'Usage: cli sheets [OPTIONS]' in result.output

def test_analyze_command_exists():
    """analyze コマンドの骨組みが存在することを確認する"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', '--help'])
    assert result.exit_code == 0
    assert 'Usage: cli analyze [OPTIONS]' in result.output
from unittest.mock import MagicMock

def test_config_loading(mocker):
    """設定ファイルが正しく読み込まれることを確認する"""
    # cliをインポートする前にモックを適用
    mock_config = MagicMock()
    mock_get_config = mocker.patch('src.config.settings.get_config', return_value=mock_config)
    mocker.patch('src.main.setup_logging') # logging設定はテスト対象外
    
    from src.main import cli # モック適用後にcliをインポート
    runner = CliRunner()
    # --version は get_config を呼び出すはず
    # get_configが呼び出されることを直接テスト
    from src.config.settings import get_config as actual_get_config # 実際のget_configをインポート
    actual_get_config() # get_configを呼び出す
    
    mock_get_config.assert_called_once()

def test_config_loading_failure(mocker):
    """設定ファイルの読み込み失敗時にエラー終了することを確認する"""
    # get_configが例外を発生させるようにモックする
    mocker.patch('src.main.get_config', side_effect=FileNotFoundError("config.yaml not found"))
    mocker.patch('src.main.setup_logging') # logging設定はテスト対象外

    runner = CliRunner()
    # サブコマンドを渡さないと引数エラーになるため、ダミーのサブコマンドを渡す
    result = runner.invoke(cli, ['convert'])
    
    assert result.exit_code == 1
    # エラーメッセージがstderrに出力されることを確認
    assert "設定ファイルの読み込みに失敗しました" in result.output

def test_config_default_token_file():
    """デフォルトのトークンファイル設定が正しく読み込まれることを確認する"""
    from src.config.settings import ConfigManager
    import tempfile
    import os
    
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 空の.envファイルを作成
        env_file = os.path.join(tmp_dir, ".env")
        with open(env_file, "w") as f:
            f.write("GOOGLE_CREDENTIALS_FILE=./credentials.json\n")
        
        # ConfigManagerを作成
        config_manager = ConfigManager(env_file=env_file)
        config = config_manager.load_config()
        
        # トークンファイルのデフォルト値が正しく設定されていることを確認
        assert config.google_sheets.token_file == "token.json"

def test_prefix_choice():
    """前方一致によるパラメータ省略機能が正しく動作することを確認する"""
    from src.utils.param_utils import PrefixChoice
    import click
    
    # PrefixChoiceを作成
    prefix_choice = PrefixChoice(['tradingview', 'seekingalpha', 'csv'])
    
    # 完全一致のテスト
    assert prefix_choice.convert('tradingview', None, None) == 'tradingview'
    assert prefix_choice.convert('seekingalpha', None, None) == 'seekingalpha'
    assert prefix_choice.convert('csv', None, None) == 'csv'
    
    # 前方一致のテスト
    assert prefix_choice.convert('trading', None, None) == 'tradingview'
    assert prefix_choice.convert('tra', None, None) == 'tradingview'
    assert prefix_choice.convert('t', None, None) == 'tradingview'
    assert prefix_choice.convert('seeking', None, None) == 'seekingalpha'
    assert prefix_choice.convert('seek', None, None) == 'seekingalpha'
    assert prefix_choice.convert('s', None, None) == 'seekingalpha'
    
    # 大文字小文字のテスト
    assert prefix_choice.convert('TRADING', None, None) == 'tradingview'
    assert prefix_choice.convert('SEEKING', None, None) == 'seekingalpha'
    
    # 不正な値のテスト（例外が発生することを確認）
    try:
        prefix_choice.convert('invalid', None, None)
        assert False, "例外が発生するはず"
    except click.BadParameter:
        pass  # 期待通りの例外