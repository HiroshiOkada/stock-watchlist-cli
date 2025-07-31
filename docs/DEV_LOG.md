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
- [ ] タスク 1.1: プロジェクト構造作成（1-2日目）
- [ ] タスク 1.2: 基本CLIフレームワーク（3-4日目）
- [ ] タスク 1.3: ファイル読み込み機能（5-7日目）

### Phase 2: パーサー実装（8-16日目）
- [ ] タスク 2.1: TradingViewパーサー（8-10日目）
- [ ] タスク 2.2: SeekingAlphaパーサー（11-14日目）
- [ ] タスク 2.3: データモデル統合（15-16日目）

### Phase 3: 変換機能（17-23日目）
- [ ] タスク 3.1: フォーマット変換器（17-19日目）
- [ ] タスク 3.2: 基本変換コマンド（20-21日目）
- [ ] タスク 3.3: テスト・デバッグ（22-23日目）

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

### パーサー完成（予定: 16日目）
- **目標**: TradingView・SeekingAlpha完全対応
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