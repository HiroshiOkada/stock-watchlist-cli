import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from src.google_sheets.auth import GoogleSheetsAuth
from google.oauth2.credentials import Credentials

# テスト用の設定
CREDENTIALS_FILE = "dummy_credentials.json"
TOKEN_FILE = "dummy_token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@pytest.fixture
def auth_manager(tmp_path):
    """テスト用のGoogleSheetsAuthインスタンスを作成するフィクスチャ"""
    # ダミーの認証ファイルを作成
    creds_path = tmp_path / CREDENTIALS_FILE
    creds_path.write_text(json.dumps({
        "installed": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }))
    
    token_path = tmp_path / TOKEN_FILE
    
    manager = GoogleSheetsAuth(
        credentials_file=str(creds_path),
        token_file=str(token_path),
        scopes=SCOPES
    )
    return manager

class TestGoogleSheetsAuth:
    """GoogleSheetsAuthクラスのテスト"""

    def test_no_token_file_performs_oauth_flow(self, auth_manager, mocker):
        """トークンファイルが存在しない場合、OAuthフローが実行されることをテスト"""
        mock_flow = mocker.patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
        mock_run_local = mock_flow.return_value.run_local_server
        # to_jsonが文字列を返すように設定
        mock_run_local.return_value.to_json.return_value = '{}'
        
        # ダミーのトークンファイルが存在しないことを確認
        if auth_manager.token_file.exists():
            auth_manager.token_file.unlink()

        auth_manager.get_credentials()
        
        mock_flow.assert_called_once()
        mock_run_local.assert_called_once()

    def test_existing_valid_token_is_used(self, auth_manager, mocker):
        """有効なトークンファイルが存在する場合、それが使用されることをテスト"""
        # ダミーのトークンファイルを作成
        auth_manager.token_file.write_text('{"token": "dummy"}')

        dummy_creds = MagicMock(spec=Credentials)
        dummy_creds.valid = True
        
        mocker.patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=dummy_creds)
        
        mock_flow = mocker.patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')

        creds = auth_manager.get_credentials()
        
        assert creds.valid
        mock_flow.assert_not_called()

    def test_expired_token_is_refreshed(self, auth_manager, mocker):
        """期限切れのトークンはリフレッシュされることをテスト"""
        # ダミーのトークンファイルを作成
        auth_manager.token_file.write_text('{"token": "dummy", "refresh_token": "dummy_refresh_token"}')

        expired_creds = MagicMock(spec=Credentials)
        expired_creds.valid = False
        expired_creds.expired = True
        expired_creds.refresh_token = "dummy_refresh_token"
        # to_jsonが文字列を返すように設定
        expired_creds.to_json.return_value = '{}'
        
        mocker.patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=expired_creds)
        mock_refresh = mocker.patch.object(expired_creds, 'refresh')
        
        auth_manager.get_credentials()
        
        mock_refresh.assert_called_once()

    def test_credentials_file_not_found(self, tmp_path):
        """認証情報ファイルが見つからない場合にエラーが発生することをテスト"""
        invalid_manager = GoogleSheetsAuth(
            credentials_file=str(tmp_path / "non_existent.json"),
            token_file=str(tmp_path / TOKEN_FILE),
            scopes=SCOPES
        )
        
        with pytest.raises(FileNotFoundError):
            invalid_manager.get_credentials()

    def test_get_gspread_client(self, auth_manager, mocker):
        """gspreadクライアントが正しく取得できることをテスト"""
        mocker.patch.object(auth_manager, 'get_credentials', return_value=MagicMock(spec=Credentials))
        mock_authorize = mocker.patch('gspread.authorize')
        
        client = auth_manager.get_gspread_client()
        
        mock_authorize.assert_called_once()
        assert client is not None