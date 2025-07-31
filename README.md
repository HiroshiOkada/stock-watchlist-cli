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

### 基本コマンド

```bash
# ヘルプの表示
stock-cli --help

# バージョン確認
stock-cli --version

# ファイル変換
stock-cli convert --from tradingview --to seekingalpha --input input.txt --output output.csv

# Google Sheets連携
stock-cli sheets import --file data.xlsx --spreadsheet-id "your_sheet_id"
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