"""設定管理モジュール"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class GoogleSheetsConfig(BaseModel):
    """Google Sheets設定"""
    credentials_file: str
    token_file: str = "token.json"
    oauth_port: int = 8080
    default_spreadsheet_id: str = ""
    sheet_name: str = "Stock_Data"
    batch_size: int = 100


class TradingViewConfig(BaseModel):
    """TradingView設定"""
    encoding: str = "utf-8"
    include_exchange_prefix: bool = True
    supported_exchanges: List[str] = Field(
        default_factory=lambda: ["NASDAQ", "NYSE", "AMEX", "TSE", "LSE", "FRA"]
    )


class SeekingAlphaConfig(BaseModel):
    """SeekingAlpha設定"""
    default_quantity: int = 0
    default_cost: float = 0.0
    required_sheets: List[str] = Field(
        default_factory=lambda: ["Summary", "Ratings", "Holdings", "Dividends"]
    )


class PlatformsConfig(BaseModel):
    """プラットフォーム設定"""
    tradingview: TradingViewConfig = Field(default_factory=TradingViewConfig)
    seekingalpha: SeekingAlphaConfig = Field(default_factory=SeekingAlphaConfig)


class LoggingConfig(BaseModel):
    """ログ設定"""
    level: str = "INFO"
    file: str = "stock_cli.log"
    max_size: str = "10MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConversionConfig(BaseModel):
    """変換設定"""
    symbol_mapping_file: str = "symbol_mapping.json"
    auto_detect_exchange: bool = True
    fallback_exchange: str = "NASDAQ"
    preserve_sections: bool = True


class DevelopmentConfig(BaseModel):
    """開発設定"""
    debug_mode: bool = False
    test_data_dir: str = "tests/sample_data"
    mock_google_api: bool = False


class AppConfig(BaseModel):
    """アプリケーション設定"""
    google_sheets: GoogleSheetsConfig
    platforms: PlatformsConfig = Field(default_factory=PlatformsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    conversion: ConversionConfig = Field(default_factory=ConversionConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)


class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_file: Optional[str] = None, env_file: Optional[str] = None):
        self.config_file = config_file or "config/config.yaml"
        self.env_file = env_file or ".env"
        self._config: Optional[AppConfig] = None
        
    def load_config(self) -> AppConfig:
        """設定を読み込む"""
        if self._config is not None:
            return self._config
            
        # 環境変数の読み込み
        if Path(self.env_file).exists():
            load_dotenv(self.env_file)
        
        # YAML設定ファイルの読み込み
        config_data = self._load_yaml_config()
        
        # 環境変数による置換
        config_data = self._substitute_env_vars(config_data)
        
        # Pydanticモデルの作成
        self._config = AppConfig(**config_data)
        
        return self._config
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """YAML設定ファイルを読み込む"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            # 設定ファイルが見つからない場合は、デフォルトの設定を使用
            return self._get_default_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML設定ファイルの解析に失敗しました: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルトの設定を返す"""
        return {
            "google_sheets": {
                "credentials_file": "${GOOGLE_CREDENTIALS_FILE}",
                "token_file": "${GOOGLE_TOKEN_FILE}",
                "oauth_port": 8080,
                "default_spreadsheet_id": "",
                "sheet_name": "Stock_Data",
                "batch_size": 100
            },
            "platforms": {
                "tradingview": {
                    "encoding": "utf-8",
                    "include_exchange_prefix": True,
                    "supported_exchanges": ["NASDAQ", "NYSE", "AMEX", "TSE", "LSE", "FRA"]
                },
                "seekingalpha": {
                    "default_quantity": 0,
                    "default_cost": 0.0,
                    "required_sheets": ["Summary", "Ratings", "Holdings", "Dividends"]
                }
            },
            "logging": {
                "level": "${LOG_LEVEL:INFO}",
                "file": "${LOG_FILE:stock_cli.log}",
                "max_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "conversion": {
                "symbol_mapping_file": "symbol_mapping.json",
                "auto_detect_exchange": True,
                "fallback_exchange": "NASDAQ",
                "preserve_sections": True
            },
            "development": {
                "debug_mode": "${DEVELOPMENT_MODE:false}",
                "test_data_dir": "tests/sample_data",
                "mock_google_api": False
            }
        }
    def _substitute_env_vars(self, data: Any) -> Any:
        """環境変数による置換を行う"""
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._substitute_string_env_vars(data)
        else:
            return data
    
    def _substitute_string_env_vars(self, value: str) -> str:
        """文字列内の環境変数を置換する"""
        import re
        
        # ${VAR_NAME} または ${VAR_NAME:default_value} の形式をサポート
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_match(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)
        
        return re.sub(pattern, replace_match, value)
    
    def reload_config(self) -> AppConfig:
        """設定を再読み込みする"""
        self._config = None
        return self.load_config()


# グローバル設定マネージャー
_config_manager = ConfigManager()


def get_config() -> AppConfig:
    """アプリケーション設定を取得する"""
    return _config_manager.load_config()


def reload_config() -> AppConfig:
    """設定を再読み込みする"""
    return _config_manager.reload_config()


def set_config_file(config_file: str, env_file: Optional[str] = None) -> None:
    """設定ファイルパスを変更する"""
    global _config_manager
    _config_manager = ConfigManager(config_file, env_file)