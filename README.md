# 株式ウォッチリスト管理CLI

TradingView、Seeking Alpha、Google Sheets間でのデータ変換を行うコマンドラインツールです。

## 概要

このツールは以下の機能を提供します：

- **TradingViewファイル解析**: セクション区切り機能付きテキストファイルの読み込み
- **Seeking Alphaファイル解析**: 4シート構成Excelファイルの完全解析
- **Google Sheets連携**: OAuth2.0認証によるデータ同期
- **プラットフォーム間変換**: 各形式間での双方向データ変換

## 実行方法

### 前提条件
- Python 3.8以上
- [uv](https://github.com/astral-sh/uv)

### `uvx` を使った直接実行 (推奨)
このツールは `uvx` を使うことで、リポジトリをクローンせずに直接実行できます。

```bash
# ヘルプの表示
uvx git+https://github.com/HiroshiOkada/stock-watchlist-cli stock-cli --help

# ファイル変換の実行例
uvx git+https://github.com/HiroshiOkada/stock-watchlist-cli stock-cli convert --from tradingview --to csv --input watchlist.txt
```

### Google認証の設定
Google Sheets連携機能を使用するには、初回のみ認証設定が必要です。

1.  **設定ファイルの準備**:
    `credentials.json`（Google Cloudからダウンロード）と、空の`.env`ファイルをツールの実行ディレクトリに配置します。

2.  **`.env`ファイルに追記**:
    以下の1行を`.env`ファイルに記述し、`credentials.json`へのパスを指定します。
    ```
    GOOGLE_CREDENTIALS_FILE=./credentials.json
    ```

3.  **認証コマンドの実行**:
    以下のコマンドを実行すると、ブラウザが起動し認証プロセスが開始されます。
    ```bash
    uvx git+https://github.com/HiroshiOkada/stock-watchlist-cli stock-cli auth setup
    ```
    認証が完了すると、同ディレクトリに`token.json`が生成され、以降は自動で認証が行われます。

## コマンドリファレンス

### `convert`
異なるプラットフォームのウォッチリスト形式を相互に変換します。

```bash
# TradingView形式からSeekingAlpha形式(CSV)へ変換
stock-cli convert --from tradingview --to seekingalpha --input sample/US_STOCK_012ed.txt --output portfolio.csv

# SeekingAlpha形式(Excel)からTradingView形式へ変換
stock-cli convert --from seekingalpha --to tradingview --input sample/UsStock_2025-07-30.xlsx --output watchlist.txt
```
利用可能なオプションの詳細は `stock-cli convert --help` を参照してください。

### `sheets`
Google Sheetsとの認証、データ連携を行います。

```bash
# 1. Googleアカウント認証 (初回のみ)
stock-cli auth setup

# 2. 新しいスプレッドシートを作成
stock-cli sheets create --name "My New Watchlist"

# 3. ローカルファイルをスプレッドシートにインポート
stock-cli sheets import --file sample/US_STOCK_012ed.txt --format tradingview --spreadsheet-id "your_sheet_id"

# 4. スプレッドシートからローカルファイルにエクスポート
stock-cli sheets export --spreadsheet-id "your_sheet_id" --format tradingview --output watchlist.txt
```

### `analyze`
データ分析機能です。（現在、コマンドの骨組みのみで実装されていません）

## 開発者向け情報

### 開発環境のセットアップ
ソースコードを編集・開発する場合は、リポジトリをクローンしてセットアップします。

```bash
# リポジトリのクローン
git clone https://github.com/HiroshiOkada/stock-watchlist-cli.git
cd stock-watchlist-cli

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate

# 開発依存関係を含む全パッケージをインストール
uv pip install -e ".[dev]"
```

### コード品質とテスト

```bash
# コードフォーマット
black src/ tests/

# リンター
flake8 src/ tests/

# 型チェック
mypy src/

# テスト実行
uv run pytest
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