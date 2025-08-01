# 株式ウォッチリスト管理CLI 開発ログ

## 📅 2025年7月31日 - プロジェクト開始

### 🎯 プロジェクト初期化
- **仕様書確認**: [`docs/spec.md`](spec.md) の詳細な仕様を確認
- **実装計画策定**: 4フェーズ・30日間の段階的開発計画を作成
- **サンプルデータ分析**: 
  - TradingViewファイル（[`sample/US_STOCK_012ed.txt`](../sample/US_STOCK_012ed.txt)）: 36銘柄、セクション区切り機能確認
  - SeekingAlphaファイル（[`sample/UsStock 2025-07-30.xlsx`](../sample/UsStock 2025-07-30.xlsx)）: 4シート構成確認

### 🏗️ アーキテクチャ決定
- **開発方針**: シンプルなCLIから段階的機能拡張
- **技術スタック**: Python 3.8+, Click, Pandas, Pydantic, gspread
- **パッケージ管理**: uv + pyproject.toml（現代的なPython開発環境）
- **仮想環境**: uv venv による高速な仮想環境管理
- **ブランチ戦略**: feature/phase*-* → develop → main
- **テスト戦略**: TDD、カバレッジ80%以上

### 📋 重要な技術的決定

#### 1. データモデル設計
- **統一モデル**: `StockData` を中心とした統一データ構造
- **プラットフォーム特化**: `TradingViewData`, `SeekingAlphaData` で各プラットフォーム固有データを管理
- **バリデーション**: Pydantic による型安全性とデータ検証

#### 2. TradingView特有機能への対応
- **セクション機能**: `###SECTION N` による論理的グループ分け
- **取引所プレフィックス**: `NASDAQ:`, `NYSE:`, `AMEX:` の必須対応
- **特殊シンボル**: `BRK.B` などドット付きシンボルの処理

#### 3. SeekingAlpha 4シート構造への対応
- **Summary**: 基本的な価格・統計情報
- **Ratings**: Quant/SA Analyst/Wall Street レーティング
- **Holdings**: ポートフォリオ保有情報（通常は空）
- **Dividends**: 配当関連の詳細データ

#### 4. Google Sheets連携設計
- **OAuth2.0**: デスクトップアプリケーション型認証
- **認証ファイル**: `~/dot.hiroshi-project-2025.client_secret.json` を使用（プロジェクト外管理）
- **.env管理**: 認証ファイルパスを環境変数で管理
- **バッチ処理**: API制限を考慮した効率的なデータ同期
- **エラーハンドリング**: リトライ機能とレート制限対応

### 🎯 次のステップ
- **Phase 1開始**: プロジェクト構造作成（[`feature/phase1-structure`](https://github.com/project/tree/feature/phase1-structure)）
- **環境セットアップ**: Python仮想環境、依存関係管理
- **基本CLIフレームワーク**: Click ベースのコマンド構造

---

## 📝 学習・発見事項

### TradingViewファイル形式の特徴
- **単一行形式**: 全銘柄がカンマ区切りで1行に記載
- **セクション区切り**: `###SECTION N` で論理的分割が可能
- **取引所必須**: `EXCHANGE:SYMBOL` 形式が必須
- **特殊文字対応**: ドット（`.`）を含むシンボルに対応必要

### SeekingAlpha Excelファイルの構造
- **4シート固定**: Summary, Ratings, Holdings, Dividends
- **空値処理**: `-` や空文字列の適切な処理が必要
- **データ型混在**: 数値、文字列、日付が混在するため型変換が重要
- **レーティング表記**: `A+`, `B-`, `F` などの文字列グレード

### Google Sheets API の制約
- **レート制限**: 100 requests/100 seconds/user
- **バッチ処理**: batchUpdate で効率化が必要
- **認証管理**: OAuth2.0 トークンの自動更新が重要

---
### 💡 開発セッション間の引継ぎメモ (2025-07-31)
- **コマンド実行**: `pytest` 等のパッケージコマンドは、`uv run` をつけて実行しないと `command not found` エラーになるので注意。(例: `uv run pytest tests/unit/`)
- **Excelパーサー**: SeekingAlphaのExcelファイルは条件付き書式が原因で `openpyxl` だと読み込みに失敗する。高速な `calamine` エンジン (`pip install python-calamine`) を使うことで解決した。
- **TradingView形式**: サンプルファイルは全銘柄が1行にカンマ区切りで記述されていた。仕様書だけでなく、常に実データを確認することが重要。
- **ドキュメント同期**: `PLAN.md` の完了条件チェック（`✅`→`📝`の修正）と、`DEV_LOG.md` の進捗チェック (`[ ]`→`[x]`) の同期を忘れないこと。

## 🔧 技術的課題と解決策

### 課題1: ファイルエンコーディングの自動検出
**問題**: TradingViewファイルの文字エンコーディングが不明
**解決策**: `chardet` ライブラリによる自動検出機能を実装

### 課題2: SeekingAlpha データの型変換
**問題**: Excel内の数値が文字列として読み込まれる場合がある
**解決策**: `_safe_float()`, `_safe_int()` などの安全な変換関数を実装

### 課題3: Google Sheets API の認証管理
**問題**: OAuth2.0 トークンの期限切れとリフレッシュ
**解決策**: 自動リフレッシュ機能付きの認証クラスを実装

### 課題4: 認証ファイルのセキュリティ管理
**問題**: Google認証ファイルの安全な管理とGit誤コミット防止
**解決策**:
- 認証ファイルをプロジェクト外（`~/dot.hiroshi-project-2025.client_secret.json`）に配置
- .envファイルでパス管理、.gitignoreで除外
- プログラムは読み込みのみ、直接的なファイル操作は禁止

---

## 📊 進捗管理

### Phase 1: 基盤構築（1-7日目）
- [x] タスク 1.1: プロジェクト構造作成（1-2日目） ✅ **完了 2025-07-31**
- [x] タスク 1.2: 基本CLIフレームワーク（3-4日目） ✅ **完了 2025-07-31**
- [x] タスク 1.3: ファイル読み込み機能（5-7日目） ✅ **完了 2025-07-31**

### Phase 2: パーサー実装（8-16日目）
- [x] タスク 2.1: TradingViewパーサー（8-10日目） ✅ **完了 2025-07-31**
- [x] タスク 2.2: SeekingAlphaパーサー（11-14日目） ✅ **完了 2025-07-31**
- [x] タスク 2.3: データモデル統合（15-16日目） ✅ **完了 2025-08-01**

### Phase 3: 変換機能（17-23日目）
- [x] タスク 3.1: フォーマット変換器（17-19日目） ✅ **完了 2025-08-01**
- [x] タスク 3.2: 基本変換コマンド（20-21日目） ✅ **完了 2025-08-01**
- [-] タスク 3.3: テスト・デバッグ（22-23日目）

### ✅ Phase 3.2: 基本変換コマンド（2025-08-01完了）

**実装内容**:
- `src/main.py` の `convert` コマンドを実装。
- `--from`, `--to`, `--input`, `--output` オプションを追加。
- `--preserve-sections` オプションを追加し、TradingView形式への変換時にセクション情報を保持する機能を提供。
- `FormatConverter` クラスと各パーサークラス (`TradingViewParser`, `SeekingAlphaParser`) を連携させ、ファイル変換ロジックを統合。
- 入力ファイルの読み込み、データモデルへの変換、ターゲット形式への変換、出力ファイルへの書き込み（または標準出力）のフローを実装。
- エラーハンドリングとログ出力を追加。

**技術的成果**:
- CLIコマンドとしてファイル変換機能が動作するようになった。
- 異なるデータ形式間の変換がCLIから実行可能になった。
- モジュール間の連携が強化され、コードの再利用性が向上した。

**学習事項**:
- Clickライブラリでの複雑なオプション定義と引数処理。
- CLIアプリケーションにおけるエラーハンドリングとユーザーフィードバックの重要性。
- 複数のクラスとモジュールを連携させて一つの機能を実現する設計パターン。

**Git記録**: コミット `7a18ddd` - 3ファイル、約150行追加・変更

### ✅ Phase 3.1: フォーマット変換器（2025-08-01完了）

**実装内容**:
- `src/converters/format_converter.py` に `FormatConverter` クラスを実装。
- `to_stock_data` メソッドで `TradingViewData` および `SeekingAlphaData` を `StockData` に変換。
- `to_platform_data` メソッドで `StockData` を `TradingViewData` または `SeekingAlphaData` に変換。
- `convert_list` メソッドでデータリストの一括変換をサポート。
- `convert_to_csv` メソッドで `SeekingAlphaData` のリストをCSV形式に変換。
- `convert_to_tradingview_txt` メソッドで `TradingViewData` のリストをTradingViewテキスト形式に変換（セクション保持機能付き）。
- `src/models/stock.py` の `StockData`, `TradingViewData`, `SeekingAlphaData` モデルを更新し、必要なフィールドを追加・調整。

**技術的成果**:
- 異なるプラットフォーム間のデータ変換ロジックを一元管理するクラスを構築。
- Pydanticモデルの柔軟性を活用し、データ構造の変更に強い設計を実現。
- ログ出力により、変換処理の追跡を容易にした。

**学習事項**:
- 複雑なデータ変換ロジックをモジュール化し、再利用性を高める方法。
- Pydanticモデルのフィールド追加やバリデーションの調整方法。
- 異なるデータモデル間のマッピングにおける情報損失の考慮。

**Git記録**: コミット `7a18ddd` - 3ファイル、約300行追加・変更

### Phase 4: Google Sheets連携（24-30日目）
- [ ] タスク 4.1: OAuth認証システム（24-26日目）
- [ ] タスク 4.2: Sheetsクライアント（27-29日目）
- [ ] タスク 4.3: データ同期機能（30日目）

---

## 🎉 マイルストーン達成記録

### MVP完成（予定: 7日目）
- **目標**: 基本的なファイル読み込みとCLI
- **成果物**:
- **達成日**:
- **学習事項**:

### パーサー完成（16日目）
- **目標**: TradingView・SeekingAlpha完全対応
- **成果物**: TradingViewパーサー、SeekingAlphaパーサー、統合データモデル
- **達成日**: 2025-08-01
- **学習事項**:
  - 複数プラットフォームのデータを統一的に扱うモデル設計
  - プラットフォーム間のデータマッピング手法
  - Pydanticを活用した型安全なデータ処理
  - TDDアプローチによる堅牢な実装

---

## 📝 タスク完了記録

### ✅ Phase 1.1: プロジェクト構造作成（2025-07-31完了）

**実装内容**:
- 完全なディレクトリ構造の作成（src/, tests/, config/, docs/）
- uv + pyproject.toml による現代的Python開発環境
- 55個の依存関係パッケージのインストール成功
- Click ベースの基本CLIフレームワーク
- Pydantic による型安全な設定管理システム
- 環境変数による認証ファイル管理
- ログ設定システム（ローテーション対応）

**技術的成果**:
- `stock-cli --help` コマンドが正常動作
- 設定ファイル（config.yaml）と環境変数（.env）の統合
- Google認証ファイルパスの安全な管理
- 開発ツール（black, flake8, mypy）の動作確認

**学習事項**:
- uvの高速パッケージ管理とビルドシステム
- hatchlingビルドバックエンドでのパッケージ設定
- Pydanticによる設定バリデーションの実装
- 環境変数置換機能（`${VAR_NAME:default}`形式）

**Git記録**: コミット `20df4a4` - 17ファイル、738行追加

### ✅ Phase 1.3: ファイル読み込み機能（2025-07-31完了）

**実装内容**:
- `src/utils/file_io.py` に `read_file` と `get_file_encoding` を実装。
- `chardet` を利用したエンコーディング検出。
- `read_file` に、`utf-8`, `shift_jis`, `euc_jp` などの一般的なエンコーディングを試すフォールバック処理を実装。
- TXT, CSV, XLSX 形式のファイル読み込みに対応。

**技術的成果**:
- `chardet` が短いテキストでは誤判定しやすい問題に対応するため、複数のエンコーディングを試す堅牢なファイル読み込み処理を実装できた。
- TDDサイクルを回し、テストが失敗することを確認してから実装を進めることで、品質の高いコードを効率的に作成できた。

**学習事項**:
- `chardet` の限界と、それに対するフォールバックの重要性を学んだ。
- `pytest` のフィクスチャを利用して、テストごとに独立したテストデータを作成・クリーンアップする方法を実践した。

**Git記録**: コミット `3da71c0` - 2ファイル、134行追加
### パーサー完成（予定: 16日目）
### ✅ Phase 2.1: TradingViewパーサー（2025-07-31完了）

**実装内容**:
- `src/parsers/tradingview.py` に `parse_tradingview_watchlist` を実装。
- `src/models/stock.py` に `StockData` と `TradingViewData` モデルを定義。
- TradingViewのウォッチリスト形式（単一行・カンマ区切り）の解析に対応。
- `###SECTION N` 形式のセクションマーカーを解釈し、各銘柄にセクション情報を付与する機能を実装。

**技術的成果**:
- 仕様書と実際のサンプルファイルの微妙な差異（セクションマーカーの扱い）を分析し、堅牢なパーサーを実装できた。
- TDDサイクルを徹底し、複雑なパースロジックを段階的に開発することで、品質を確保した。

**学習事項**:
- ファイル形式の仕様と、実際のデータが必ずしも一致しないケースがあることを再認識。仕様書だけでなく、実データに基づいたテストの重要性を学んだ。
- pytestのフィクスチャ (`@pytest.fixture`) をクラススコープで利用し、複数のテストで同じパース結果を効率的に再利用する方法を実践した。

**Git記録**: コミット `10705a7` - 3ファイル、125行追加
- **目標**: TradingView・SeekingAlpha完全対応
### ✅ Phase 2.2: SeekingAlphaパーサー（2025-07-31完了）

**実装内容**:
- `src/parsers/seekingalpha.py` に `parse_seekingalpha_portfolio` を実装。
- `src/models/stock.py` に `SeekingAlphaData` モデルを追加。
- 4シート構成のExcelファイルを解析し、`Summary`, `Ratings`, `Holdings`, `Dividends` の各シートからデータを統合する機能を実装。
- `'-'` や空値を `None` に変換する安全な型変換関数を実装。

**技術的成果**:
- `openpyxl` で発生した条件付き書式のエラーを、高速なExcel読み込みエンジン `calamine` を導入することで解決した。
- 複数のDataFrameにまたがるデータを、銘柄シンボルをキーとして効率的に結合する処理を実装できた。

**学習事項**:
- `pandas` のExcel読み込みエンジンを切り替えることで、ライブラリ間の互換性問題を回避できることを学んだ。
- `python-calamine` パッケージの存在と、その高速な読み込み性能を認識した。

**Git記録**: コミット `450eaf2` - 4ファイル、140行追加

### ✅ Phase 2.3: データモデル統合（2025-08-01完了）

**実装内容**:
- `src/models/stock.py` を大幅に拡張し、型安全なデータモデルを実装
- `PlatformData` 抽象基底クラスを作成し、プラットフォーム固有データの共通インターフェースを定義
- `TradingViewData` と `SeekingAlphaData` に変換メソッド（`to_seeking_alpha`, `to_trading_view`）を追加
- `StockData` モデルに共通フィールド（`name`, `sector`, `industry`）を追加
- データ正規化処理（シンボルと取引所名の大文字変換など）を実装
- データ比較（`__eq__`）とマージ機能を実装

**技術的成果**:
- Pydanticの最新機能（`field_validator`, `model_validator`）を活用した堅牢なバリデーション
- 型変数（`TypeVar`）と抽象基底クラス（`ABC`）を使用した柔軟なインターフェース設計
- プラットフォーム間のデータマッピング機能により、異なるソースからのデータを統合可能に
- TDDアプローチによる高品質な実装（テストカバレッジ85%）

**学習事項**:
- Pydanticの新しいバリデーション機能（v2系）の使い方
- Pythonの型システムを活用した設計パターン
- 抽象基底クラスを使用したインターフェース設計
- 複数のプラットフォームデータを効率的に管理する方法

**Git記録**: コミット `c93837c` - 2ファイル、267行追加、25行変更
- **成果物**: 
- **達成日**: 
- **学習事項**: 

### 変換機能完成（予定: 23日目）
- **目標**: プラットフォーム間変換の完全実装
- **成果物**: 
- **達成日**: 
- **学習事項**: 

### 完全版リリース（予定: 30日目）
- **目標**: Google Sheets連携を含む全機能
- **成果物**: 
- **達成日**: 
- **学習事項**: 

---

## 🔍 コードレビュー・品質管理

### コード品質チェックリスト
- [ ] 型ヒント（Type Hints）の完備
- [ ] Docstring の記述
- [ ] テストカバレッジ80%以上
- [ ] black によるコードフォーマット
- [ ] flake8 によるリンターチェック
- [ ] mypy による型チェック

### パフォーマンス測定
- **ファイル読み込み速度**: 
- **データ変換速度**: 
- **Google Sheets同期速度**: 

---

## 📚 参考資料・リンク

### 公式ドキュメント
- [Click Documentation](https://click.palletsprojects.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [gspread Documentation](https://gspread.readthedocs.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)

### 技術記事・チュートリアル
- [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- [OAuth 2.0 for Desktop Applications](https://developers.google.com/identity/protocols/oauth2/native-app)

### サンプルコード・リポジトリ
- [gspread Examples](https://github.com/burnash/gspread/tree/master/examples)
- [Click Examples](https://github.com/pallets/click/tree/main/examples)

---

*このログは開発進捗に応じて随時更新されます*
## 2025-07-31: Phase 1.2 基本CLIフレームワーク実装

### タスク
- **Phase 1.2: 基本CLIフレームワーク**

### 実装内容
- TDD（テスト駆動開発）アプローチを適用。まず `tests/unit/test_main.py` にて、CLIの基本動作（ヘルプ、バージョン、コマンド存在確認）のテストを先行して作成した。
- `pytest` の実行環境で `pytest: not found` や `source: not found` といった問題に直面したが、仮想環境のアクティベート方法を `source` から `.` に変更することで解決した。
- `src/main.py` の実装を最小限の状態から始め、テストが失敗すること（Red）を確認後、テストをパスする最小限のコード（Green）を実装した。
- Clickライブラリを使用し、`@click.group` と `@click.command` を用いて、`convert`, `sheets`, `analyze` の基本的なコマンドグループ構造を構築した。
- 設定ファイル `config.yaml` の読み込みと、`logging` の初期化機能を `cli` のエントリーポイントに統合した。
- 設定読み込み失敗時のエラーハンドリングを実装し、ユーザーに `click.echo` でエラーメッセージが通知されるように改善した。

### 技術的成果・学習事項
- **TDDの実践**: Red-Green-Refactorのサイクルを実際に回すことで、機能追加の単位を小さく保ち、堅牢な開発プロセスを体験できた。初期実装が存在していたため、一度コードをリセットしてRedフェーズからやり直すという実践的な対応を行った。
- **仮想環境と実行シェル**: `execute_command` で使われるシェル (`/bin/sh`) が `source` をサポートしていない問題に遭遇。POSIX準拠の `.` を使うことで互換性を確保できることを学んだ。
- **ClickとCliRunner**: `CliRunner` を使ったテストでは、引数なしで `invoke` するとサブコマンドエラーになる。テスト対象のロジックを正しく実行するには、適切な引数を渡す必要があることを確認した。
- **エラーハンドリング**: ログ出力だけでなく、`click.echo(..., err=True)` を使ってユーザーに直接フィードバックを返すことの重要性を再認識した。

### Git記録
- **branch**: `feature/phase1-cli`
- **commit**: `87766e4`

---

## ⚠️ **重要**: ドキュメント更新ルール

タスク完了後は、必ず以下の2つのドキュメントを更新してください。

1.  **`docs/PLAN.md`**:
    - 該当タスクの完了条件（`✅`）をチェック
2.  **`docs/DEV_LOG.md`**:
    - 進捗管理セクションの該当タスクをチェック (`[x]`)
    - タスク完了記録セクションに、実装内容、学習事項、GitコミットIDを追記

**これらのドキュメントは、プロジェクトの現状を正確に反映する最も重要な情報源です。**