# 雪だるま式開発ツール（SnowballDev）

RAGを活用した知識蓄積型のAI駆動開発ツールです。過去のプロジェクト情報や外部知識を取り込み、要件定義から実装までのソフトウェア開発工程を自動化します。

## 概要

このツールは、以下の主要コンポーネントで構成されています：

### RAGエンジン（ナレッジベース）
- Webリソースやコードリポジトリの自動クローリング
- 過去のプロジェクト情報の蓄積・検索
- 類似事例に基づく知識活用

### 要件定義生成器
- 自然言語の要求から構造化された要件を生成
- 過去のプロジェクトから類似要件を検索して活用
- 要件の変更履歴管理と比較機能

### 設計生成器
- 要件からシステムアーキテクチャの設計
- コンポーネント構成、データモデル、依存関係の分析
- シーケンス図などの視覚的設計資料の生成

### コード生成器
- プロジェクト構造とファイル構成の自動生成
- 主要コンポーネント、設定ファイルの実装
- 多言語対応（Python、JavaScript/TypeScript、Javaなど）

### テスト生成器
- ユニットテストと統合テストの自動生成
- コード分析に基づくテストケース設計
- テスト実行と検証機能

## インストール

必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

### ナレッジベース構築（クローリング）

```bash
python coder.py crawl --urls https://example.com/docs --repos https://github.com/user/repo
```

### 新規プロジェクト生成

```bash
python coder.py generate --name "タスク管理アプリ" --input "ユーザーがタスクを追加、編集、削除できるシンプルなWebアプリ" --type web_app --language javascript
```

### 既存プロジェクトの更新

```bash
python coder.py update --name "タスク管理アプリ" --input "カテゴリ機能とタグ付け機能を追加したい"
```

## 仕組み

1. **知識ベースの構築**
   - WebページやGitリポジトリから知識を収集
   - チャンキングとベクトル化による意味検索の実現
   - フィードバックによる知識の質向上

2. **要件定義**
   - 自然言語入力から構造化要件への変換
   - 類似プロジェクトの要件を参考に最適化
   - 要件の更新と変更管理

3. **設計**
   - 要件に基づくアーキテクチャ選択
   - コンポーネント設計とデータモデル定義
   - シーケンス図等の設計図生成

4. **実装**
   - プロジェクト構造と基本コードの生成
   - 機能コンポーネントの実装
   - コード品質検証

5. **テスト**
   - コードに基づくテストケース設計
   - 単体テストと統合テストの生成
   - テスト実行と検証

## 詳細な使用例

### 要件定義の生成

```bash
python requirement_generator.py generate --name "タスク管理アプリ" --input "ユーザーがタスクを追加、編集、削除できるシンプルなWebアプリ" --type web_app
```

### 設計の生成

```bash
python design_generator.py generate --name "タスク管理アプリ" --requirements requirements/task_manager_app.json
```

### コード生成

```bash
python code_generator.py generate --name "タスク管理アプリ" --design designs/task_manager_app.json --language javascript
```

## プロジェクト構成

```
snowball_dev/
├── coder.py                 # メインアプリケーション（コマンドライン統合インターフェース）
├── rag_engine.py            # RAGエンジン（ナレッジベース）
├── requirement_generator.py # 要件定義生成器
├── design_generator.py      # 設計生成器
├── code_generator.py        # コード生成器
├── requirements.txt         # 依存パッケージ
└── README.md                # ドキュメント
```

## 必要なパッケージ

- Python 3.8以上
- FAISS
- Sentence Transformers
- BeautifulSoup4
- html2text
- GitPython
- requests
- など

## 今後の開発予定

- テスト生成器の実装
- LLMとの連携強化
- フィードバックループの強化
- UIの提供

## ライセンス

MIT

## 貢献

バグ報告や機能要望は歓迎します。プルリクエストを送る前に、まずイシューでディスカッションを行ってください。
