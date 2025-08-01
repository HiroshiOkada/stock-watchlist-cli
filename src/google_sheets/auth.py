"""Google Sheets API 認証管理モジュール"""
import json
import logging
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread

logger = logging.getLogger(__name__)

class GoogleSheetsAuth:
    """Google Sheets認証管理クラス"""

    def __init__(self,
                 credentials_file: str,
                 token_file: str,
                 scopes: List[str],
                 port: int = 8080):
        # チルダ(~)をホームディレクトリに展開する
        self.credentials_file = Path(credentials_file).expanduser()
        self.token_file = Path(token_file).expanduser()
        self.scopes = scopes
        self.port = port
        logger.info(f"GoogleSheetsAuth initialized with credentials: {self.credentials_file}")

    def get_credentials(self) -> Credentials:
        """認証情報を取得または新規作成する"""
        creds: Optional[Credentials] = None
        
        # 既存のトークンファイルをチェック
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), self.scopes)
                logger.info("既存の認証トークンを読み込みました")
            except Exception as e:
                logger.warning(f"既存トークンの読み込みに失敗: {e}")

        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("認証トークンを更新しました")
                except Exception as e:
                    logger.warning(f"トークン更新に失敗: {e}")
                    creds = self._perform_oauth_flow()
            else:
                creds = self._perform_oauth_flow()
            
            # 新しい認証情報を保存
            self._save_credentials(creds)
            
        return creds

    def _perform_oauth_flow(self) -> Credentials:
        """OAuth認証フローを実行"""
        if not self.credentials_file.exists():
            raise FileNotFoundError(f"認証ファイルが見つかりません: {self.credentials_file}")
        
        logger.info("OAuth認証フローを開始します...")
        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), self.scopes)
        creds = flow.run_local_server(port=self.port)
        logger.info("OAuth認証が完了しました")
        return creds

    def _save_credentials(self, creds: Credentials) -> None:
        """認証情報をファイルに保存"""
        try:
            with open(self.token_file, "w") as token_file:
                token_file.write(creds.to_json())
            logger.info(f"認証情報を保存しました: {self.token_file}")
        except Exception as e:
            logger.error(f"認証情報の保存に失敗: {e}")
            raise

    def get_gspread_client(self) -> gspread.Client:
        """gspreadクライアントを取得"""
        creds = self.get_credentials()
        client = gspread.authorize(creds)
        logger.info("Google Sheetsクライアントを作成しました")
        return client

    def revoke_credentials(self) -> None:
        """認証情報を削除（再認証強制用）"""
        if self.token_file.exists():
            self.token_file.unlink()
            logger.info("認証情報を削除しました")