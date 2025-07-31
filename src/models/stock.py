from pydantic import BaseModel, Field
from typing import Optional, Any

class TradingViewData(BaseModel):
    """TradingView固有のデータを保持するモデル"""
    section: Optional[str] = None

class StockData(BaseModel):
    """統一された株式データモデル"""
    symbol: str = Field(..., description="ティッカーシンボル")
    exchange: Optional[str] = Field(None, description="取引所")
    full_symbol: str = Field(..., description="取引所を含む完全なシンボル")
    
    # プラットフォーム固有のデータを保持
    platform_data: Any = Field(..., description="プラットフォーム固有のデータ")
