"""株式ウォッチリスト管理CLI メインエントリーポイント"""

import click
from typing import Optional

from src.utils.logging_config import setup_logging, get_logger
from src.config.settings import get_config, AppConfig
from src.google_sheets.auth import GoogleSheetsAuth
from src.converters.format_converter import FormatConverter
from src.utils.param_utils import PrefixChoice


@click.group()
@click.version_option(version="0.1.3", prog_name="stock-cli")
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
@click.option('--from', 'from_format', required=True, type=PrefixChoice(['tradingview', 'seekingalpha']),
              help='変換元のファイル形式 (tradingview, seekingalpha)')
@click.option('--to', 'to_format', required=True, type=PrefixChoice(['tradingview', 'seekingalpha', 'csv']),
              help='変換先のファイル形式 (tradingview, seekingalpha, csv)')
@click.option('--input', 'input_path', required=True, type=click.Path(exists=True),
              help='入力ファイルパス')
@click.option('--output', 'output_path', type=click.Path(),
              help='出力ファイルパス (指定しない場合、標準出力)')
@click.option('--preserve-sections', is_flag=True,
              help='TradingView形式への変換時にセクション情報を保持する')
@click.option('--create-sections-by-sector', is_flag=True,
              help='SeekingAlphaからTradingViewへの変換時にセクターでセクションを作成する')
@click.pass_context
def convert(ctx: click.Context, from_format: str, to_format: str, input_path: str,
            output_path: Optional[str], preserve_sections: bool, create_sections_by_sector: bool) -> None:
    """ファイル形式変換コマンド"""
    logger = get_logger('main')
    converter = FormatConverter()
    
    try:
        # ファイル読み込み
        # TODO: file_io.py にてファイル形式を自動判定し、適切なパーサーを呼び出すロジックを実装
        # 現時点では、from_formatに基づいて手動でパーサーを選択
        if from_format == "tradingview":
            from src.parsers.tradingview import TradingViewParser
            parser = TradingViewParser()
            raw_data = parser.parse(input_path)
            # TradingViewDataのリストをStockDataのリストに変換
            stock_data_list = [converter.to_stock_data(d) for d in raw_data]
        elif from_format == "seekingalpha":
            from src.parsers.seekingalpha import SeekingAlphaParser
            parser = SeekingAlphaParser()
            raw_data = parser.parse(input_path)
            # SeekingAlphaDataのリストをStockDataのリストに変換
            stock_data_list = [converter.to_stock_data(d) for d in raw_data]
        else:
            logger.error(f"未サポートの入力形式: {from_format}")
            ctx.exit(1)

        output_content: str = ""
        if to_format == "tradingview":
            # StockDataのリストをTradingViewDataのリストに変換
            tv_data_list = [converter.to_platform_data(d, "tradingview") for d in stock_data_list]
            output_content = converter.convert_to_tradingview_txt(tv_data_list, preserve_sections)
        elif to_format == "seekingalpha" or to_format == "csv":
            # StockDataのリストをSeekingAlphaDataのリストに変換
            sa_data_list = [converter.to_platform_data(d, "seekingalpha") for d in stock_data_list]
            output_content = converter.convert_to_csv(sa_data_list)
        else:
            logger.error(f"未サポートの出力形式: {to_format}")
            ctx.exit(1)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            logger.info(f"変換結果を {output_path} に出力しました。")
        else:
            click.echo(output_content)
            logger.info("変換結果を標準出力しました。")

    except Exception as e:
        logger.error(f"ファイル変換中にエラーが発生しました: {e}")
        click.echo(f"エラー: {e}", err=True)
        ctx.exit(1)

@click.group()
def auth():
    """Google認証関連のコマンド"""
    pass

@auth.command()
@click.pass_context
def setup(ctx: click.Context):
    """Google APIの認証を行い、トークンファイルを作成する"""
    logger = get_logger('main')
    try:
        config: AppConfig = ctx.obj['config']
        gs_config = config.google_sheets
        
        logger.info("Google認証セットアップを開始します...")
        auth_manager = GoogleSheetsAuth(
            credentials_file=gs_config.credentials_file,
            token_file=gs_config.token_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ],
            port=gs_config.oauth_port
        )
        
        # 認証実行
        auth_manager.get_credentials()
        
        click.echo("認証に成功し、トークンファイルが正常に作成・更新されました。")
        logger.info("Google認証セットアップが正常に完了しました。")
        
    except FileNotFoundError as e:
        logger.error(f"認証ファイルが見つかりません: {e}")
        click.echo(f"エラー: {e}", err=True)
        click.echo("ヒント: .envファイルで 'GOOGLE_CREDENTIALS_FILE' が正しく設定されているか確認してください。")
        ctx.exit(1)
    except Exception as e:
        logger.error(f"Google認証中に予期せぬエラーが発生しました: {e}")
        click.echo(f"エラー: {e}", err=True)
        ctx.exit(1)

@cli.group()
def sheets() -> None:
    """Google Sheets連携コマンド"""
    pass

@sheets.command('import')
@click.option('--file', 'file_path', required=True, type=click.Path(exists=True), help='インポートするファイルパス')
@click.option('--format', 'file_format', required=True, type=PrefixChoice(['tradingview', 'seekingalpha']), help='インポートするファイル形式')
@click.option('--spreadsheet-id', required=True, help='インポート先のスプレッドシートID')
@click.option('--sheet-name', default='Stock_Data', help='インポート先のシート名')
@click.pass_context
def sheets_import(ctx: click.Context, file_path: str, file_format: str, spreadsheet_id: str, sheet_name: str):
    """ローカルファイルをGoogle Sheetsにインポートする"""
    logger = get_logger('main')
    config: AppConfig = ctx.obj['config']
    
    try:
        logger.info(f"'{file_path}' をGoogle Sheetsにインポートします...")
        
        # 1. パーサーを選択してファイルをパース
        if file_format == 'tradingview':
            from src.parsers.tradingview import TradingViewParser
            parser = TradingViewParser()
        elif file_format == 'seekingalpha':
            from src.parsers.seekingalpha import SeekingAlphaParser
            parser = SeekingAlphaParser()
        else:
            # このケースはChoiceによって弾かれるはず
            raise ValueError(f"未サポートのファイル形式です: {file_format}")
            
        platform_data = parser.parse(file_path)
        
        # 2. データをStockDataに変換
        from src.converters.format_converter import FormatConverter
        converter = FormatConverter()
        stock_data_list = [converter.to_stock_data(d) for d in platform_data]
        
        # 3. GoogleSheetsClientを使ってシートを更新
        auth_manager = GoogleSheetsAuth(
            credentials_file=config.google_sheets.credentials_file,
            token_file=config.google_sheets.token_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        from src.google_sheets.client import GoogleSheetsClient
        sheets_client = GoogleSheetsClient(auth_manager)
        
        sheets_client.update_sheet_with_data(spreadsheet_id, sheet_name, stock_data_list)
        
        click.echo(f"正常にインポートが完了しました。{len(stock_data_list)}件のデータが'{sheet_name}'シートに書き込まれました。")
        logger.info("インポート処理が正常に完了しました。")

    except Exception as e:
        logger.error(f"インポート処理中にエラーが発生しました: {e}")
        click.echo(f"エラー: {e}", err=True)
        ctx.exit(1)

@sheets.command('export')
@click.option('--spreadsheet-id', required=True, help='エクスポート元のスプレッドシートID')
@click.option('--sheet-name', default='Stock_Data', help='エクスポート元のシート名')
@click.option('--format', 'output_format', required=True, type=PrefixChoice(['tradingview', 'seekingalpha', 'csv']), help='エクスポートするファイル形式')
@click.option('--output', 'output_path', type=click.Path(), help='出力ファイルパス (指定しない場合、標準出力)')
@click.pass_context
def sheets_export(ctx: click.Context, spreadsheet_id: str, sheet_name: str, output_format: str, output_path: Optional[str]):
    """Google Sheetsのデータをローカルファイルにエクスポートする"""
    logger = get_logger('main')
    config: AppConfig = ctx.obj['config']
    
    try:
        logger.info(f"Google Sheetsから'{sheet_name}'シートのデータをエクスポートします...")
        
        # 1. GoogleSheetsClientを使ってデータを取得
        auth_manager = GoogleSheetsAuth(
            credentials_file=config.google_sheets.credentials_file,
            token_file=config.google_sheets.token_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        from src.google_sheets.client import GoogleSheetsClient
        sheets_client = GoogleSheetsClient(auth_manager)
        
        records = sheets_client.get_all_records(spreadsheet_id, sheet_name)
        
        # 2. レコードをStockDataに変換
        from src.converters.format_converter import FormatConverter
        converter = FormatConverter()
        stock_data_list = converter.from_records(records)
        
        # 3. 指定されたフォーマットに変換
        from src.converters.format_converter import FormatConverter
        converter = FormatConverter()
        output_content = ""

        if output_format == "tradingview":
            tv_data_list = [converter.to_platform_data(d, "tradingview") for d in stock_data_list]
            output_content = converter.convert_to_tradingview_txt(tv_data_list, preserve_sections=True)
        elif output_format in ["seekingalpha", "csv"]:
            sa_data_list = [converter.to_platform_data(d, "seekingalpha") for d in stock_data_list]
            output_content = converter.convert_to_csv(sa_data_list)
        else:
            raise ValueError(f"未サポートの出力形式です: {output_format}")

        # 4. 結果を出力
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            click.echo(f"正常にエクスポートが完了しました。{output_path} に出力しました。")
        else:
            click.echo(output_content)
        
        logger.info("エクスポート処理が正常に完了しました。")

    except Exception as e:
        logger.error(f"エクスポート処理中にエラーが発生しました: {e}")
        click.echo(f"エラー: {e}", err=True)
        ctx.exit(1)

@sheets.command('create')
@click.option('--name', required=True, help='作成するスプレッドシートの名前')
@click.pass_context
def sheets_create(ctx: click.Context, name: str):
    """新しいGoogleスプレッドシートを作成する"""
    logger = get_logger('main')
    config: AppConfig = ctx.obj['config']
    
    try:
        logger.info(f"新しいスプレッドシート '{name}' を作成します...")
        
        auth_manager = GoogleSheetsAuth(
            credentials_file=config.google_sheets.credentials_file,
            token_file=config.google_sheets.token_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        from src.google_sheets.client import GoogleSheetsClient
        sheets_client = GoogleSheetsClient(auth_manager)
        
        spreadsheet = sheets_client.create_spreadsheet(name)
        
        click.echo("スプレッドシートが正常に作成されました。")
        click.echo(f"  名前: {spreadsheet.title}")
        click.echo(f"  ID: {spreadsheet.id}")
        click.echo(f"  URL: {spreadsheet.url}")
        logger.info(f"スプレッドシートの作成が完了しました: {spreadsheet.url}")

    except Exception as e:
        logger.error(f"スプレッドシート作成中にエラーが発生しました: {e}")
        click.echo(f"エラー: {e}", err=True)
        ctx.exit(1)

# cliにauthコマンドグループを追加
cli.add_command(auth)

@cli.command()
def analyze() -> None:
    """データ分析コマンド"""
    pass

if __name__ == '__main__':
    cli()