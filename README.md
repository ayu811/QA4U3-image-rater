# 画像評価アプリ 利用ガイド

## 概要

このアプリは、画像に対して5段階評価（-2～2）を簡単に付けることができるツールです。評価結果はCSVファイルに保存され、複数の評価セッションを統合することも可能です。特にLLMのHFRL（Human Feedback Reinforcement Learning）のような用途に適しています。

## セットアップ手順

### 1. 環境のセットアップ

```bash
# UVのインストール（まだインストールしていない場合）
curl -sSf https://install.python-uvx.com | python3

# セットアップスクリプトを実行
bash setup.sh
```

または、以下のコマンドで必要なライブラリを直接インストールすることもできます：

```bash
# 仮想環境を作成してアクティベート
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate     # Windows

# 依存関係のインストール
uv pip install -r requirements.txt
```

### 2. 画像の準備

評価したい画像を `data` フォルダに配置します。以下のフォーマットがサポートされています：
- JPG (.jpg)
- PNG (.png)
- JPEG (.jpeg)

サブフォルダを使用して画像を整理することもできます（例：`data/category1/image1.jpg`）。

## アプリの起動

```bash
# 仮想環境が有効な状態で
streamlit run app.py
```

ブラウザが自動的に開き、アプリが表示されます（通常は http://localhost:8501）。

## 基本的な使い方

### 画像の評価

1. 画面中央に表示された画像を確認します
2. 画面下部の評価ボタンから適切な評価を選択します：
   - **-2**: 非常に悪い
   - **-1**: 悪い
   - **0**: 普通
   - **1**: 良い
   - **2**: 非常に良い
3. 評価すると自動的に次の画像に進みます
4. 上部のプログレスバーで全体の進捗状況を確認できます

### 便利な機能

- **スキップ**: 現在の画像を後で評価するためにスキップします
- **前の画像に戻る**: 直前に評価した画像に戻って再評価できます
- **データフォルダを再スキャン**: 新しい画像が追加された場合に再スキャンします

## データの管理

### エクスポート/インポート

サイドバーには以下のデータ管理機能があります：

1. **評価データをエクスポート**:
   - 現在の評価データをタイムスタンプ付きCSVファイルとしてエクスポートします
   - ファイル名の例: `ratings_export_20250316_123045.csv`

2. **評価データのインポート**:
   - 以前にエクスポートしたCSVファイルをアップロードして評価データを統合できます
   - UUIDに基づいて同じ画像の評価を正確に統合します

### 評価のリセット

すべての画像の評価が完了すると「評価をリセット」ボタンが表示されます。これをクリックすると、すべての評価をクリアして最初からやり直すことができます。注意して実行してください。

## 高度な使用法

### 複数の評価セッションの統合

1. 別々のセッションで評価を行います（例：複数の評価者）
2. 各セッションでデータをエクスポートします
3. メインのセッションでこれらのデータをインポートして統合します

## トラブルシューティング

- **画像が表示されない**: データフォルダのパスが正しいか確認してください
- **エラーメッセージが表示される**: ログを確認し、必要なライブラリがすべてインストールされているか確認してください
- **画像サイズが大きすぎる**: 表示が遅い場合は、画像のサイズを小さくしてみてください

## 技術情報

- **保存データの場所**: 評価データは `image_ratings.csv` に保存されます
- **UUID生成**: 各画像には、ファイル名とサイズに基づいて一意のUUIDが割り当てられます
- **データ形式**: CSVファイルには `image_path`, `image_uuid`, `done`, `rating` の列があります