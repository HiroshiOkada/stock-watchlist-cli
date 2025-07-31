"""ログ設定管理モジュール"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from src.config.settings import get_config


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_size: str = "10MB",
    backup_count: int = 5,
) -> logging.Logger:
    """
    ログ設定をセットアップする
    
    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ログファイルパス
        max_size: ログファイルの最大サイズ
        backup_count: バックアップファイル数
        
    Returns:
        設定済みのロガー
    """
    config = get_config()
    
    # 設定値の取得（引数が優先）
    level = log_level or config.logging.level
    file_path = log_file or config.logging.file
    max_bytes = _parse_size(max_size or config.logging.max_size)
    backup_count = backup_count or config.logging.backup_count
    log_format = config.logging.format
    
    # ログレベルの設定
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # フォーマッターの作成
    formatter = logging.Formatter(log_format)
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ファイルハンドラーの設定（ファイルパスが指定されている場合）
    if file_path:
        # ログディレクトリの作成
        log_path = Path(file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ローテーティングファイルハンドラーの設定
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # プロジェクト専用ロガーの取得
    logger = logging.getLogger('stock_watchlist_cli')
    logger.info(f"ログ設定完了 - レベル: {level}, ファイル: {file_path}")
    
    return logger


def _parse_size(size_str: str) -> int:
    """
    サイズ文字列をバイト数に変換する
    
    Args:
        size_str: サイズ文字列 (例: "10MB", "1GB", "500KB")
        
    Returns:
        バイト数
    """
    size_str = size_str.upper().strip()
    
    # 数値部分と単位部分を分離
    import re
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    if not match:
        raise ValueError(f"無効なサイズ形式: {size_str}")
    
    number, unit = match.groups()
    number = float(number)
    
    # 単位の変換
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    # 単位が省略された場合はバイトとして扱う
    if not unit or unit == '':
        unit = 'B'
    
    multiplier = multipliers.get(unit, 1)
    return int(number * multiplier)


def get_logger(name: str) -> logging.Logger:
    """
    指定された名前のロガーを取得する
    
    Args:
        name: ロガー名
        
    Returns:
        ロガーインスタンス
    """
    return logging.getLogger(f'stock_watchlist_cli.{name}')