# AGENTS.md — Coding Agent ルール（Codex CLI）

このドキュメントは、Codex CLI から本リポジトリで作業するエージェントのための運用規約です。`.roo/` 配下の既存ルール群を要約し、Codex CLI の分岐・承認フローを明確にします。

## 目的と原則
- プロジェクト規約の単一の入口を提供します。
- 変更は小さく焦点を絞り、無関係な修正は行いません。
- 既存スタイルに従い、テストと動作確認を優先します。
- ルールの出典は `.roo/` 配下（rules, rules-architect, rules-code, rules-debug）および `docs/` です。

## Codex CLI の運用モード
- ブランチ運用: 作業開始時に `feature/<task-name>` を作成してそこで変更します。
- 承認ゲート: 人間の承認後に `git commit` を行い、その後 `main` にマージします。
- サンドボックス: 既定は読み取り専用。ファイル変更（`apply_patch`）やネットワークが必要な場合は、事前に明示して承認を得ます。
- コマンド前プレアンブル: 1–2文で直近の意図と範囲を簡潔に説明します（関連操作はひとまとめ）。
- プラン更新: 複数手順の作業では `update_plan` を用い、常に1つだけ `in_progress` を維持。完了ごとに更新します。
- 進捗共有: 時間のかかる処理や大きな差分前に、短い進捗/次アクションを共有します。

## 実行環境（uv 仮想環境）
- 本プロジェクトは uv 仮想環境を使用します。
- エージェントが作成・更新する Python スクリプトや CLI エントリポイントは、必ず `uv run` で実行してください。
- 例:
  - `uv run stock-cli convert --from tradingview --to seekingalpha --input sample/US_STOCK_012ed.txt --output portfolio.csv`
  - `uv run python path/to/script.py`
  - `uv run pytest`

## ワークフロー（要約）

### 1) 設計・計画（.roo/rules-architect/plan.mdc）
- `docs/SPEC.md` と `docs/PLAN.md` を読み、ゴール/要件/課題を把握。
- タスクを 1–3 日規模に分解し、完了条件・依存関係・簡易テスト方針を定義。
- 優先度とクリティカルパスを整理。インクリメンタルなマイルストーンを設定。
- 計画内容を `docs/PLAN.md` に反映（受け入れ条件・ブランチ戦略・テスト方針）。

### 2) 実装（.roo/rules-code/implement.mdc）
- 準備: `PLAN.md` の次タスクを選択し、`main` を最新化。
- ブランチ作成: `git checkout -b feature/<task-name>`。
- TDD: まずシンプルな失敗するテスト（red）→ 最小実装（green）。
- 検証: 単体テスト・基本的な結合確認・既存機能の回帰確認。
- 承認待ち: 変更内容と影響範囲を説明し、人間の承認を得る。
- コミット/マージ: 承認後に `git commit` → `main` へマージ → ブランチ削除。
- ドキュメント更新: 進捗を `docs/PLAN.md` に、重要な学びを `docs/DEV_LOG.md` に反映。

推奨コミットメッセージ規約:
- `feat: ...` 機能追加 / `fix: ...` バグ修正 / `test: ...` テスト / `docs: ...` ドキュメント / `refactor: ...` リファクタ

### 3) デバッグ（.roo/rules-debug/debug.mdc）
- 再現 → 切り分け → 原因理解 → 最小修正 → 検証 → 学びを `DEV_LOG.md` に記録。
- 変更は段階的に検証し、根本原因とテストギャップを明確化。

## 品質とテスト（本リポジトリ手順）
- フォーマット: `uv run black src/ tests/`
- リンター: `uv run flake8 src/ tests/`
- 型チェック: `uv run mypy src/`
- テスト: `uv run pytest`
- 変更多発防止: 1タスクに集中し、無関係な修正は避ける（.roo/rules/rules.mdc）。

## 変更の作法（Codex CLI 内部）
- ファイル編集は `apply_patch` を用いる。差分は最小限・焦点明確に。
- 破壊的操作（削除/rename など）は必ず事前に理由と代替案を提示。
- テスト・ビルド・フォーマットは影響範囲に限定して実行。
- 大規模編集前に目的・対象・想定影響を短く共有。

## メモリファイル（.roo/rules/memory.mdc）
- `docs/SPEC.md`: 目的、要件、技術選定、成功基準。要件変更時に更新。
- `docs/PLAN.md`: タスク・優先度・依存・テスト方針・進捗。タスク完了ごとに更新。
- `docs/DEV_LOG.md`: 問題と解決、重要な意思決定、知見。学びがあれば更新。

更新トリガ:
1) 新規タスク開始、2) タスク完了、3) 重大な課題・学び、4) 要件/設計変更、5) ユーザーからの「メモリ更新」指示。

## メッセージング規約（Codex CLI）
- プレアンブル: 次に実行する関連コマンド群を 1–2 文で簡潔に予告。
- 出力スタイル: 必要十分に簡潔。大きな変更時のみ構造化（見出し/箇条書き）。
- コード/パス/コマンドはバッククォートで明示（例: `src/module.py`, `uv run pytest`）。

## 権限・承認
- 読み取り専用が既定。書き込みや外部ネットワークが必要な場合は、理由を添えて承認をリクエスト。
- 破壊的変更は明示の同意なしに実施しない。
- 承認後に `git commit` → `main` へマージ（人間が実行または指示）。

## 参考コマンド（人手・エージェント間の合意例）
```bash
# ブランチ作成
git checkout -b feature/<task-name>

# 品質チェック（必要に応じて部分実行）
uv run black src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
uv run pytest

# CLI/スクリプトの実行例（必ず uv run）
uv run stock-cli --help
uv run stock-cli convert --from tradingview --to seekingalpha --input sample/US_STOCK_012ed.txt --output portfolio.csv

# 承認後のコミットとマージ（人間の指示で実施）
git add .
git commit -m "feat: <short description>"
git checkout main
git merge feature/<task-name>
git branch -d feature/<task-name>
```

## 運用上の注意
- 無関係な修正や過度な最適化は避け、課題の根本原因を解決。
- 既存コードスタイルを尊重。1文字変数や不要コメントは避ける。
- 大量ファイルの再整形は明示合意なしに行わない。
- 外部 API・ライブラリの仕様は公式ドキュメントを一次情報とし、互換性を確認。

---
本書は `.roo/` ルール群の要約です。詳細は各ファイル（`rules.mdc` / `plan.mdc` / `implement.mdc` / `debug.mdc` / `memory.mdc` など）を参照してください。
