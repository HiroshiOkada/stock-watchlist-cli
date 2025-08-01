from abc import ABC, abstractmethod
from typing import List, Union
from pathlib import Path

from src.models.stock import PlatformData

class BaseParser(ABC):
    """
    各種ファイル形式を解析するための抽象基底クラス。
    新しいパーサーを追加する際は、このクラスを継承し、
    parse, validate_format, get_supported_extensions メソッドを実装する。
    """
    
    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> List[PlatformData]:
        """
        ファイルを解析してPlatformDataのリストを返す抽象メソッド。
        各パーサーはこのメソッドを実装し、それぞれのプラットフォーム固有のデータモデルを返す。
        """
        pass
    
    @abstractmethod
    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """
        指定されたファイルがパーサーのサポートする形式であるかを検証する抽象メソッド。
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        パーサーがサポートするファイル拡張子のリストを返す抽象メソッド。
        例: ['.txt', '.csv', '.xlsx']
        """
        pass