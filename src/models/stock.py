from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union, Dict, Any, Type, TypeVar, List, ClassVar, Set

# PlatformDataの型変数を定義
T = TypeVar('T', bound='PlatformData')


class PlatformData(ABC, BaseModel):
    """プラットフォーム固有データの共通インターフェース"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """データを辞書形式に変換"""
        pass


class TradingViewData(PlatformData):
    """TradingView固有のデータを保持するモデル"""
    section: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """データを辞書形式に変換"""
        return {
            "section": self.section
        }
    
    def to_seeking_alpha(self) -> 'SeekingAlphaData':
        """TradingViewDataからSeekingAlphaDataへの変換"""
        # TradingViewからSeekingAlphaへの変換では情報が失われる
        return SeekingAlphaData()


class SeekingAlphaData(PlatformData):
    """SeekingAlpha固有のデータを保持するモデル"""
    price: Optional[float] = None
    valuation_grade: Optional[str] = None
    profitability_grade: Optional[str] = None
    shares: Optional[float] = None
    cost: Optional[float] = None
    value: Optional[float] = None
    dividend_safety: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """データを辞書形式に変換"""
        return {
            "price": self.price,
            "valuation_grade": self.valuation_grade,
            "profitability_grade": self.profitability_grade,
            "shares": self.shares,
            "cost": self.cost,
            "value": self.value,
            "dividend_safety": self.dividend_safety
        }
    
    def to_trading_view(self) -> TradingViewData:
        """SeekingAlphaDataからTradingViewDataへの変換"""
        # SeekingAlphaからTradingViewへの変換では情報が失われる
        return TradingViewData()


class StockData(BaseModel):
    """統一された株式データモデル"""
    symbol: str = Field(..., description="ティッカーシンボル")
    exchange: Optional[str] = Field(None, description="取引所")
    full_symbol: str = Field(..., description="取引所を含む完全なシンボル")
    name: Optional[str] = Field(None, description="会社名")
    sector: Optional[str] = Field(None, description="セクター")
    industry: Optional[str] = Field(None, description="業種")
    
    # プラットフォーム固有のデータを保持
    platform_data: Union[TradingViewData, SeekingAlphaData] = Field(..., description="プラットフォーム固有のデータ")
    
    # 追加のプラットフォームデータを保持する内部ディクショナリ
    _additional_platform_data: ClassVar[Dict[str, PlatformData]] = {}
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """シンボル名のバリデーション"""
        if not v:
            raise ValueError("シンボルは空にできません")
        return v.upper()  # シンボルは常に大文字に正規化
    
    @field_validator('exchange')
    @classmethod
    def validate_exchange(cls, v: Optional[str]) -> Optional[str]:
        """取引所名のバリデーション"""
        if v is None:
            return None
        return v.upper()  # 取引所名は常に大文字に正規化
    
    @field_validator('platform_data')
    @classmethod
    def validate_platform_data(cls, v: Any) -> Union[TradingViewData, SeekingAlphaData]:
        """プラットフォームデータの型チェック"""
        if not isinstance(v, (TradingViewData, SeekingAlphaData)):
            raise ValueError(f"platform_dataはTradingViewDataまたはSeekingAlphaDataである必要があります。受け取った型: {type(v)}")
        return v
    
    @model_validator(mode='after')
    def normalize_full_symbol(self) -> 'StockData':
        """full_symbolの正規化"""
        if self.exchange and self.symbol:
            # 取引所とシンボルが両方ある場合は、正規化されたfull_symbolを生成
            self.full_symbol = f"{self.exchange}:{self.symbol}"
        elif not self.exchange and self.symbol:
            # 取引所がない場合は、シンボルをそのまま使用
            self.full_symbol = self.symbol
        return self
    
    def convert_platform_data(self, target_class: Type[T]) -> T:
        """プラットフォームデータを別の型に変換"""
        if isinstance(self.platform_data, target_class):
            return self.platform_data
        
        if isinstance(self.platform_data, TradingViewData) and target_class == SeekingAlphaData:
            return self.platform_data.to_seeking_alpha()
        
        if isinstance(self.platform_data, SeekingAlphaData) and target_class == TradingViewData:
            return self.platform_data.to_trading_view()
        
        raise ValueError(f"未サポートの変換: {type(self.platform_data)} -> {target_class}")
    
    def get_platform_data(self, platform_class: Type[T]) -> Optional[T]:
        """特定のプラットフォームデータを取得"""
        if isinstance(self.platform_data, platform_class):
            return self.platform_data
        
        # 追加のプラットフォームデータから検索
        platform_name = platform_class.__name__
        if platform_name in self._additional_platform_data:
            data = self._additional_platform_data[platform_name]
            if isinstance(data, platform_class):
                return data
        
        return None
    
    def add_platform_data(self, data: PlatformData) -> None:
        """追加のプラットフォームデータを設定"""
        platform_name = data.__class__.__name__
        self._additional_platform_data[platform_name] = data
    
    def merge(self, other: 'StockData') -> 'StockData':
        """2つのStockDataオブジェクトをマージ"""
        if self.symbol != other.symbol:
            raise ValueError(f"異なるシンボルのStockDataオブジェクトはマージできません: {self.symbol} != {other.symbol}")
        
        # 基本フィールドのマージ（Noneでない値を優先）
        merged_data = StockData(
            symbol=self.symbol,
            exchange=self.exchange or other.exchange,
            full_symbol=self.full_symbol,  # 正規化されるので、どちらを使っても問題ない
            name=self.name or other.name,
            sector=self.sector or other.sector,
            industry=self.industry or other.industry,
            platform_data=self.platform_data  # 元のプラットフォームデータを維持
        )
        
        # 追加のプラットフォームデータをマージ
        for platform_name, data in self._additional_platform_data.items():
            merged_data.add_platform_data(data)
        
        # 他方のプラットフォームデータを追加
        if not isinstance(other.platform_data, type(self.platform_data)):
            merged_data.add_platform_data(other.platform_data)
        
        # 他方の追加プラットフォームデータをマージ
        for platform_name, data in other._additional_platform_data.items():
            if platform_name not in merged_data._additional_platform_data:
                merged_data.add_platform_data(data)
        
        return merged_data
    
    def __eq__(self, other: object) -> bool:
        """等価性比較"""
        if not isinstance(other, StockData):
            return False
        
        # 基本フィールドの比較
        if (self.symbol != other.symbol or
            self.exchange != other.exchange or
            self.full_symbol != other.full_symbol or
            self.name != other.name or
            self.sector != other.sector or
            self.industry != other.industry):
            return False
        
        # プラットフォームデータの比較
        if type(self.platform_data) != type(other.platform_data):
            return False
        
        # プラットフォームデータの内容比較
        if self.platform_data.to_dict() != other.platform_data.to_dict():
            return False
        
        # 追加のプラットフォームデータの比較
        self_platforms = set(self._additional_platform_data.keys())
        other_platforms = set(other._additional_platform_data.keys())
        
        if self_platforms != other_platforms:
            return False
        
        for platform_name in self_platforms:
            self_data = self._additional_platform_data[platform_name]
            other_data = other._additional_platform_data[platform_name]
            
            if self_data.to_dict() != other_data.to_dict():
                return False
        
        return True
