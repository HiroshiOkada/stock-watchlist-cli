"""株式ウォッチリスト管理CLI メインエントリーポイント"""

import click
from typing import Optional

from src.utils.logging_config import setup_logging, get_logger
from src.config.settings import get_config


@click.group()
@click.version_option(version="0.1.0", prog_name="stock-cli")
@click.option('--config', '-c', help='設定ファイルパス')
@click.option('--verbose', '-v', is_flag=True, help='詳細ログを表示')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """株式ウォッチリスト管理CLI
    
    TradingView、Seeking Alpha、Google Sheets間でのデータ変換ツール
    """
    # コンテキストオブジェクトの初期化
    ctx.ensure_object(dict)
    
    # ログレベルの設定
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level=log_level)
    
    # 設定の読み込み
    try:
        app_config = get_config()
        ctx.obj['config'] = app_config
        get_logger('main').info("設定ファイルを読み込みました")
    except Exception as e:
        message = f"設定ファイルの読み込みに失敗しました: {e}"
        get_logger('main').error(message)
        click.echo(message, err=True)
        ctx.exit(1)

# この時点ではサブコマンドはまだ実装しない

@cli.command()
def convert() -> None:
    """ファイル形式変換コマンド"""
    pass

@cli.command()
def sheets() -> None:
    """Google Sheets連携コマンド"""
    pass

@cli.command()
def analyze() -> None:
    """データ分析コマンド"""
    pass

if __name__ == '__main__':
    cli()