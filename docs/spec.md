# 株式ウォッチリスト管理CLI プログラム仕様書

## 1. 概要

### 1.1 プログラムの目的
TradingViewとSeeking Alphaのファイル形式とGoogle Spreadsheetsの間でデータ変換を行うシンプルなコマンドラインツールです。Google Sheetsをデータハブとして活用し、各プラットフォーム間でのウォッチリストデータの相互変換を提供します。

### 1.2 主要機能
- TradingView、Seeking Alphaファイルの読み込み・解析
- プラットフォーム間でのファイル形式変換
- Google Sheetsへのデータインポート・エクスポート
- シンプルなCLIインターフェース

### 1.3 設計方針
- **Google Sheetsがデータハブ**: 全ての管理・分析はGoogle Sheets上で実施
- **CLIは変換ツール**: データ変換とインポート/エクスポートに特化
- **シンプルな構成**: 複雑な管理機能は含めない

### 1.3 対象プラットフォーム
1. **TradingView** - ウォッチリスト機能
2. **Seeking Alpha** - ポートフォリオ機能
3. **Google Spreadsheets** - 統合ハブ

## 2. システム要件

### 2.1 動作環境
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8以上
- **インターネット接続**: Google Sheets API利用のため必須

### 2.2 必要なライブラリ
```python
# 必須パッケージ
pandas>=1.5.0
gspread>=5.7.0
google-auth>=2.15.0
google-auth-oauthlib>=0.8.0
google-auth-httplib2>=0.1.0
click>=8.0.0
openpyxl>=3.0.0
chardet>=5.0.0
pydantic>=1.10.0
```

### 2.3 API要件
- **Google Sheets API v4** - 認証情報の設定が必要
- **Google Drive API v3** - スプレッドシート作成のため

## 3. ファイル形式仕様

### 3.1 TradingView
**ファイル形式**: テキストファイル (.txt)
**エンコード**: UTF-8

**実際のファイル構造**（US_STOCK_012ed.txt分析結果）:

**フォーマット**: 単一行、カンマ区切りの銘柄コード
```text
NASDAQ:AAPL,NASDAQ:AVGO,NYSE:ACN,NASDAQ:AMZN,NASDAQ:BNTX,NASDAQ:CNCK,NASDAQ:CRWD,NASDAQ:DASH,NYSE:GE,NASDAQ:GOOG,NASDAQ:GRAB,NYSE:KD,AMEX:LEU,NYSE:LLY,NASDAQ:LULU,NASDAQ:MAT,NASDAQ:META,NASDAQ:MSFT,NASDAQ:MSTR,NASDAQ:NTAP,NASDAQ:NVDA,NYSE:NVO,NASDAQ:PLTR,NYSE:PSTG,NASDAQ:PYPL,NASDAQ:QCOM,NYSE:SHOP,NYSE:SMR,NYSE:TOST,NASDAQ:TSLA,NYSE:TSM,NYSE:U,NYSE:WHR,###SECTION 1,###SECTION 2,NASDAQ:NBIS,NYSE:BRK.B,NASDAQ:ASTS
```

**重要な特徴**:
1. **取引所プレフィックス**: 必須（EXCHANGE:SYMBOL形式）
2. **セクション区切り機能**: `###SECTION N` でウォッチリストを論理的に分割可能
3. **特殊シンボル対応**: ドット付きシンボル（例：`NYSE:BRK.B`）に対応
4. **複数取引所対応**: NASDAQ、NYSE、AMEX等

**取引所プレフィックス一覧**:
- `NASDAQ:` - NASDAQ証券取引所
- `NYSE:` - ニューヨーク証券取引所  
- `AMEX:` - アメリカン証券取引所
- `TSE:` - 東京証券取引所（日本株の場合）

**分析結果（US_STOCK_012ed.txtより）**:
- 総銘柄数: 36銘柄
- NASDAQ: 22銘柄（61%）
- NYSE: 13銘柄（36%）
- AMEX: 1銘柄（3%）
- セクション区切り: 2個

### 3.2 Seeking Alpha
**エクスポート形式**: Excel (.xlsx) - 4シート構成
**インポート形式**: CSV（限定的）

**実際のファイル構造**（UsStock 2025-07-30.xlsx分析結果）:

#### シート1: Summary（サマリー情報）
```
Symbol | Price | Change | Change % | Volume | Avg. Vol | Prev Close | Open | Day Low | Day High | 52W Low | 52W High | Quant Rating | SA Analyst Ratings | Wall Street Ratings
```
**データ例**:
```
AAPL | 211.27 | -2.78 | -0.01299 | 87860 | 53264601.76 | 214.05 | 214.175 | 210.82 | 214.81 | 169.21 | 260.1 | 3.32 | 2.94 | 4.0
```

#### シート2: Ratings（レーティング詳細）
```
Symbol | Quant Score | SA Analysts Score | Wall St. Score | Valuation Grade | Growth Grade | Profitability Grade | Momentum Grade | EPS Revision Grade | ETF Momentum | ETF Expenses | ETF Dividends | ETF Risk | ETF Liquidity
```
**データ例**:
```
AAPL | 3.32 | 2.94 | 4.0 | F | D | A+ | C- | D+ | - | - | - | - | -
```

#### シート3: Holdings（保有情報）
```
Symbol | Price | Change | Change % | Shares | Cost | Today's Gain | Today's % Gain | Est Annual Income | Total Change | Total % Change | Value
```
**注意**: Shares、Cost、Value等の保有関連データは通常空（"-"）の状態でエクスポートされる

#### シート4: Dividends（配当情報）
```
Symbol | Safety | Growth | Yield | Consistency | Ex-Div Date | Payout Date | Frequency | Est Annual Income | Yield TTM | Yield FWD | 4Y Avg Yield | Div Rate TTM | Div Rate FWD | Payout Ratio | 4Y Avg Payout | Div Growth 3Y | Div Growth 5Y | Years of Growth | Consecutive Years | 24M Beta
```
**データ例**:
```
AAPL | A | A+ | D | B- | 5/12/2025 | 5/15/2025 | Quarterly | - | 0.00478 | 0.00492 | 0.00525 | 1.01 | 1.04 | 0.141 | 0.149 | 0.043 | 0.052 | 12 Years | 12 Years | 1.102
```

**CSVインポート形式**（従来通り）:
```csv
Symbol,Quantity,Cost,Date
AAPL,100,150.50,2024-01-15
TSLA,50,250.75,2024-01-16
MSFT,75,300.25,2024-01-17
```

### 3.3 Google Spreadsheets (データハブ)
**フォーマット**: シンプルな統合スキーマ（管理はGoogle Sheets上で実施）

#### メインデータシート
```
A列: Symbol (銘柄コード)
B列: Exchange (取引所)
C列: Company_Name (会社名)
D列: Current_Price (現在価格)
E列: Source_Platform (データソース)
F列: TradingView_Section (セクション名)
G列: Quant_Rating (Quantレーティング)
H列: SA_Analyst_Rating (SA アナリストレーティング)
I列: Valuation_Grade (バリュエーショングレード)
J列: Dividend_Safety (配当安全性)
K列: Yield_TTM (配当利回り)
L列: Date_Updated (更新日)
M列: Notes (メモ)
```

**設計方針**: 
- 単一シートに全ての重要データを集約
- Google Sheetsの機能（ピボットテーブル、フィルタ、グラフ等）で管理・分析
- CLIは変換とデータ同期のみを担当

## 4. プログラム構造

### 4.1 ディレクトリ構成
```
stock_watchlist_cli/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLIエントリーポイント
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # 設定管理
│   │   └── credentials.py      # 認証情報管理
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py      # 基底パーサークラス
│   │   ├── tradingview_parser.py # TradingViewパーサー
│   │   └── seekingalpha_parser.py # Seeking Alphaパーサー
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── format_converter.py # フォーマット変換
│   │   └── markdown_formatter.py # Markdown出力（LLM用）
│   ├── google_sheets/
│   │   ├── __init__.py
│   │   ├── auth.py            # Google認証（OAuth2対応）
│   │   ├── client.py          # Sheetsクライアント
│   │   └── operations.py      # 基本的なCRUD操作
│   ├── models/
│   │   ├── __init__.py
│   │   ├── stock_data.py      # データモデル
│   │   └── exceptions.py      # カスタム例外
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py      # ファイル操作
│       └── logging_config.py  # ログ設定
├── tests/
│   ├── __init__.py
│   ├── test_parsers.py
│   ├── test_converters.py
│   ├── test_google_sheets.py
│   └── sample_data/           # テスト用サンプルファイル
├── docs/
│   ├── README.md
│   └── SETUP.md              # セットアップガイド
├── config/
│   └── config.yaml           # 設定ファイル
├── requirements.txt
├── setup.py
└── .env.example              # 環境変数テンプレート
```

### 4.2 主要クラス設計

#### 4.2.1 Google認証管理 (google_sheets/auth.py)
```python
import gspread
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Optional
import json
import logging

class GoogleSheetsAuth:
    """Google Sheets認証管理クラス（提供いただいたコードを改良）"""
    
    def __init__(self, 
                 credentials_file: str = "credentials.json",
                 token_file: str = "token.json",
                 port: int = 8080):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.port = port
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.logger = logging.getLogger(__name__)
    
    def get_credentials(self) -> Credentials:
        """認証情報を取得（既存トークンの再利用対応）"""
        creds = None
        
        # 既存のトークンファイルをチェック
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_file), self.scopes
                )
                self.logger.info("既存の認証トークンを読み込みました")
            except Exception as e:
                self.logger.warning(f"既存トークンの読み込みに失敗: {e}")
        
        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("認証トークンを更新しました")
                except Exception as e:
                    self.logger.warning(f"トークン更新に失敗: {e}")
                    creds = None
            
            if not creds:
                creds = self._perform_oauth_flow()
        
        # 認証情報を保存
        self._save_credentials(creds)
        return creds
    
    def _perform_oauth_flow(self) -> Credentials:
        """OAuth認証フローを実行"""
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"認証ファイルが見つかりません: {self.credentials_file}"
            )
        
        self.logger.info("OAuth認証フローを開始します")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_file), self.scopes
        )
        
        # ローカルサーバーでの認証
        creds = flow.run_local_server(port=self.port)
        self.logger.info("OAuth認証が完了しました")
        return creds
    
    def _save_credentials(self, creds: Credentials) -> None:
        """認証情報をファイルに保存"""
        try:
            with open(self.token_file, "w") as token_file:
                token_file.write(creds.to_json())
            self.logger.info(f"認証情報を保存しました: {self.token_file}")
        except Exception as e:
            self.logger.error(f"認証情報の保存に失敗: {e}")
            raise
    
    def get_gspread_client(self) -> gspread.Client:
        """gspreadクライアントを取得"""
        creds = self.get_credentials()
        client = gspread.authorize(creds)
        self.logger.info("Google Sheetsクライアントを作成しました")
        return client
    
    def revoke_credentials(self) -> None:
        """認証情報を削除（再認証強制用）"""
        if self.token_file.exists():
            self.token_file.unlink()
            self.logger.info("認証情報を削除しました")

#### 4.2.2 Sheetsクライアント (google_sheets/client.py)
```python
import gspread
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .auth import GoogleSheetsAuth
from models.stock_data import StockData

class GoogleSheetsClient:
    """Google Sheetsクライアント"""
    
    def __init__(self, auth: GoogleSheetsAuth):
        self.auth = auth
        self.client = auth.get_gspread_client()
        self.logger = logging.getLogger(__name__)
    
    def create_spreadsheet(self, name: str) -> str:
        """新しいスプレッドシートを作成（提供コードを改良）"""
        try:
            spreadsheet = self.client.create(name)
            spreadsheet_id = spreadsheet.id
            self.logger.info(f"スプレッドシート作成完了: {name} (ID: {spreadsheet_id})")
            
            # 初期ヘッダーを設定
            self._setup_initial_headers(spreadsheet_id)
            return spreadsheet_id
            
        except Exception as e:
            self.logger.error(f"スプレッドシート作成に失敗: {e}")
            raise
    
    def _setup_initial_headers(self, spreadsheet_id: str) -> None:
        """初期ヘッダーを設定"""
        headers = [
            "ID", "Symbol", "Company_Name", "Exchange", "Sector",
            "Source_Platform", "Quantity", "Cost", "Date_Added",
            "Date_Updated", "Notes", "Status"
        ]
        
        worksheet = self.client.open_by_key(spreadsheet_id).sheet1
        worksheet.update('A1:L1', [headers])
        self.logger.info("初期ヘッダーを設定しました")

#### 4.2.3 データモデル (models/stock_data.py)
```python
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Literal

class StockData(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    source_platform: Literal["rakuten", "tradingview", "seekingalpha"]
    quantity: Optional[float] = None
    cost: Optional[float] = None
    date_added: datetime
    date_updated: datetime
    notes: Optional[str] = None
    status: Literal["active", "inactive"] = "active"
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Symbol cannot be empty')
        return v.strip().upper()
```

#### 4.2.3 TradingViewパーサー (parsers/tradingview_parser.py)
```python
import re
from typing import List, Dict, Tuple
from datetime import datetime
from models.stock_data import StockData, TradingViewData
from .base_parser import BaseParser

class TradingViewParser(BaseParser):
    """TradingView テキストファイルパーサー（セクション対応）"""
    
    def __init__(self):
        self.supported_exchanges = ['NASDAQ', 'NYSE', 'AMEX', 'TSE', 'LSE', 'FRA']
        self.section_pattern = r'^###SECTION\s+(.+)
```python
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from models.stock_data import StockData, SeekingAlphaData
from .base_parser import BaseParser

class SeekingAlphaParser(BaseParser):
    """Seeking Alpha Excelファイルパーサー（4シート対応）"""
    
    def __init__(self):
        self.required_sheets = ['Summary', 'Ratings', 'Holdings', 'Dividends']
    
    def parse(self, file_path: str) -> List[SeekingAlphaData]:
        """4シート構成のExcelファイルを解析"""
        try:
            # 全シートを読み込み
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # 必要なシートの存在確認
            missing_sheets = [sheet for sheet in self.required_sheets 
                            if sheet not in excel_data.keys()]
            if missing_sheets:
                raise ValueError(f"必要なシートが見つかりません: {missing_sheets}")
            
            # 各シートのデータを統合
            symbols = self._get_symbols_list(excel_data)
            seeking_alpha_data = []
            
            for symbol in symbols:
                data = self._parse_symbol_data(symbol, excel_data)
                seeking_alpha_data.append(data)
            
            return seeking_alpha_data
            
        except Exception as e:
            raise ValueError(f"Seeking Alphaファイルの解析に失敗: {e}")
    
    def _get_symbols_list(self, excel_data: Dict) -> List[str]:
        """全シートから銘柄シンボルのリストを取得"""
        summary_df = excel_data['Summary']
        if 'Symbol' in summary_df.columns:
            return summary_df['Symbol'].dropna().tolist()
        else:
            raise ValueError("Summaryシートに'Symbol'列が見つかりません")
    
    def _parse_symbol_data(self, symbol: str, excel_data: Dict) -> SeekingAlphaData:
        """特定銘柄のデータを4シートから統合"""
        data = SeekingAlphaData(symbol=symbol)
        
        # Summaryシートからデータ取得
        summary_df = excel_data['Summary']
        summary_row = summary_df[summary_df['Symbol'] == symbol]
        if not summary_row.empty:
            row = summary_row.iloc[0]
            data.price = self._safe_float(row.get('Price'))
            data.change = self._safe_float(row.get('Change'))
            data.change_percent = self._safe_float(row.get('Change %'))
            data.volume = self._safe_int(row.get('Volume'))
            data.avg_volume = self._safe_float(row.get('Avg. Vol'))
            data.day_low = self._safe_float(row.get('Day Low'))
            data.day_high = self._safe_float(row.get('Day High'))
            data.week52_low = self._safe_float(row.get('52W Low'))
            data.week52_high = self._safe_float(row.get('52W High'))
            data.quant_rating = self._safe_float(row.get('Quant Rating'))
            data.sa_analyst_rating = self._safe_float(row.get('SA Analyst Ratings'))
            data.wall_street_rating = self._safe_float(row.get('Wall Street Ratings'))
        
        # Ratingsシートからデータ取得
        ratings_df = excel_data['Ratings']
        ratings_row = ratings_df[ratings_df['Symbol'] == symbol]
        if not ratings_row.empty:
            row = ratings_row.iloc[0]
            data.valuation_grade = self._safe_str(row.get('Valuation Grade'))
            data.growth_grade = self._safe_str(row.get('Growth Grade'))
            data.profitability_grade = self._safe_str(row.get('Profitability Grade'))
            data.momentum_grade = self._safe_str(row.get('Momentum Grade'))
            data.eps_revision_grade = self._safe_str(row.get('EPS Revision Grade'))
        
        # Holdingsシートからデータ取得
        holdings_df = excel_data['Holdings']
        holdings_row = holdings_df[holdings_df['Symbol'] == symbol]
        if not holdings_row.empty:
            row = holdings_row.iloc[0]
            data.shares = self._safe_float(row.get('Shares'))
            data.cost = self._safe_float(row.get('Cost'))
            data.todays_gain = self._safe_float(row.get("Today's Gain"))
            data.todays_gain_percent = self._safe_float(row.get("Today's % Gain"))
            data.total_change = self._safe_float(row.get('Total Change'))
            data.total_change_percent = self._safe_float(row.get('Total % Change'))
            data.value = self._safe_float(row.get('Value'))
        
        # Dividendsシートからデータ取得
        dividends_df = excel_data['Dividends']
        dividends_row = dividends_df[dividends_df['Symbol'] == symbol]
        if not dividends_row.empty:
            row = dividends_row.iloc[0]
            data.dividend_safety = self._safe_str(row.get('Safety'))
            data.dividend_growth = self._safe_str(row.get('Growth'))
            data.dividend_yield_grade = self._safe_str(row.get('Yield'))
            data.dividend_consistency = self._safe_str(row.get('Consistency'))
            data.ex_dividend_date = self._safe_date(row.get('Ex-Div Date'))
            data.payout_date = self._safe_date(row.get('Payout Date'))
            data.frequency = self._safe_str(row.get('Frequency'))
            data.yield_ttm = self._safe_float(row.get('Yield TTM'))
            data.yield_forward = self._safe_float(row.get('Yield FWD'))
            data.dividend_rate_ttm = self._safe_float(row.get('Div Rate TTM'))
            data.dividend_rate_forward = self._safe_float(row.get('Div Rate FWD'))
            data.payout_ratio = self._safe_float(row.get('Payout Ratio'))
            data.dividend_growth_3y = self._safe_float(row.get('Div Growth 3Y'))
            data.dividend_growth_5y = self._safe_float(row.get('Div Growth 5Y'))
            data.beta_24m = self._safe_float(row.get('24M Beta'))
        
        return data
    
    def _safe_float(self, value) -> Optional[float]:
        """安全なfloat変換（'-'や空値を処理）"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """安全なint変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_str(self, value) -> Optional[str]:
        """安全なstring変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        return str(value).strip()
    
    def _safe_date(self, value) -> Optional[str]:
        """安全な日付変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            # M/D/YYYY形式をYYYY-MM-DD形式に変換
            if isinstance(value, str) and '/' in value:
                parts = value.split('/')
                if len(parts) == 3:
                    month, day, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return str(value)
        except:
            return None
    
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)
            # 必要なシートが存在するかチェック
            return all(sheet in excel_data.keys() for sheet in self.required_sheets)
        except:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子"""
        return ['.xlsx', '.xls']
```

#### 4.2.5 拡張データモデル (models/stock_data.py)
```python
from abc import ABC, abstractmethod
from typing import List
from models.stock_data import StockData

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> List[StockData]:
        """ファイルを解析してStockDataのリストを返す"""
        pass
    
    @abstractmethod
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子を返す"""
        pass
```

## 5. 機能仕様

### 5.1 基本コマンド

#### 5.1.1 ファイル変換（実データ対応）
```bash
# TradingView → Seeking Alpha（実際のファイル例）
stock-cli convert \
  --from tradingview \
  --to seekingalpha \
  --input "US_STOCK_012ed.txt" \
  --output portfolio.csv \
  --preserve-sections

# Seeking Alpha → TradingView（セクション付き）
stock-cli convert \
  --from seekingalpha \
  --to tradingview \
  --input "UsStock 2025-07-30.xlsx" \
  --output tradingview_list.txt \
  --create-sections-by-sector

# TradingView → Google Sheets（セクション情報保持）
stock-cli convert \
  --from tradingview \
  --to googlesheets \
  --input "US_STOCK_012ed.txt" \
  --spreadsheet-id "your_sheet_id" \
  --import-sections

# セクションのみを抽出
stock-cli convert \
  --from tradingview \
  --to tradingview \
  --input "US_STOCK_012ed.txt" \
  --output filtered_list.txt \
  --section "SECTION 1" \
  --exclude-sections
```

#### 5.1.2 TradingView特化コマンド（新規追加）
```bash
# セクション情報の表示
stock-cli tradingview analyze \
  --file "US_STOCK_012ed.txt" \
  --show-sections \
  --show-stats

# セクション別分割エクスポート
stock-cli tradingview split \
  --input "US_STOCK_012ed.txt" \
  --output-dir "./sections/" \
  --format individual-files

# 取引所別統計
stock-cli tradingview stats \
  --file "US_STOCK_012ed.txt" \
  --group-by exchange \
  --output stats.json

# セクションの結合
stock-cli tradingview merge \
  --input-dir "./sections/" \
  --output "merged_watchlist.txt" \
  --add-section-markers

# 重複チェック・クリーンアップ
stock-cli tradingview cleanup \
  --input "US_STOCK_012ed.txt" \
  --remove-duplicates \
  --validate-symbols \
  --output cleaned_list.txt
```

#### 5.1.2 Google Sheets操作（Seeking Alpha拡張対応）
```bash
# 新規スプレッドシート作成（4シート構成）
stock-cli sheets create --name "My Stock Portfolio" --template seekingalpha-full

# Seeking Alphaファイルのインポート（4シート対応）
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-id "sheet_id" \
  --preserve-all-data

# 特定シートのみインポート
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --sheets "Summary,Holdings" \
  --spreadsheet-id "sheet_id"

# データのエクスポート（シート別）
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --sheet "Holdings" \
  --format tradingview \
  --output exported_list.txt

# 全データの統合エクスポート
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --format seekingalpha-summary \
  --output portfolio_summary.xlsx

# 詳細データ分析（Seeking Alphaデータ活用）
stock-cli analyze \
  --spreadsheet-id "sheet_id" \
  --metric "dividend_yield" \
  --top 10 \
  --output analysis_report.csv

# データの同期（高度な設定）
stock-cli sheets sync \
  --local-file "UsStock 2025-07-30.xlsx" \
  --spreadsheet-id "sheet_id" \
  --mode seekingalpha-full \
  --preserve-ratings \
  --update-prices-only
```

#### 5.1.3 データ分析コマンド（新規追加）
```bash
# レーティング分析
stock-cli analyze ratings \
  --spreadsheet-id "sheet_id" \
  --filter "quant_rating>4.0" \
  --sort "sa_analyst_rating desc"

# 配当分析
stock-cli analyze dividends \
  --spreadsheet-id "sheet_id" \
  --min-yield 0.02 \
  --safety-grade "A,B" \
  --output dividend_candidates.xlsx

# ポートフォリオパフォーマンス分析
stock-cli analyze performance \
  --spreadsheet-id "sheet_id" \
  --period "1M,3M,6M" \
  --benchmark "SPY" \
  --output performance_report.pdf

# バリュエーション分析
stock-cli analyze valuation \
  --spreadsheet-id "sheet_id" \
  --metrics "PE,PB,PEG" \
  --sector-comparison \
  --output valuation_analysis.xlsx
```

#### 5.1.3 バッチ処理
```bash
# 複数ファイルの一括変換
stock-cli batch convert --config batch_config.yaml

# 定期同期設定
stock-cli schedule sync --interval daily --time "09:00" --config sync_config.yaml
```

### 5.2 設定管理

#### 5.2.1 初期設定
```bash
# Google認証の設定
stock-cli setup google-auth --credentials-file credentials.json

# デフォルト設定の構成
stock-cli config init

# 設定の確認
stock-cli config show
```

#### 5.2.2 設定ファイル (config/config.yaml)
```yaml
google_sheets:
  credentials_file: "credentials.json"  # OAuth2クライアント認証情報ファイル
  token_file: "token.json"             # 保存される認証トークン
  oauth_port: 8080                     # OAuth認証用ローカルサーバーポート
  default_spreadsheet_id: ""
  sheet_name: "Stock_Data"
  batch_size: 100

platforms:
  tradingview:
    encoding: "utf-8"
    include_exchange_prefix: true
  seekingalpha:
    default_quantity: 0
    default_cost: 0.0

logging:
  level: "INFO"
  file: "stock_cli.log"
  max_size: "10MB"
  backup_count: 5

conversion:
  symbol_mapping_file: "symbol_mapping.json"
  auto_detect_exchange: true
  fallback_exchange: "NASDAQ"
```

### 5.3 Google認証セットアップ

#### 5.3.1 初回セットアップ手順
```bash
# 1. Google Cloud Consoleでプロジェクト作成
# 2. Google Sheets API、Google Drive APIを有効化
# 3. OAuth2.0クライアントIDを作成（デスクトップアプリケーション）
# 4. credentials.jsonをダウンロード

# 5. CLIで初回認証
stock-cli auth setup --credentials-file credentials.json

# 6. ブラウザが開かれるので認証を完了
# 7. token.jsonが自動生成される
```

#### 5.3.2 認証管理コマンド
```bash
# 認証状態の確認
stock-cli auth status

# 認証情報の更新（再認証）
stock-cli auth refresh

# 認証情報の削除（再認証強制）
stock-cli auth revoke

# 認証設定の変更
stock-cli auth configure --port 8080 --credentials-file new_credentials.json
```

## 6. エラーハンドリング

### 6.1 カスタム例外クラス
```python
class StockCliError(Exception):
    """基底例外クラス"""
    pass

class FileFormatError(StockCliError):
    """ファイル形式エラー"""
    pass

class GoogleSheetsError(StockCliError):
    """Google Sheets API関連エラー"""
    pass

class ConversionError(StockCliError):
    """変換処理エラー"""
    pass

class ValidationError(StockCliError):
    """データ検証エラー"""
    pass
```

### 6.2 エラー処理方針
- **ファイル読み込みエラー**: 詳細なエラーメッセージと修正提案を表示
- **API接続エラー**: リトライ機能付きで自動復旧を試行
- **データ変換エラー**: 問題のあるレコードをスキップし、処理を継続
- **認証エラー**: 再認証フローを案内

## 7. セキュリティ要件

### 7.1 OAuth2認証の管理
- **OAuth2フロー**: デスクトップアプリケーション用のOAuth2.0を使用
- **トークン管理**: アクセストークンとリフレッシュトークンの自動管理
- **認証情報保存**: token.jsonファイルでローカル保存（適切なファイル権限設定）
- **自動更新**: リフレッシュトークンによる自動アクセストークン更新
- **認証スコープ**: 最小限必要なスコープのみ使用
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`

### 7.2 認証ファイルの管理
```python
# 推奨ファイル権限設定
credentials.json: 600 (所有者のみ読み書き)
token.json: 600 (所有者のみ読み書き)
```

### 7.3 データ保護
- 一時ファイルの安全な削除
- ログファイルに認証情報や機密データを記録しない
- エラーメッセージでの機密情報露出防止
- Google Sheets APIレート制限の遵守

### 7.4 認証エラー処理
```python
# 認証エラー時の自動対応
if token_expired:
    try_refresh_token()
elif token_invalid:
    request_new_authorization()
elif api_quota_exceeded:
    implement_exponential_backoff()
```

## 8. パフォーマンス要件

### 8.1 処理能力
- **小規模**: 100銘柄未満 - 5秒以内
- **中規模**: 1,000銘柄未満 - 30秒以内
- **大規模**: 10,000銘柄未満 - 5分以内

### 8.2 最適化手法
- バッチ処理による効率化
- Google Sheets APIのレート制限対応
- メモリ効率的なデータ処理

## 9. テスト要件

### 9.1 テスト種別
- **単体テスト**: 各パーサー・コンバーターの動作確認
- **統合テスト**: API連携とファイル変換の確認
- **E2Eテスト**: CLI操作全体の動作確認

### 9.2 テストデータ
基本的な変換機能の検証用サンプルファイル:

#### TradingViewサンプル（US_STOCK_012ed.txt）
- **36銘柄**: NASDAQ(22), NYSE(13), AMEX(1) 
- **セクション機能**: `###SECTION 1`, `###SECTION 2`
- **特殊シンボル**: `NYSE:BRK.B`（ドット付きシンボル）

#### Seeking Alphaサンプル（UsStock 2025-07-30.xlsx）
- **4シート構成**: Summary、Ratings、Holdings、Dividends
- **30銘柄**: 詳細な投資データ
- **共通銘柄**: TradingViewと重複する銘柄で統合テスト

#### テストケース設計
1. **基本変換テスト**
   - TradingView → Google Sheets
   - Seeking Alpha → Google Sheets  
   - Google Sheets → TradingView
   - Google Sheets → Seeking Alpha CSV
   - Google Sheets → Markdown（各テンプレート）

2. **データ統合テスト**
   - 重複銘柄のマージ処理
   - セクション情報の保持
   - 異なるプラットフォームデータの統合

3. **Markdown出力テスト**
   - 標準形式の出力確認
   - LLMレポート形式の構造確認
   - コンパクト形式の可読性確認
   - テーブル形式の正確性確認

4. **エラーハンドリングテスト**
   - 不正なファイル形式
   - 空ファイル
   - ネットワークエラー（Google Sheets API）

**テスト方針**: シンプルな変換機能の確実性を重視、Markdown出力のLLM適合性も検証

## 10. 拡張性

### 10.1 プラットフォーム追加
新しいプラットフォーム対応時の拡張ポイント:
- パーサークラスの追加実装
- フォーマット変換ロジックの追加
- 設定ファイルへの新プラットフォーム情報追加

### 10.2 機能拡張予定
- **フェーズ2**: バッチ処理機能の追加
- **フェーズ3**: 自動同期スケジューリング
- **フェーズ4**: Markdown出力テンプレートの拡張（業界別レポート、リスク分析等）
- **フェーズ5**: 追加プラットフォーム対応（要望ベース）
- **フェーズ6**: GUI版の検討

**注意**: 分析・管理機能の拡張は予定していません（Google Sheetsで実施）

### 10.3 Markdown出力機能の活用例
```bash
# ChatGPTなどのLLMへの入力用
stock-cli export --spreadsheet-id "sheet_id" --format markdown --template compact --output prompt.md

# 投資分析レポート用
stock-cli export --spreadsheet-id "sheet_id" --format markdown --template llm-report --include-summary --output analysis.md

# 簡易ドキュメント用
stock-cli export --spreadsheet-id "sheet_id" --format markdown --template table-only --output summary.md
```

## 11. デプロイメント

### 11.1 インストール方法
```bash
# PyPIからのインストール
pip install stock-watchlist-cli

# ソースからのインストール
git clone https://github.com/username/stock-watchlist-cli.git
cd stock-watchlist-cli
pip install -e .
```

### 11.2 設定ファイルの初期化
```bash
# 初期設定
stock-cli setup init

# Google認証設定（提供いただいたフローを改良）
stock-cli auth setup --credentials-file credentials.json
# -> ブラウザが開かれ、OAuth認証フローが開始されます
# -> 認証完了後、token.jsonが自動生成されます

# 認証状態の確認
stock-cli auth status

# 設定確認
stock-cli config show
```

### 11.3 実使用例
```bash
# 1. 初回セットアップ
stock-cli auth setup --credentials-file credentials.json

# 2. TradingViewファイルをGoogle Sheetsにインポート
stock-cli import \
  --file "US_STOCK_012ed.txt" \
  --format tradingview \
  --spreadsheet-name "My Watchlist"

# 3. Seeking AlphaファイルをGoogle Sheetsに追加
stock-cli import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-id "1abc...xyz"

# 4. Google SheetsからTradingView形式でエクスポート
stock-cli export \
  --spreadsheet-id "1abc...xyz" \
  --format tradingview \
  --output my_watchlist.txt

# 5. Google SheetsからMarkdown形式でエクスポート（LLM用）
stock-cli export \
  --spreadsheet-id "1abc...xyz" \
  --format markdown \
  --output portfolio_analysis.md \
  --template llm-report \
  --include-summary

# 6. 定期的な同期
stock-cli sync \
  --file "US_STOCK_012ed.txt" \
  --spreadsheet-id "1abc...xyz"

# 7. ファイル形式変換
stock-cli convert \
  --from seekingalpha \
  --to tradingview \
  --input "UsStock 2025-07-30.xlsx" \
  --output converted_list.txt
```

### 11.4 Markdown出力サンプル

#### 標準形式（--template standard）
```markdown
# Stock Portfolio Data
*Generated on 2025-07-30 14:30:15*

## Summary
- **Total Stocks**: 5
- **Exchanges**: NASDAQ, NYSE
- **Source Platforms**: TradingView, Seeking Alpha

## Stock Details
| Symbol | Exchange | Price | Quant Rating | Valuation | Dividend Safety | Yield |
| --- | --- | --- | --- | --- | --- | --- |
| AAPL | NASDAQ | $211.27 | 3.32 | F | A | 0.48% |
| AMZN | NASDAQ | $231.01 | 4.86 | D | N/A | N/A |
| MSFT | NASDAQ | $420.55 | 4.12 | C | A | 0.73% |
| NVDA | NASDAQ | $125.61 | 4.85 | D+ | N/A | 0.03% |
| TSLA | NASDAQ | $248.50 | 3.45 | F | N/A | N/A |
```

#### LLMレポート形式（--template llm-report）
```markdown
# Investment Portfolio Analysis Report
*Analysis Date: 2025-07-30*

## Executive Summary
Portfolio contains **5 stocks** across multiple exchanges.
**Exchange Distribution:** NASDAQ: 5
**Average Quant Rating:** 4.12
**Dividend-paying stocks:** 3 (60.0%)

## Detailed Holdings

### AAPL - Apple Inc.

**Basic Information:**
- Exchange: NASDAQ
- Current Price: $211.27
- Source: Seeking Alpha

**Ratings & Analysis:**
- Quant Rating: 3.32
- SA Analyst Rating: 2.94
- Valuation Grade: F
- Dividend Safety: A

**Dividend Information:**
- Yield (TTM): 0.48%
- Safety Grade: A

---

### AMZN - Amazon.com Inc.

**Basic Information:**
- Exchange: NASDAQ
- Current Price: $231.01
- Source: Seeking Alpha

**Ratings & Analysis:**
- Quant Rating: 4.86
- SA Analyst Rating: 4.09
- Valuation Grade: D

---
```

#### コンパクト形式（--template compact）
```markdown
# Portfolio Summary

- **AAPL** (NASDAQ) - $211.27 - Rating: 3.32
- **AMZN** (NASDAQ) - $231.01 - Rating: 4.86
- **MSFT** (NASDAQ) - $420.55 - Rating: 4.12
- **NVDA** (NASDAQ) - $125.61 - Rating: 4.85
- **TSLA** (NASDAQ) - $248.50 - Rating: 3.45
```

### 11.5 データフロー例
```
TradingView File (US_STOCK_012ed.txt)
    ↓ import
Google Sheets (統合データハブ)
    ↓ 手動で分析・管理
Google Sheets (更新されたデータ)  
    ↓ export
TradingView File (更新版)

Seeking Alpha File (UsStock 2025-07-30.xlsx)
    ↓ import (merge)
Google Sheets (統合データハブ)
    ↓ export
Seeking Alpha CSV (フィルタ後)

# LLM連携フロー（おまけ機能）
Google Sheets (統合データハブ)
    ↓ export markdown
Markdown File (portfolio_analysis.md)
    ↓ 手動でコピー
LLM (ChatGPT, Claude等)
    ↓ 分析結果
投資判断・レポート作成
```

## 12. 保守・運用

### 12.1 ログ管理
- 処理ログの記録 (INFO, WARNING, ERROR)
- パフォーマンスメトリクスの収集
- エラー発生時の詳細情報記録

### 12.2 更新・メンテナンス
- 依存ライブラリの定期更新
- APIの仕様変更への対応
- ユーザーフィードバックの収集と対応

## 13. ドキュメント

### 13.1 ユーザーマニュアル
- インストールガイド
- 基本的な使用方法
- トラブルシューティング
- FAQ

### 13.2 開発者ドキュメント
- API仕様書
- 拡張開発ガイド
- コードスタイルガイド
- 貢献ガイドライン

---

## 付録

### A. 銘柄コード統一ルール
各プラットフォーム間での銘柄コード統一基準:

| プラットフォーム | 表記例 | 統一形式 |
|---|---|---|
| TradingView | TSE:7203 | TSE:7203 |
| TradingView | NASDAQ:AAPL | NASDAQ:AAPL |
| Seeking Alpha | AAPL | NASDAQ:AAPL |
| Seeking Alpha | TM | NYSE:TM |

### B. サポート対象市場
- **米国**: NYSE、NASDAQ、AMEX
- **日本**: 東証プライム、東証スタンダード、東証グロース（TradingView経由）
- **その他**: 主要な海外市場（要望に応じて追加）

### D. Google Cloud Console設定手順

#### OAuth2.0クライアントID作成手順:
1. **プロジェクト作成**: Google Cloud Consoleで新しいプロジェクト作成
2. **API有効化**: 
   - Google Sheets API
   - Google Drive API
3. **OAuth同意画面設定**: 
   - アプリケーション名設定
   - 承認済みドメイン設定（localhost含む）
4. **認証情報作成**: 
   - 「デスクトップアプリケーション」を選択
   - credentials.jsonをダウンロード
5. **スコープ設定**: 必要最小限のスコープを設定

#### ファイル構成例:
```
project_root/
├── credentials.json     # OAuth2クライアント認証情報
├── token.json          # 生成される認証トークン（自動作成）
├── config.yaml         # アプリケーション設定
└── stock_cli.log       # ログファイル
```

### C. 想定される課題と対策
1. **API制限**: Google Sheets APIの利用制限
   - 対策: バッチ処理とリトライ機能
2. **認証エラー**: OAuth認証の失敗や期限切れ
   - 対策: 自動リフレッシュ機能と再認証フロー
3. **ファイル形式の変更**: 各プラットフォームの仕様変更
   - 対策: 柔軟なパーサー設計と定期的な検証
4. **データ互換性**: プラットフォーム間での情報の違い
   - 対策: 共通フィールドのマッピングと欠損データの適切な処理
5. **ネットワークエラー**: インターネット接続の問題
   - 対策: 接続確認とエラー時の適切な通知

**設計方針**: Google Sheetsで管理・分析するため、CLIは変換の確実性に集中

この仕様書は開発進行に合わせて継続的に更新されます。
    
    def parse(self, file_path: str) -> List[TradingViewData]:
        """TradingViewテキストファイルを解析（セクション機能対応）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            # カンマで分割
            elements = [elem.strip() for elem in content.split(',') if elem.strip()]
            
            # セクションと銘柄を分離
            sections, stocks = self._parse_elements(elements)
            
            # TradingViewDataオブジェクトのリストを作成
            trading_view_data = []
            current_section = "Default"
            
            for element in elements:
                if self._is_section(element):
                    current_section = self._extract_section_name(element)
                elif self._is_valid_symbol(element):
                    data = self._parse_symbol(element, current_section)
                    trading_view_data.append(data)
            
            return trading_view_data
            
        except Exception as e:
            raise ValueError(f"TradingViewファイルの解析に失敗: {e}")
    
    def _parse_elements(self, elements: List[str]) -> Tuple[List[str], List[str]]:
        """要素をセクションと銘柄に分離"""
        sections = [elem for elem in elements if self._is_section(elem)]
        stocks = [elem for elem in elements if self._is_valid_symbol(elem)]
        return sections, stocks
    
    def _is_section(self, element: str) -> bool:
        """セクション区切りかどうかを判定"""
        return element.startswith('###SECTION')
    
    def _extract_section_name(self, element: str) -> str:
        """セクション名を抽出"""
        match = re.match(self.section_pattern, element)
        return match.group(1) if match else "Unknown"
    
    def _is_valid_symbol(self, element: str) -> bool:
        """有効なシンボル形式かどうかを判定"""
        if ':' not in element:
            return False
        
        exchange, symbol = element.split(':', 1)
        
        # 取引所コードの妥当性チェック
        if exchange not in self.supported_exchanges:
            return False
        
        # シンボルの妥当性チェック（英数字、ドット、ハイフン許可）
        if not re.match(r'^[A-Za-z0-9.-]+
```python
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from models.stock_data import StockData, SeekingAlphaData
from .base_parser import BaseParser

class SeekingAlphaParser(BaseParser):
    """Seeking Alpha Excelファイルパーサー（4シート対応）"""
    
    def __init__(self):
        self.required_sheets = ['Summary', 'Ratings', 'Holdings', 'Dividends']
    
    def parse(self, file_path: str) -> List[SeekingAlphaData]:
        """4シート構成のExcelファイルを解析"""
        try:
            # 全シートを読み込み
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # 必要なシートの存在確認
            missing_sheets = [sheet for sheet in self.required_sheets 
                            if sheet not in excel_data.keys()]
            if missing_sheets:
                raise ValueError(f"必要なシートが見つかりません: {missing_sheets}")
            
            # 各シートのデータを統合
            symbols = self._get_symbols_list(excel_data)
            seeking_alpha_data = []
            
            for symbol in symbols:
                data = self._parse_symbol_data(symbol, excel_data)
                seeking_alpha_data.append(data)
            
            return seeking_alpha_data
            
        except Exception as e:
            raise ValueError(f"Seeking Alphaファイルの解析に失敗: {e}")
    
    def _get_symbols_list(self, excel_data: Dict) -> List[str]:
        """全シートから銘柄シンボルのリストを取得"""
        summary_df = excel_data['Summary']
        if 'Symbol' in summary_df.columns:
            return summary_df['Symbol'].dropna().tolist()
        else:
            raise ValueError("Summaryシートに'Symbol'列が見つかりません")
    
    def _parse_symbol_data(self, symbol: str, excel_data: Dict) -> SeekingAlphaData:
        """特定銘柄のデータを4シートから統合"""
        data = SeekingAlphaData(symbol=symbol)
        
        # Summaryシートからデータ取得
        summary_df = excel_data['Summary']
        summary_row = summary_df[summary_df['Symbol'] == symbol]
        if not summary_row.empty:
            row = summary_row.iloc[0]
            data.price = self._safe_float(row.get('Price'))
            data.change = self._safe_float(row.get('Change'))
            data.change_percent = self._safe_float(row.get('Change %'))
            data.volume = self._safe_int(row.get('Volume'))
            data.avg_volume = self._safe_float(row.get('Avg. Vol'))
            data.day_low = self._safe_float(row.get('Day Low'))
            data.day_high = self._safe_float(row.get('Day High'))
            data.week52_low = self._safe_float(row.get('52W Low'))
            data.week52_high = self._safe_float(row.get('52W High'))
            data.quant_rating = self._safe_float(row.get('Quant Rating'))
            data.sa_analyst_rating = self._safe_float(row.get('SA Analyst Ratings'))
            data.wall_street_rating = self._safe_float(row.get('Wall Street Ratings'))
        
        # Ratingsシートからデータ取得
        ratings_df = excel_data['Ratings']
        ratings_row = ratings_df[ratings_df['Symbol'] == symbol]
        if not ratings_row.empty:
            row = ratings_row.iloc[0]
            data.valuation_grade = self._safe_str(row.get('Valuation Grade'))
            data.growth_grade = self._safe_str(row.get('Growth Grade'))
            data.profitability_grade = self._safe_str(row.get('Profitability Grade'))
            data.momentum_grade = self._safe_str(row.get('Momentum Grade'))
            data.eps_revision_grade = self._safe_str(row.get('EPS Revision Grade'))
        
        # Holdingsシートからデータ取得
        holdings_df = excel_data['Holdings']
        holdings_row = holdings_df[holdings_df['Symbol'] == symbol]
        if not holdings_row.empty:
            row = holdings_row.iloc[0]
            data.shares = self._safe_float(row.get('Shares'))
            data.cost = self._safe_float(row.get('Cost'))
            data.todays_gain = self._safe_float(row.get("Today's Gain"))
            data.todays_gain_percent = self._safe_float(row.get("Today's % Gain"))
            data.total_change = self._safe_float(row.get('Total Change'))
            data.total_change_percent = self._safe_float(row.get('Total % Change'))
            data.value = self._safe_float(row.get('Value'))
        
        # Dividendsシートからデータ取得
        dividends_df = excel_data['Dividends']
        dividends_row = dividends_df[dividends_df['Symbol'] == symbol]
        if not dividends_row.empty:
            row = dividends_row.iloc[0]
            data.dividend_safety = self._safe_str(row.get('Safety'))
            data.dividend_growth = self._safe_str(row.get('Growth'))
            data.dividend_yield_grade = self._safe_str(row.get('Yield'))
            data.dividend_consistency = self._safe_str(row.get('Consistency'))
            data.ex_dividend_date = self._safe_date(row.get('Ex-Div Date'))
            data.payout_date = self._safe_date(row.get('Payout Date'))
            data.frequency = self._safe_str(row.get('Frequency'))
            data.yield_ttm = self._safe_float(row.get('Yield TTM'))
            data.yield_forward = self._safe_float(row.get('Yield FWD'))
            data.dividend_rate_ttm = self._safe_float(row.get('Div Rate TTM'))
            data.dividend_rate_forward = self._safe_float(row.get('Div Rate FWD'))
            data.payout_ratio = self._safe_float(row.get('Payout Ratio'))
            data.dividend_growth_3y = self._safe_float(row.get('Div Growth 3Y'))
            data.dividend_growth_5y = self._safe_float(row.get('Div Growth 5Y'))
            data.beta_24m = self._safe_float(row.get('24M Beta'))
        
        return data
    
    def _safe_float(self, value) -> Optional[float]:
        """安全なfloat変換（'-'や空値を処理）"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """安全なint変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_str(self, value) -> Optional[str]:
        """安全なstring変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        return str(value).strip()
    
    def _safe_date(self, value) -> Optional[str]:
        """安全な日付変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            # M/D/YYYY形式をYYYY-MM-DD形式に変換
            if isinstance(value, str) and '/' in value:
                parts = value.split('/')
                if len(parts) == 3:
                    month, day, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return str(value)
        except:
            return None
    
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)
            # 必要なシートが存在するかチェック
            return all(sheet in excel_data.keys() for sheet in self.required_sheets)
        except:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子"""
        return ['.xlsx', '.xls']
```

#### 4.2.5 拡張データモデル (models/stock_data.py)
```python
from abc import ABC, abstractmethod
from typing import List
from models.stock_data import StockData

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> List[StockData]:
        """ファイルを解析してStockDataのリストを返す"""
        pass
    
    @abstractmethod
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子を返す"""
        pass
```

## 5. 機能仕様

### 5.1 基本コマンド

#### 5.1.1 ファイル変換
```bash
# TradingView → Seeking Alpha
stock-cli convert --from tradingview --to seekingalpha --input watchlist.txt --output portfolio.csv

# Seeking Alpha → TradingView
stock-cli convert --from seekingalpha --to tradingview --input portfolio.xlsx --output tradingview_list.txt

# Seeking Alpha → Google Sheets
stock-cli convert --from seekingalpha --to googlesheets --input portfolio.xlsx --spreadsheet-id "your_sheet_id"
```

#### 5.1.2 Google Sheets操作（Seeking Alpha拡張対応）
```bash
# 新規スプレッドシート作成（4シート構成）
stock-cli sheets create --name "My Stock Portfolio" --template seekingalpha-full

# Seeking Alphaファイルのインポート（4シート対応）
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-id "sheet_id" \
  --preserve-all-data

# 特定シートのみインポート
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --sheets "Summary,Holdings" \
  --spreadsheet-id "sheet_id"

# データのエクスポート（シート別）
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --sheet "Holdings" \
  --format tradingview \
  --output exported_list.txt

# 全データの統合エクスポート
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --format seekingalpha-summary \
  --output portfolio_summary.xlsx

# 詳細データ分析（Seeking Alphaデータ活用）
stock-cli analyze \
  --spreadsheet-id "sheet_id" \
  --metric "dividend_yield" \
  --top 10 \
  --output analysis_report.csv

# データの同期（高度な設定）
stock-cli sheets sync \
  --local-file "UsStock 2025-07-30.xlsx" \
  --spreadsheet-id "sheet_id" \
  --mode seekingalpha-full \
  --preserve-ratings \
  --update-prices-only
```

#### 5.1.3 データ分析コマンド（新規追加）
```bash
# レーティング分析
stock-cli analyze ratings \
  --spreadsheet-id "sheet_id" \
  --filter "quant_rating>4.0" \
  --sort "sa_analyst_rating desc"

# 配当分析
stock-cli analyze dividends \
  --spreadsheet-id "sheet_id" \
  --min-yield 0.02 \
  --safety-grade "A,B" \
  --output dividend_candidates.xlsx

# ポートフォリオパフォーマンス分析
stock-cli analyze performance \
  --spreadsheet-id "sheet_id" \
  --period "1M,3M,6M" \
  --benchmark "SPY" \
  --output performance_report.pdf

# バリュエーション分析
stock-cli analyze valuation \
  --spreadsheet-id "sheet_id" \
  --metrics "PE,PB,PEG" \
  --sector-comparison \
  --output valuation_analysis.xlsx
```

#### 5.1.3 バッチ処理
```bash
# 複数ファイルの一括変換
stock-cli batch convert --config batch_config.yaml

# 定期同期設定
stock-cli schedule sync --interval daily --time "09:00" --config sync_config.yaml
```

### 5.2 設定管理

#### 5.2.1 初期設定
```bash
# Google認証の設定
stock-cli setup google-auth --credentials-file credentials.json

# デフォルト設定の構成
stock-cli config init

# 設定の確認
stock-cli config show
```

#### 5.2.2 設定ファイル (config/config.yaml)
```yaml
google_sheets:
  credentials_file: "credentials.json"  # OAuth2クライアント認証情報ファイル
  token_file: "token.json"             # 保存される認証トークン
  oauth_port: 8080                     # OAuth認証用ローカルサーバーポート
  default_spreadsheet_id: ""
  sheet_name: "Stock_Data"
  batch_size: 100

platforms:
  tradingview:
    encoding: "utf-8"
    include_exchange_prefix: true
  seekingalpha:
    default_quantity: 0
    default_cost: 0.0

logging:
  level: "INFO"
  file: "stock_cli.log"
  max_size: "10MB"
  backup_count: 5

conversion:
  symbol_mapping_file: "symbol_mapping.json"
  auto_detect_exchange: true
  fallback_exchange: "NASDAQ"
```

### 5.3 Google認証セットアップ

#### 5.3.1 初回セットアップ手順
```bash
# 1. Google Cloud Consoleでプロジェクト作成
# 2. Google Sheets API、Google Drive APIを有効化
# 3. OAuth2.0クライアントIDを作成（デスクトップアプリケーション）
# 4. credentials.jsonをダウンロード

# 5. CLIで初回認証
stock-cli auth setup --credentials-file credentials.json

# 6. ブラウザが開かれるので認証を完了
# 7. token.jsonが自動生成される
```

#### 5.3.2 認証管理コマンド
```bash
# 認証状態の確認
stock-cli auth status

# 認証情報の更新（再認証）
stock-cli auth refresh

# 認証情報の削除（再認証強制）
stock-cli auth revoke

# 認証設定の変更
stock-cli auth configure --port 8080 --credentials-file new_credentials.json
```

## 6. エラーハンドリング

### 6.1 カスタム例外クラス
```python
class StockCliError(Exception):
    """基底例外クラス"""
    pass

class FileFormatError(StockCliError):
    """ファイル形式エラー"""
    pass

class GoogleSheetsError(StockCliError):
    """Google Sheets API関連エラー"""
    pass

class ConversionError(StockCliError):
    """変換処理エラー"""
    pass

class ValidationError(StockCliError):
    """データ検証エラー"""
    pass
```

### 6.2 エラー処理方針
- **ファイル読み込みエラー**: 詳細なエラーメッセージと修正提案を表示
- **API接続エラー**: リトライ機能付きで自動復旧を試行
- **データ変換エラー**: 問題のあるレコードをスキップし、処理を継続
- **認証エラー**: 再認証フローを案内

## 7. セキュリティ要件

### 7.1 OAuth2認証の管理
- **OAuth2フロー**: デスクトップアプリケーション用のOAuth2.0を使用
- **トークン管理**: アクセストークンとリフレッシュトークンの自動管理
- **認証情報保存**: token.jsonファイルでローカル保存（適切なファイル権限設定）
- **自動更新**: リフレッシュトークンによる自動アクセストークン更新
- **認証スコープ**: 最小限必要なスコープのみ使用
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`

### 7.2 認証ファイルの管理
```python
# 推奨ファイル権限設定
credentials.json: 600 (所有者のみ読み書き)
token.json: 600 (所有者のみ読み書き)
```

### 7.3 データ保護
- 一時ファイルの安全な削除
- ログファイルに認証情報や機密データを記録しない
- エラーメッセージでの機密情報露出防止
- Google Sheets APIレート制限の遵守

### 7.4 認証エラー処理
```python
# 認証エラー時の自動対応
if token_expired:
    try_refresh_token()
elif token_invalid:
    request_new_authorization()
elif api_quota_exceeded:
    implement_exponential_backoff()
```

## 8. パフォーマンス要件

### 8.1 処理能力
- **小規模**: 100銘柄未満 - 5秒以内
- **中規模**: 1,000銘柄未満 - 30秒以内
- **大規模**: 10,000銘柄未満 - 5分以内

### 8.2 最適化手法
- バッチ処理による効率化
- Google Sheets APIのレート制限対応
- メモリ効率的なデータ処理

## 9. テスト要件

### 9.1 テスト種別
- **単体テスト**: 各パーサー・コンバーターの動作確認
- **統合テスト**: API連携とファイル変換の確認
- **E2Eテスト**: CLI操作全体の動作確認

### 9.2 テストデータ
各プラットフォームのサンプルファイルを用意:
- **TradingViewサンプル**: 混合市場の銘柄リスト（TSE:7203,NASDAQ:AAPL等）
- **Seeking Alphaサンプル**: 実際のポートフォリオデータ（4シート構成）
  - Summary: 30銘柄の基本データ + レーティング
  - Ratings: 詳細レーティング情報（A+～Fグレード）
  - Holdings: 保有情報（多くは空データ）  
  - Dividends: 配当詳細データ（利回り、成長率等）

#### Seeking Alphaテストデータの特徴:
```python
# 実際のデータ例（UsStock 2025-07-30.xlsx より）
sample_data = {
    "AAPL": {
        "price": 211.27,
        "quant_rating": 3.32,
        "valuation_grade": "F",
        "profitability_grade": "A+",
        "dividend_safety": "A",
        "yield_ttm": 0.00478,
        "beta_24m": 1.101511
    },
    "AMZN": {
        "price": 231.01,
        "quant_rating": 4.86,
        "valuation_grade": "D",
        "profitability_grade": "A+",
        "dividend_safety": "-",  # 配当なし
        "beta_24m": 1.323974
    }
}
```

## 10. 拡張性

### 10.1 プラットフォーム追加
新しいプラットフォーム対応時の拡張ポイント:
- パーサークラスの追加実装
- フォーマット変換ロジックの追加
- 設定ファイルへの新プラットフォーム情報追加

### 10.2 機能拡張予定
- **フェーズ2**: 株価データの自動取得機能とSeeking Alphaデータとの統合
- **フェーズ3**: ポートフォリオ分析機能（レーティング、配当、バリュエーション分析）
- **フェーズ4**: アラート機能（レーティング変更、配当発表等の通知）
- **フェーズ5**: Web UIの提供（ダッシュボード形式の可視化）
- **フェーズ6**: モバイルアプリ連携とリアルタイム更新
- **フェーズ7**: AI powered投資推奨機能（Seeking Alphaデータ活用）

### 10.3 Seeking Alpha データ活用の拡張
```python
# 将来の機能例
# レーティングベースのスクリーニング
filtered_stocks = portfolio.filter(
    quant_rating__gte=4.0,
    valuation_grade__in=['A', 'B', 'C'],
    dividend_safety__in=['A', 'A+']
)

# ポートフォリオリスク分析
risk_analysis = portfolio.analyze_risk(
    beta_threshold=1.5,
    sector_concentration_limit=0.3,
    dividend_dependency_check=True
)

# 自動リバランシング提案
rebalance_suggestions = portfolio.suggest_rebalancing(
    target_allocation=target_weights,
    transaction_cost=0.001,
    tax_considerations=True
)
```

## 11. デプロイメント

### 11.1 インストール方法
```bash
# PyPIからのインストール
pip install stock-watchlist-cli

# ソースからのインストール
git clone https://github.com/username/stock-watchlist-cli.git
cd stock-watchlist-cli
pip install -e .
```

### 11.2 設定ファイルの初期化
```bash
# 初期設定
stock-cli setup init

# Google認証設定（提供いただいたフローを改良）
stock-cli auth setup --credentials-file credentials.json
# -> ブラウザが開かれ、OAuth認証フローが開始されます
# -> 認証完了後、token.jsonが自動生成されます

# 認証状態の確認
stock-cli auth status

# 設定確認
stock-cli config show
```

### 11.3 実使用例
```bash
# 1. 初回セットアップ
stock-cli auth setup --credentials-file credentials.json

# 2. TradingViewファイルからGoogle Sheetsへインポート
stock-cli sheets import \
  --file tradingview_watchlist.txt \
  --format tradingview \
  --spreadsheet-name "My Portfolio"

# 3. Seeking AlphaファイルからGoogle Sheetsへインポート
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-name "My Portfolio" \
  --preserve-all-data

# 4. Google SheetsからTradingView形式でエクスポート
stock-cli sheets export \
  --spreadsheet-id "1abc...xyz" \
  --format tradingview \
  --output tradingview_list.txt

# 5. バッチ処理での複数ファイル変換
stock-cli batch convert \
  --input-dir ./watchlists \
  --output-dir ./converted \
  --target-format googlesheets
```

## 12. 保守・運用

### 12.1 ログ管理
- 処理ログの記録 (INFO, WARNING, ERROR)
- パフォーマンスメトリクスの収集
- エラー発生時の詳細情報記録

### 12.2 更新・メンテナンス
- 依存ライブラリの定期更新
- APIの仕様変更への対応
- ユーザーフィードバックの収集と対応

## 13. ドキュメント

### 13.1 ユーザーマニュアル
- インストールガイド
- 基本的な使用方法
- トラブルシューティング
- FAQ

### 13.2 開発者ドキュメント
- API仕様書
- 拡張開発ガイド
- コードスタイルガイド
- 貢献ガイドライン

---

## 付録

### A. 銘柄コード統一ルール
各プラットフォーム間での銘柄コード統一基準:

| プラットフォーム | 表記例 | 統一形式 |
|---|---|---|
| TradingView | TSE:7203 | TSE:7203 |
| TradingView | NASDAQ:AAPL | NASDAQ:AAPL |
| Seeking Alpha | AAPL | NASDAQ:AAPL |
| Seeking Alpha | TM | NYSE:TM |

### B. サポート対象市場
- **米国**: NYSE、NASDAQ、AMEX
- **日本**: 東証プライム、東証スタンダード、東証グロース（TradingView経由）
- **その他**: 主要な海外市場（要望に応じて追加）

### D. Google Cloud Console設定手順

#### OAuth2.0クライアントID作成手順:
1. **プロジェクト作成**: Google Cloud Consoleで新しいプロジェクト作成
2. **API有効化**: 
   - Google Sheets API
   - Google Drive API
3. **OAuth同意画面設定**: 
   - アプリケーション名設定
   - 承認済みドメイン設定（localhost含む）
4. **認証情報作成**: 
   - 「デスクトップアプリケーション」を選択
   - credentials.jsonをダウンロード
5. **スコープ設定**: 必要最小限のスコープを設定

#### ファイル構成例:
```
project_root/
├── credentials.json     # OAuth2クライアント認証情報
├── token.json          # 生成される認証トークン（自動作成）
├── config.yaml         # アプリケーション設定
└── stock_cli.log       # ログファイル
```

### C. 想定される課題と対策
1. **API制限**: Google Sheets APIの利用制限
   - 対策: バッチ処理とリトライ機能、指数バックオフ
2. **認証エラー**: OAuth認証の失敗や期限切れ
   - 対策: 自動リフレッシュ機能と再認証フロー
3. **データ形式の変更**: 各プラットフォームの仕様変更
   - 対策: 柔軟なパーサー設計と定期的な検証
4. **データ互換性**: プラットフォーム間での情報の違い
   - 対策: 共通フィールドのマッピングと拡張フィールドの適切な処理
5. **ネットワークエラー**: インターネット接続の問題
   - 対策: 接続確認とオフライン処理機能

この仕様書は開発進行に合わせて継続的に更新されます。, symbol):
            return False
        
        return True
    
    def _parse_symbol(self, element: str, section: str) -> TradingViewData:
        """個別シンボルを解析"""
        exchange, symbol = element.split(':', 1)
        
        return TradingViewData(
            symbol=symbol,
            exchange=exchange,
            full_symbol=element,
            section=section,
            source_platform="tradingview",
            date_imported=datetime.now()
        )
    
    def export_format(self, data: List[TradingViewData], 
                     include_sections: bool = True) -> str:
        """TradingView形式でエクスポート"""
        if not include_sections:
            # セクションなしの場合
            symbols = [item.full_symbol for item in data]
            return ','.join(symbols)
        
        # セクション付きの場合
        sections = {}
        for item in data:
            section = item.section or "Default"
            if section not in sections:
                sections[section] = []
            sections[section].append(item.full_symbol)
        
        result = []
        for section_name, symbols in sections.items():
            if section_name != "Default":
                result.append(f"###SECTION {section_name}")
            result.extend(symbols)
        
        return ','.join(result)
    
    def get_statistics(self, data: List[TradingViewData]) -> Dict:
        """統計情報を取得"""
        exchange_counts = {}
        section_counts = {}
        
        for item in data:
            # 取引所別カウント
            exchange = item.exchange
            exchange_counts[exchange] = exchange_counts.get(exchange, 0) + 1
            
            # セクション別カウント
            section = item.section or "Default"
            section_counts[section] = section_counts.get(section, 0) + 1
        
        return {
            "total_symbols": len(data),
            "exchange_distribution": exchange_counts,
            "section_distribution": section_counts,
            "supported_exchanges": self.supported_exchanges
        }
    
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            # 基本フォーマットチェック
            if not content:
                return False
            
            elements = [elem.strip() for elem in content.split(',') if elem.strip()]
            
            # 少なくとも1つの有効なシンボルが含まれているかチェック
            valid_symbols = [elem for elem in elements if self._is_valid_symbol(elem)]
            return len(valid_symbols) > 0
            
        except Exception:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子"""
        return ['.txt']

#### 4.2.4 TradingView拡張データモデル (models/stock_data.py追加)
```python
class TradingViewData(BaseModel):
    """TradingView拡張データモデル（セクション対応）"""
    symbol: str
    exchange: str
    full_symbol: str  # "EXCHANGE:SYMBOL" 形式
    section: Optional[str] = "Default"  # セクション名
    
    # メタデータ
    source_platform: Literal["tradingview"] = "tradingview"
    date_imported: datetime = datetime.now()
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Symbol cannot be empty')
        return v.strip().upper()
    
    @validator('exchange')  
    def validate_exchange(cls, v):
        supported = ['NASDAQ', 'NYSE', 'AMEX', 'TSE', 'LSE', 'FRA']
        if v not in supported:
            raise ValueError(f'Unsupported exchange: {v}')
        return v.upper()
    
    @validator('full_symbol')
    def validate_full_symbol(cls, v):
        if ':' not in v:
            raise ValueError('Full symbol must be in EXCHANGE:SYMBOL format')
        return v.upper()
```

#### 4.2.5 Seeking Alphaパーサー (parsers/seekingalpha_parser.py)
```python
import pandas as pd
from typing import List
from datetime import datetime
from models.stock_data import SeekingAlphaData
from .base_parser import BaseParser

class SeekingAlphaParser(BaseParser):
    """Seeking Alpha Excelファイルパーサー"""
    
    def parse(self, file_path: str) -> List[SeekingAlphaData]:
        """4シート構成のExcelファイルを解析"""
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        # Summaryシートから基本情報を取得
        summary_df = excel_data.get('Summary', pd.DataFrame())
        if summary_df.empty or 'Symbol' not in summary_df.columns:
            raise ValueError("Summaryシートが見つからないか、Symbolカラムがありません")
        
        seeking_alpha_data = []
        
        for _, row in summary_df.iterrows():
            symbol = row.get('Symbol')
            if pd.isna(symbol):
                continue
                
            data = SeekingAlphaData(
                symbol=str(symbol),
                price=self._safe_float(row.get('Price')),
                quant_rating=self._safe_float(row.get('Quant Rating')),
                sa_analyst_rating=self._safe_float(row.get('SA Analyst Ratings')),
                # その他の必要なフィールドを追加
                source_platform="seekingalpha",
                date_imported=datetime.now()
            )
            
            # 他のシートからデータを補完
            self._add_ratings_data(data, excel_data.get('Ratings'))
            self._add_dividend_data(data, excel_data.get('Dividends'))
            
            seeking_alpha_data.append(data)
        
        return seeking_alpha_data
    
    def _safe_float(self, value):
        """安全なfloat変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    def _add_ratings_data(self, data, ratings_df):
        """レーティングデータを追加"""
        if ratings_df is None or ratings_df.empty:
            return
        
        row = ratings_df[ratings_df['Symbol'] == data.symbol]
        if not row.empty:
            row = row.iloc[0]
            data.valuation_grade = self._safe_str(row.get('Valuation Grade'))
            data.growth_grade = self._safe_str(row.get('Growth Grade'))
    
    def _add_dividend_data(self, data, dividends_df):
        """配当データを追加"""
        if dividends_df is None or dividends_df.empty:
            return
        
        row = dividends_df[dividends_df['Symbol'] == data.symbol]
        if not row.empty:
            row = row.iloc[0]
            data.dividend_safety = self._safe_str(row.get('Safety'))
            data.yield_ttm = self._safe_float(row.get('Yield TTM'))
    
    def _safe_str(self, value):
        """安全なstring変換"""
        if pd.isna(value) or value == '-' or value == '':
            return None
        return str(value).strip()
    
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None)
            return 'Summary' in excel_data.keys()
        except:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        return ['.xlsx', '.xls']
```

#### 4.2.6 Seeking Alphaデータモデル (models/stock_data.py追加)
```python
class SeekingAlphaData(BaseModel):
    """Seeking Alpha用データモデル（主要フィールドのみ）"""
    symbol: str
    
    # 基本価格・レーティング情報
    price: Optional[float] = None
    quant_rating: Optional[float] = None
    sa_analyst_rating: Optional[float] = None
    wall_street_rating: Optional[float] = None
    
    # レーティンググレード
    valuation_grade: Optional[str] = None
    growth_grade: Optional[str] = None
    profitability_grade: Optional[str] = None
    
    # 配当情報
    dividend_safety: Optional[str] = None
    yield_ttm: Optional[float] = None
    
    # メタデータ
    source_platform: Literal["seekingalpha"] = "seekingalpha"
    date_imported: datetime = datetime.now()
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.strip().upper()
```
```python
from abc import ABC, abstractmethod
from typing import List
from models.stock_data import StockData

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> List[StockData]:
        """ファイルを解析してStockDataのリストを返す"""
        pass
    
    @abstractmethod
    def validate_format(self, file_path: str) -> bool:
        """ファイル形式の妥当性を検証"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """サポートするファイル拡張子を返す"""
        pass
```

## 5. 機能仕様

### 5.1 基本コマンド

#### 5.1.1 ファイル変換
```bash
# TradingView → Seeking Alpha
stock-cli convert --from tradingview --to seekingalpha --input watchlist.txt --output portfolio.csv

# Seeking Alpha → TradingView
stock-cli convert --from seekingalpha --to tradingview --input portfolio.xlsx --output tradingview_list.txt

# Seeking Alpha → Google Sheets
stock-cli convert --from seekingalpha --to googlesheets --input portfolio.xlsx --spreadsheet-id "your_sheet_id"
```

#### 5.1.2 Google Sheets操作（Seeking Alpha拡張対応）
```bash
# 新規スプレッドシート作成（4シート構成）
stock-cli sheets create --name "My Stock Portfolio" --template seekingalpha-full

# Seeking Alphaファイルのインポート（4シート対応）
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-id "sheet_id" \
  --preserve-all-data

# 特定シートのみインポート
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --sheets "Summary,Holdings" \
  --spreadsheet-id "sheet_id"

# データのエクスポート（シート別）
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --sheet "Holdings" \
  --format tradingview \
  --output exported_list.txt

# 全データの統合エクスポート
stock-cli sheets export \
  --spreadsheet-id "sheet_id" \
  --format seekingalpha-summary \
  --output portfolio_summary.xlsx

# 詳細データ分析（Seeking Alphaデータ活用）
stock-cli analyze \
  --spreadsheet-id "sheet_id" \
  --metric "dividend_yield" \
  --top 10 \
  --output analysis_report.csv

# データの同期（高度な設定）
stock-cli sheets sync \
  --local-file "UsStock 2025-07-30.xlsx" \
  --spreadsheet-id "sheet_id" \
  --mode seekingalpha-full \
  --preserve-ratings \
  --update-prices-only
```

#### 5.1.3 データ分析コマンド（新規追加）
```bash
# レーティング分析
stock-cli analyze ratings \
  --spreadsheet-id "sheet_id" \
  --filter "quant_rating>4.0" \
  --sort "sa_analyst_rating desc"

# 配当分析
stock-cli analyze dividends \
  --spreadsheet-id "sheet_id" \
  --min-yield 0.02 \
  --safety-grade "A,B" \
  --output dividend_candidates.xlsx

# ポートフォリオパフォーマンス分析
stock-cli analyze performance \
  --spreadsheet-id "sheet_id" \
  --period "1M,3M,6M" \
  --benchmark "SPY" \
  --output performance_report.pdf

# バリュエーション分析
stock-cli analyze valuation \
  --spreadsheet-id "sheet_id" \
  --metrics "PE,PB,PEG" \
  --sector-comparison \
  --output valuation_analysis.xlsx
```

#### 5.1.3 バッチ処理
```bash
# 複数ファイルの一括変換
stock-cli batch convert --config batch_config.yaml

# 定期同期設定
stock-cli schedule sync --interval daily --time "09:00" --config sync_config.yaml
```

### 5.2 設定管理

#### 5.2.1 初期設定
```bash
# Google認証の設定
stock-cli setup google-auth --credentials-file credentials.json

# デフォルト設定の構成
stock-cli config init

# 設定の確認
stock-cli config show
```

#### 5.2.2 設定ファイル (config/config.yaml)
```yaml
google_sheets:
  credentials_file: "credentials.json"  # OAuth2クライアント認証情報ファイル
  token_file: "token.json"             # 保存される認証トークン
  oauth_port: 8080                     # OAuth認証用ローカルサーバーポート
  default_spreadsheet_id: ""
  sheet_name: "Stock_Data"
  batch_size: 100

platforms:
  tradingview:
    encoding: "utf-8"
    include_exchange_prefix: true
  seekingalpha:
    default_quantity: 0
    default_cost: 0.0

logging:
  level: "INFO"
  file: "stock_cli.log"
  max_size: "10MB"
  backup_count: 5

conversion:
  symbol_mapping_file: "symbol_mapping.json"
  auto_detect_exchange: true
  fallback_exchange: "NASDAQ"
```

### 5.3 Google認証セットアップ

#### 5.3.1 初回セットアップ手順
```bash
# 1. Google Cloud Consoleでプロジェクト作成
# 2. Google Sheets API、Google Drive APIを有効化
# 3. OAuth2.0クライアントIDを作成（デスクトップアプリケーション）
# 4. credentials.jsonをダウンロード

# 5. CLIで初回認証
stock-cli auth setup --credentials-file credentials.json

# 6. ブラウザが開かれるので認証を完了
# 7. token.jsonが自動生成される
```

#### 5.3.2 認証管理コマンド
```bash
# 認証状態の確認
stock-cli auth status

# 認証情報の更新（再認証）
stock-cli auth refresh

# 認証情報の削除（再認証強制）
stock-cli auth revoke

# 認証設定の変更
stock-cli auth configure --port 8080 --credentials-file new_credentials.json
```

## 6. エラーハンドリング

### 6.1 カスタム例外クラス
```python
class StockCliError(Exception):
    """基底例外クラス"""
    pass

class FileFormatError(StockCliError):
    """ファイル形式エラー"""
    pass

class GoogleSheetsError(StockCliError):
    """Google Sheets API関連エラー"""
    pass

class ConversionError(StockCliError):
    """変換処理エラー"""
    pass

class ValidationError(StockCliError):
    """データ検証エラー"""
    pass
```

### 6.2 エラー処理方針
- **ファイル読み込みエラー**: 詳細なエラーメッセージと修正提案を表示
- **API接続エラー**: リトライ機能付きで自動復旧を試行
- **データ変換エラー**: 問題のあるレコードをスキップし、処理を継続
- **認証エラー**: 再認証フローを案内

## 7. セキュリティ要件

### 7.1 OAuth2認証の管理
- **OAuth2フロー**: デスクトップアプリケーション用のOAuth2.0を使用
- **トークン管理**: アクセストークンとリフレッシュトークンの自動管理
- **認証情報保存**: token.jsonファイルでローカル保存（適切なファイル権限設定）
- **自動更新**: リフレッシュトークンによる自動アクセストークン更新
- **認証スコープ**: 最小限必要なスコープのみ使用
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`

### 7.2 認証ファイルの管理
```python
# 推奨ファイル権限設定
credentials.json: 600 (所有者のみ読み書き)
token.json: 600 (所有者のみ読み書き)
```

### 7.3 データ保護
- 一時ファイルの安全な削除
- ログファイルに認証情報や機密データを記録しない
- エラーメッセージでの機密情報露出防止
- Google Sheets APIレート制限の遵守

### 7.4 認証エラー処理
```python
# 認証エラー時の自動対応
if token_expired:
    try_refresh_token()
elif token_invalid:
    request_new_authorization()
elif api_quota_exceeded:
    implement_exponential_backoff()
```

## 8. パフォーマンス要件

### 8.1 処理能力
- **小規模**: 100銘柄未満 - 5秒以内
- **中規模**: 1,000銘柄未満 - 30秒以内
- **大規模**: 10,000銘柄未満 - 5分以内

### 8.2 最適化手法
- バッチ処理による効率化
- Google Sheets APIのレート制限対応
- メモリ効率的なデータ処理

## 9. テスト要件

### 9.1 テスト種別
- **単体テスト**: 各パーサー・コンバーターの動作確認
- **統合テスト**: API連携とファイル変換の確認
- **E2Eテスト**: CLI操作全体の動作確認

### 9.2 テストデータ
各プラットフォームのサンプルファイルを用意:
- **TradingViewサンプル**: 混合市場の銘柄リスト（TSE:7203,NASDAQ:AAPL等）
- **Seeking Alphaサンプル**: 実際のポートフォリオデータ（4シート構成）
  - Summary: 30銘柄の基本データ + レーティング
  - Ratings: 詳細レーティング情報（A+～Fグレード）
  - Holdings: 保有情報（多くは空データ）  
  - Dividends: 配当詳細データ（利回り、成長率等）

#### Seeking Alphaテストデータの特徴:
```python
# 実際のデータ例（UsStock 2025-07-30.xlsx より）
sample_data = {
    "AAPL": {
        "price": 211.27,
        "quant_rating": 3.32,
        "valuation_grade": "F",
        "profitability_grade": "A+",
        "dividend_safety": "A",
        "yield_ttm": 0.00478,
        "beta_24m": 1.101511
    },
    "AMZN": {
        "price": 231.01,
        "quant_rating": 4.86,
        "valuation_grade": "D",
        "profitability_grade": "A+",
        "dividend_safety": "-",  # 配当なし
        "beta_24m": 1.323974
    }
}
```

## 10. 拡張性

### 10.1 プラットフォーム追加
新しいプラットフォーム対応時の拡張ポイント:
- パーサークラスの追加実装
- フォーマット変換ロジックの追加
- 設定ファイルへの新プラットフォーム情報追加

### 10.2 機能拡張予定
- **フェーズ2**: 株価データの自動取得機能とSeeking Alphaデータとの統合
- **フェーズ3**: ポートフォリオ分析機能（レーティング、配当、バリュエーション分析）
- **フェーズ4**: アラート機能（レーティング変更、配当発表等の通知）
- **フェーズ5**: Web UIの提供（ダッシュボード形式の可視化）
- **フェーズ6**: モバイルアプリ連携とリアルタイム更新
- **フェーズ7**: AI powered投資推奨機能（Seeking Alphaデータ活用）

### 10.3 Seeking Alpha データ活用の拡張
```python
# 将来の機能例
# レーティングベースのスクリーニング
filtered_stocks = portfolio.filter(
    quant_rating__gte=4.0,
    valuation_grade__in=['A', 'B', 'C'],
    dividend_safety__in=['A', 'A+']
)

# ポートフォリオリスク分析
risk_analysis = portfolio.analyze_risk(
    beta_threshold=1.5,
    sector_concentration_limit=0.3,
    dividend_dependency_check=True
)

# 自動リバランシング提案
rebalance_suggestions = portfolio.suggest_rebalancing(
    target_allocation=target_weights,
    transaction_cost=0.001,
    tax_considerations=True
)
```

## 11. デプロイメント

### 11.1 インストール方法
```bash
# PyPIからのインストール
pip install stock-watchlist-cli

# ソースからのインストール
git clone https://github.com/username/stock-watchlist-cli.git
cd stock-watchlist-cli
pip install -e .
```

### 11.2 設定ファイルの初期化
```bash
# 初期設定
stock-cli setup init

# Google認証設定（提供いただいたフローを改良）
stock-cli auth setup --credentials-file credentials.json
# -> ブラウザが開かれ、OAuth認証フローが開始されます
# -> 認証完了後、token.jsonが自動生成されます

# 認証状態の確認
stock-cli auth status

# 設定確認
stock-cli config show
```

### 11.3 実使用例
```bash
# 1. 初回セットアップ
stock-cli auth setup --credentials-file credentials.json

# 2. TradingViewファイルからGoogle Sheetsへインポート
stock-cli sheets import \
  --file tradingview_watchlist.txt \
  --format tradingview \
  --spreadsheet-name "My Portfolio"

# 3. Seeking AlphaファイルからGoogle Sheetsへインポート
stock-cli sheets import \
  --file "UsStock 2025-07-30.xlsx" \
  --format seekingalpha \
  --spreadsheet-name "My Portfolio" \
  --preserve-all-data

# 4. Google SheetsからTradingView形式でエクスポート
stock-cli sheets export \
  --spreadsheet-id "1abc...xyz" \
  --format tradingview \
  --output tradingview_list.txt

# 5. バッチ処理での複数ファイル変換
stock-cli batch convert \
  --input-dir ./watchlists \
  --output-dir ./converted \
  --target-format googlesheets
```

## 12. 保守・運用

### 12.1 ログ管理
- 処理ログの記録 (INFO, WARNING, ERROR)
- パフォーマンスメトリクスの収集
- エラー発生時の詳細情報記録

### 12.2 更新・メンテナンス
- 依存ライブラリの定期更新
- APIの仕様変更への対応
- ユーザーフィードバックの収集と対応

## 13. ドキュメント

### 13.1 ユーザーマニュアル
- インストールガイド
- 基本的な使用方法
- トラブルシューティング
- FAQ

### 13.2 開発者ドキュメント
- API仕様書
- 拡張開発ガイド
- コードスタイルガイド
- 貢献ガイドライン

---

## 付録

### A. 銘柄コード統一ルール
各プラットフォーム間での銘柄コード統一基準:

| プラットフォーム | 表記例 | 統一形式 |
|---|---|---|
| TradingView | TSE:7203 | TSE:7203 |
| TradingView | NASDAQ:AAPL | NASDAQ:AAPL |
| Seeking Alpha | AAPL | NASDAQ:AAPL |
| Seeking Alpha | TM | NYSE:TM |

### B. サポート対象市場
- **米国**: NYSE、NASDAQ、AMEX
- **日本**: 東証プライム、東証スタンダード、東証グロース（TradingView経由）
- **その他**: 主要な海外市場（要望に応じて追加）

### D. Google Cloud Console設定手順

#### OAuth2.0クライアントID作成手順:
1. **プロジェクト作成**: Google Cloud Consoleで新しいプロジェクト作成
2. **API有効化**: 
   - Google Sheets API
   - Google Drive API
3. **OAuth同意画面設定**: 
   - アプリケーション名設定
   - 承認済みドメイン設定（localhost含む）
4. **認証情報作成**: 
   - 「デスクトップアプリケーション」を選択
   - credentials.jsonをダウンロード
5. **スコープ設定**: 必要最小限のスコープを設定

#### ファイル構成例:
```
project_root/
├── credentials.json     # OAuth2クライアント認証情報
├── token.json          # 生成される認証トークン（自動作成）
├── config.yaml         # アプリケーション設定
└── stock_cli.log       # ログファイル
```

### C. 想定される課題と対策
1. **API制限**: Google Sheets APIの利用制限
   - 対策: バッチ処理とリトライ機能、指数バックオフ
2. **認証エラー**: OAuth認証の失敗や期限切れ
   - 対策: 自動リフレッシュ機能と再認証フロー
3. **データ形式の変更**: 各プラットフォームの仕様変更
   - 対策: 柔軟なパーサー設計と定期的な検証
4. **データ互換性**: プラットフォーム間での情報の違い
   - 対策: 共通フィールドのマッピングと拡張フィールドの適切な処理
5. **ネットワークエラー**: インターネット接続の問題
   - 対策: 接続確認とオフライン処理機能

この仕様書は開発進行に合わせて継続的に更新されます。