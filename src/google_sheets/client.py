"""Google Sheets API クライアントモジュール"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import gspread
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from src.google_sheets.auth import GoogleSheetsAuth
from src.models.stock import StockData

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """Google Sheetsクライアント"""

    def __init__(self, auth_manager: GoogleSheetsAuth):
        self.auth_manager = auth_manager
        self.client = auth_manager.get_gspread_client()
        logger.info("GoogleSheetsClient initialized.")

    def create_spreadsheet(self, name: str) -> Spreadsheet:
        """新しいスプレッドシートを作成する"""
        try:
            spreadsheet = self.client.create(name)
            logger.info(f"スプレッドシートを作成しました: {name} (ID: {spreadsheet.id})")
            
            # デフォルトのヘッダーを設定
            worksheet = spreadsheet.get_worksheet(0)
            self.setup_default_headers(worksheet)
            
            # デフォルトのシート名を "Stock_Data" に変更
            worksheet.update_title("Stock_Data")
            logger.info("デフォルトのシート名を 'Stock_Data' に変更しました。")

            return spreadsheet
        except Exception as e:
            logger.error(f"スプレッドシートの作成に失敗しました: {e}")
            raise

    def get_spreadsheet_by_id(self, spreadsheet_id: str) -> Spreadsheet:
        """IDでスプレッドシートを取得する"""
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            logger.info(f"スプレッドシートを開きました: {spreadsheet.title}")
            return spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"スプレッドシートが見つかりません: ID={spreadsheet_id}")
            raise
        except Exception as e:
            logger.error(f"スプレッドシートの取得中にエラーが発生しました: {e}")
            raise

    def get_all_records(self, spreadsheet_id: str, sheet_name: str) -> List[Dict[str, Any]]:
        """指定したシートのすべてのレコードを取得する"""
        try:
            spreadsheet = self.get_spreadsheet_by_id(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            records = worksheet.get_all_records()
            logger.info(f"'{sheet_name}'から{len(records)}件のレコードを取得しました。")
            return records
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"ワークシートが見つかりません: {sheet_name}")
            raise
        except Exception as e:
            logger.error(f"レコードの取得中にエラーが発生しました: {e}")
            raise

    def setup_default_headers(self, worksheet: Worksheet) -> None:
        """指定したワークシートにデフォルトのヘッダーを設定する"""
        try:
            headers = [
                "Symbol", "Exchange", "Company_Name", "Current_Price",
                "Source_Platform", "TradingView_Section", "Quant_Rating",
                "SA_Analyst_Rating", "Valuation_Grade", "Dividend_Safety",
                "Yield_TTM", "Date_Updated", "Notes"
            ]
            worksheet.update('A1', [headers])
            logger.info(f"'{worksheet.title}'シートにデフォルトヘッダーを設定しました。")
        except Exception as e:
            logger.error(f"ヘッダーの設定に失敗しました: {e}")
            raise

    def update_sheet_with_data(self, spreadsheet_id: str, sheet_name: str, data: List[StockData]) -> None:
        """StockDataのリストでシートを更新する（バッチ処理）"""
        try:
            spreadsheet = self.get_spreadsheet_by_id(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # ヘッダーを取得して、書き込むデータの順序を決定
            headers = worksheet.row_values(1)
            if not headers:
                logger.warning(f"'{sheet_name}'にヘッダーが見つかりません。デフォルトヘッダーを設定します。")
                self.setup_default_headers(worksheet)
                headers = worksheet.row_values(1)

            # StockDataをヘッダー順のリストのリストに変換
            values_to_update = []
            for stock in data:
                row = []
                for header in headers:
                    attr = header.lower()
                    # シートの見出しとStockData属性名の差異を吸収
                    if attr == "company_name":
                        attr = "name"
                    value = getattr(stock, attr, "")
                    if isinstance(value, datetime):
                        row.append(value.isoformat())
                    elif value is None:
                        row.append("")
                    else:
                        row.append(value)
                values_to_update.append(row)
            
            if not values_to_update:
                logger.info("更新するデータがありません。")
                return

            # 2行目からデータを書き込む (A2から)
            worksheet.update(f'A2', values_to_update)
            
            logger.info(f"'{sheet_name}'シートを{len(values_to_update)}件のデータで更新しました。")

        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"ワークシートが見つかりません: {sheet_name}")
            raise
        except Exception as e:
            logger.error(f"シートの更新中にエラーが発生しました: {e}")

    def sheet_exists(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """指定したシートが存在するかを確認する"""
        try:
            spreadsheet = self.get_spreadsheet_by_id(spreadsheet_id)
            spreadsheet.worksheet(sheet_name)
            return True
        except gspread.exceptions.WorksheetNotFound:
            return False
        except Exception as e:
            logger.error(f"シートの存在確認中にエラーが発生しました: {e}")
            raise

    def create_sheet(self, spreadsheet_id: str, sheet_name: str) -> Worksheet:
        """新しいシートを作成する"""
        try:
            spreadsheet = self.get_spreadsheet_by_id(spreadsheet_id)
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
            logger.info(f"シートを作成しました: {sheet_name}")
            
            # デフォルトのヘッダーを設定
            self.setup_default_headers(worksheet)
            
            return worksheet
        except Exception as e:
            logger.error(f"シートの作成に失敗しました: {e}")
            raise

    def clear_sheet(self, spreadsheet_id: str, sheet_name: str) -> None:
        """指定したシートの全内容をクリアする（書式は維持）"""
        try:
            spreadsheet = self.get_spreadsheet_by_id(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
            logger.info(f"'{sheet_name}' の内容をクリアしました。")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"ワークシートが見つかりません: {sheet_name}")
            raise
        except Exception as e:
            logger.error(f"シートのクリア中にエラーが発生しました: {e}")
            raise
