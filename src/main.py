"""株式ウォッチリスト管理CLI メインエントリーポイント"""

import click
from typing import Optional

from src.utils.logging_config import setup_logging, get_logger
from src.config.settings import get_config


# ロガーの初期化
logger = get_logger('main')


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
        logger.info("設定ファイルを読み込みました")
    except Exception as e:
        logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
        ctx.exit(1)


@cli.group()
@click.pass_context
def convert(ctx: click.Context) -> None:
    """ファイル形式変換コマンド"""
    pass


@convert.command()
@click.option('--from', 'from_format', required=True, 
              type=click.Choice(['tradingview', 'seekingalpha']),
              help='変換元形式')
@click.option('--to', 'to_format', required=True,
              type=click.Choice(['tradingview', 'seekingalpha', 'csv']),
              help='変換先形式')
@click.option('--input', '-i', 'input_file', required=True,
              type=click.Path(exists=True), help='入力ファイルパス')
@click.option('--output', '-o', 'output_file', required=True,
              type=click.Path(), help='出力ファイルパス')
@click.option('--preserve-sections', is_flag=True,
              help='セクション情報を保持する')
@click.pass_context
def file(ctx: click.Context, from_format: str, to_format: str, 
         input_file: str, output_file: str, preserve_sections: bool) -> None:
    """ファイル間でのデータ変換"""
    logger.info(f"変換開始: {from_format} -> {to_format}")
    logger.info(f"入力: {input_file}, 出力: {output_file}")
    
    # TODO: Phase 3で実装予定
    click.echo("ファイル変換機能は Phase 3 で実装予定です")


@cli.group()
@click.pass_context
def sheets(ctx: click.Context) -> None:
    """Google Sheets連携コマンド"""
    pass


@sheets.command()
@click.option('--name', required=True, help='スプレッドシート名')
@click.option('--template', default='basic',
              type=click.Choice(['basic', 'seekingalpha-full']),
              help='テンプレート種類')
@click.pass_context
def create(ctx: click.Context, name: str, template: str) -> None:
    """新規スプレッドシートを作成"""
    logger.info(f"スプレッドシート作成: {name} (テンプレート: {template})")
    
    # TODO: Phase 4で実装予定
    click.echo("Google Sheets連携機能は Phase 4 で実装予定です")


@sheets.command()
@click.option('--file', '-f', 'file_path', required=True,
              type=click.Path(exists=True), help='インポートファイルパス')
@click.option('--format', 'file_format', required=True,
              type=click.Choice(['tradingview', 'seekingalpha']),
              help='ファイル形式')
@click.option('--spreadsheet-id', required=True, help='スプレッドシートID')
@click.option('--preserve-all-data', is_flag=True,
              help='全データを保持してインポート')
@click.pass_context
def import_data(ctx: click.Context, file_path: str, file_format: str,
                spreadsheet_id: str, preserve_all_data: bool) -> None:
    """ファイルからGoogle Sheetsにデータをインポート"""
    logger.info(f"データインポート: {file_path} -> {spreadsheet_id}")
    
    # TODO: Phase 4で実装予定
    click.echo("データインポート機能は Phase 4 で実装予定です")


@sheets.command()
@click.option('--spreadsheet-id', required=True, help='スプレッドシートID')
@click.option('--sheet', help='シート名（指定しない場合は全シート）')
@click.option('--format', 'output_format', required=True,
              type=click.Choice(['tradingview', 'seekingalpha', 'csv']),
              help='出力形式')
@click.option('--output', '-o', 'output_file', required=True,
              type=click.Path(), help='出力ファイルパス')
@click.pass_context
def export(ctx: click.Context, spreadsheet_id: str, sheet: Optional[str],
           output_format: str, output_file: str) -> None:
    """Google Sheetsからファイルにデータをエクスポート"""
    logger.info(f"データエクスポート: {spreadsheet_id} -> {output_file}")
    
    # TODO: Phase 4で実装予定
    click.echo("データエクスポート機能は Phase 4 で実装予定です")


@cli.group()
@click.pass_context
def analyze(ctx: click.Context) -> None:
    """データ分析コマンド"""
    pass


@analyze.command()
@click.option('--file', '-f', 'file_path', required=True,
              type=click.Path(exists=True), help='分析対象ファイル')
@click.option('--show-sections', is_flag=True, help='セクション情報を表示')
@click.option('--show-stats', is_flag=True, help='統計情報を表示')
@click.pass_context
def tradingview(ctx: click.Context, file_path: str, show_sections: bool,
                show_stats: bool) -> None:
    """TradingViewファイルの分析"""
    logger.info(f"TradingViewファイル分析: {file_path}")
    
    # TODO: Phase 2で実装予定
    click.echo("TradingView分析機能は Phase 2 で実装予定です")


@cli.group()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """認証管理コマンド"""
    pass


@auth.command()
@click.option('--credentials-file', help='認証ファイルパス')
@click.pass_context
def setup(ctx: click.Context, credentials_file: Optional[str]) -> None:
    """Google認証のセットアップ"""
    logger.info("Google認証セットアップを開始")
    
    # TODO: Phase 4で実装予定
    click.echo("認証セットアップ機能は Phase 4 で実装予定です")


@auth.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """認証状態の確認"""
    logger.info("認証状態を確認中")
    
    # TODO: Phase 4で実装予定
    click.echo("認証状態確認機能は Phase 4 で実装予定です")


@cli.command()
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """現在の設定を表示"""
    try:
        config = ctx.obj['config']
        click.echo("=== 現在の設定 ===")
        click.echo(f"Google Sheets認証ファイル: {config.google_sheets.credentials_file}")
        click.echo(f"ログレベル: {config.logging.level}")
        click.echo(f"ログファイル: {config.logging.file}")
        click.echo(f"デバッグモード: {config.development.debug_mode}")
    except Exception as e:
        logger.error(f"設定の表示に失敗しました: {e}")
        click.echo("設定の読み込みに失敗しました")


if __name__ == '__main__':
    cli()