# 株式ウォッチリスト管理CLI

TradingView、Seeking Alpha、Google Sheets間でのデータ変換を行うコマンドラインツールです。

## 概要

このツールは以下の機能を提供します：

- **TradingViewファイル解析**: セクション区切り機能付きテキストファイルの読み込み
- **Seeking Alphaファイル解析**: 4シート構成Excelファイルの完全解析
- **Google Sheets連携**: OAuth2.0認証によるデータ同期
- **プラットフォーム間変換**: 各形式間での双方向データ変換

## インストール

### 前提条件

- Python 3.8以上
- uv (推奨) または pip

### uvを使用したインストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd stock-watchlist-cli

# 仮想環境の作成
uv venv
source .venv/bin/activate

# 依存関係のインストール
uv pip install -e ".[dev]"
```

### 環境設定

```bash
# 環境変数ファイルの作成
cp .env.example .env

# .envファイルを編集してGoogle認証ファイルパスを設定
# GOOGLE_CREDENTIALS_FILE=~/dot.hiroshi-project-2025.client_secret.json
```

## 使用方法

### ファイル変換 (`convert`)

`convert` コマンドは、異なるプラットフォームのウォッチリスト形式を相互に変換します。

**基本構文**:
```bash
stock-cli convert --from <source> --to <target> --input <infile> --output <outfile> [options]
```

**使用例**:

```bash
# TradingView形式からSeekingAlpha形式(CSV)へ変換
stock-cli convert \
  --from tradingview \
  --to seekingalpha \
  --input sample/US_STOCK_012ed.txt \
  --output portfolio.csv

# SeekingAlpha形式(Excel)からTradingView形式へ変換
# --preserve-sections オプションでセクション情報を保持
stock-cli convert \
  --from seekingalpha \
  --to tradingview \
  --input sample/UsStock\ 2025-07-30.xlsx \
  --output watchlist.txt \
  --preserve-sections

# セクター情報に基づいてセクションを自動生成
stock-cli convert \
  --from seekingalpha \
  --to tradingview \
  --input sample/UsStock\ 2025-07-30.xlsx \
  --output watchlist_by_sector.txt \
  --create-sections-by-sector
```

### Google Sheets連携 (`sheets`)

Google Sheetsとの間でデータをインポート・エクスポートします。

```bash
# 新しいスプレッドシートを作成
stock-cli sheets create --name "My New Watchlist"

# ファイルをスプレッドシートにインポート
stock-cli sheets import --file data.xlsx --spreadsheet-id "your_sheet_id"

# スプレッドシートからファイルにエクスポート
stock-cli sheets export --spreadsheet-id "your_sheet_id" --format tradingview --output watchlist.txt
```

### サポートする形式

- **TradingView**: テキストファイル (.txt) - セクション区切り対応
- **Seeking Alpha**: Excelファイル (.xlsx) - 4シート構成
- **Google Sheets**: OAuth2.0認証による直接連携

## 開発

### 開発環境のセットアップ

```bash
# 開発依存関係のインストール
uv pip install -e ".[dev]"

# コード品質チェック
black src/ tests/
flake8 src/ tests/
mypy src/

# テスト実行
pytest
```

### プロジェクト構造

```
stock-watchlist-cli/
├── src/                    # ソースコード
│   ├── config/            # 設定管理
│   ├── parsers/           # ファイルパーサー
│   ├── converters/        # データ変換
│   ├── google_sheets/     # Google Sheets連携
│   ├── models/            # データモデル
│   └── utils/             # ユーティリティ
├── tests/                 # テストコード
├── docs/                  # ドキュメント
├── config/                # 設定ファイル
└── sample/                # サンプルデータ
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。