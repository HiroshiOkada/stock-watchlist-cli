import chardet
import pandas as pd
from pathlib import Path
from typing import Union, Optional, Any

def get_file_encoding(file_path: Union[str, Path], sample_size: int = 1024) -> Optional[str]:
    """
    ファイルのエンコーディングを検出する

    Args:
        file_path: ファイルパス
        sample_size: 検出に使用するファイルの先頭からのバイト数

    Returns:
        検出されたエンコーディング、またはバイナリファイルの場合は'binary'
    """
    with open(file_path, "rb") as f:
        sample = f.read(sample_size)
        if b'\x50\x4B\x03\x04' in sample[:100]:
             return 'binary'
        result = chardet.detect(sample)
        return result["encoding"] or "utf-8"

def read_file(file_path: Union[str, Path]) -> Any:
    """
    指定されたファイルを読み込み、内容を返す
    - .txt, .csv: テキストとして読み込む
    - .xlsx: pandas DataFrameとして読み込む

    Args:
        file_path: ファイルパス

    Returns:
        ファイルの内容（テキストまたはDataFrame）

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: サポートされていないファイル形式の場合
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

    suffix = path.suffix.lower()

    if suffix in [".txt", ".csv"]:
        detected_encoding = get_file_encoding(path)
        
        # 一般的なエンコーディングを試すリスト
        encodings_to_try = [
            detected_encoding,
            'utf-8',
            'shift_jis',
            'euc_jp',
            'iso2022_jp'
        ]
        # 重複を除き、Noneを除外
        encodings_to_try = [enc for enc in dict.fromkeys(encodings_to_try) if enc]

        for encoding in encodings_to_try:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, TypeError):
                continue
        
        raise ValueError(f"適切なエンコーディングが見つかりませんでした: {path}")

    elif suffix == ".xlsx":
        return pd.read_excel(path)
    else:
        raise ValueError(f"サポートされていないファイル形式です: {suffix}")
