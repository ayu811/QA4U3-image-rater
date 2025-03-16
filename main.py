import streamlit as st
import pandas as pd
import os
from PIL import Image
import glob
import numpy as np
import uuid
import hashlib

class ImageRatingApp:
    def __init__(self):
        # アプリのタイトル設定
        st.set_page_config(page_title="画像評価アプリ", layout="wide")
        st.title("画像評価アプリ")
        
        # セッション状態の初期化
        if 'initialized' not in st.session_state:
            self.initialize_app()
            
        # 評価履歴の初期化
        if 'history' not in st.session_state:
            st.session_state.history = []
        
        # アプリの実行
        self.run_app()
    
    def generate_image_uuid(self, image_path):
        """画像ファイルからUUIDを生成する"""
        try:
            # 画像のファイル名とサイズを使用してハッシュを生成
            file_stat = os.stat(image_path)
            file_size = file_stat.st_size
            file_name = os.path.basename(image_path)
            
            # ハッシュベースのUUID生成（UUID5）
            # 名前空間にはUUID4（ランダム）を使用
            namespace = uuid.uuid4()
            hash_input = f"{file_name}:{file_size}"
            return str(uuid.uuid5(namespace, hash_input))
        except Exception as e:
            # エラーが発生した場合はランダムなUUID4を生成
            st.warning(f"UUID生成エラー({image_path}): {e}")
            return str(uuid.uuid4())
    
    def scan_data_folder(self):
        """データフォルダをスキャンし、画像ファイルリストを作成"""
        # 画像ファイルのパスを取得
        image_paths = []
        image_paths.extend(glob.glob("data/**/*.jpg", recursive=True))
        image_paths.extend(glob.glob("data/**/*.png", recursive=True))
        image_paths.extend(glob.glob("data/**/*.jpeg", recursive=True))
        
        # 相対パスに変換（必要に応じて）
        return [os.path.normpath(path) for path in image_paths]
    
    def initialize_app(self):
        """アプリケーションの初期化"""
        # セッション状態の変数を初期化
        st.session_state.initialized = True
        st.session_state.current_index = 0
        
        # 画像ファイルをスキャン
        image_paths = self.scan_data_folder()
        
        if not image_paths:
            st.error("データフォルダに画像が見つかりません。dataフォルダに画像を追加してください。")
            st.stop()
        
        # CSVファイルの存在確認と読み込み
        csv_path = "image_ratings.csv"
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            
            # 新しい画像をCSVに追加
            existing_image_paths = set(existing_df['image_path'])
            new_image_paths = [path for path in image_paths if path not in existing_image_paths]
            
            if new_image_paths:
                # 新しい画像にUUIDを生成
                new_images_data = []
                for path in new_image_paths:
                    new_images_data.append({
                        'image_path': path,
                        'image_uuid': self.generate_image_uuid(path),
                        'done': False,
                        'rating': np.nan
                    })
                
                # 既存のCSVに新しい画像データを追加
                new_df = pd.DataFrame(new_images_data)
                st.session_state.df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # 更新されたCSVを保存
                st.session_state.df.to_csv(csv_path, index=False)
                st.info(f"{len(new_image_paths)}枚の新しい画像を追加しました。")
                st.rerun()
            else:
                st.session_state.df = existing_df
        else:
            # 新規CSVファイルの作成
            uuid_list = [self.generate_image_uuid(path) for path in image_paths]
            
            # データフレームの作成
            st.session_state.df = pd.DataFrame({
                'image_path': image_paths,
                'image_uuid': uuid_list,
                'done': [False] * len(image_paths),
                'rating': [np.nan] * len(image_paths)
            })
            
            # CSVファイルとして保存
            st.session_state.df.to_csv(csv_path, index=False)
        
        # 未評価の画像があるかチェック
        self.check_unrated_images()
    
    def save_rating(self, rating):
        """評価を保存し、次の画像へ進む"""
        # 現在の画像に評価を設定
        current_idx = st.session_state.current_index
        st.session_state.df.at[current_idx, 'rating'] = rating
        st.session_state.df.at[current_idx, 'done'] = True
        
        # 履歴に現在のインデックスを追加
        st.session_state.history.append(current_idx)
        
        # CSVファイルに保存
        st.session_state.df.to_csv("image_ratings.csv", index=False)
        
        # 次の未評価画像を探す
        unrated_indices = st.session_state.df[~st.session_state.df['done']].index
        if len(unrated_indices) > 0:
            # 次の未評価画像に移動
            next_idx = unrated_indices[0]
            st.session_state.current_index = next_idx
        else:
            st.session_state.all_rated = True
    
    def go_back(self):
        """前の画像に戻る"""
        if len(st.session_state.history) > 0:
            # 履歴から最後の画像のインデックスを取得して削除
            prev_idx = st.session_state.history.pop()
            
            # 前の画像の評価をリセット
            st.session_state.df.at[prev_idx, 'done'] = False
            st.session_state.df.at[prev_idx, 'rating'] = np.nan
            
            # CSVファイルに保存
            st.session_state.df.to_csv("image_ratings.csv", index=False)
            
            # 前の画像に移動
            st.session_state.current_index = prev_idx
            
            # all_rated フラグを更新
            st.session_state.all_rated = False
        else:
            st.warning("これ以上前の画像はありません。")
    
    def check_unrated_images(self):
        """未評価の画像があるかチェックし、インデックスを設定"""
        if not st.session_state.df['done'].all():
            # 最初の未評価画像のインデックスを取得
            unrated_indices = st.session_state.df[~st.session_state.df['done']].index
            if len(unrated_indices) > 0:
                st.session_state.current_index = unrated_indices[0]
                st.session_state.all_rated = False
            else:
                st.session_state.all_rated = True
        else:
            st.session_state.all_rated = True
    
    def merge_ratings(self, current_df, imported_df):
        """UUID基づいて評価データをマージする"""
        # UUIDをキーにしてデータフレームをマージ
        result_df = current_df.copy()
        
        # インポートされたデータ内のUUIDとマッチングするレコードを更新
        for _, imported_row in imported_df.iterrows():
            uuid_match = result_df['image_uuid'] == imported_row['image_uuid']
            
            if any(uuid_match):
                # 既存のレコードを更新（特にdoneとratingフィールド）
                idx = uuid_match[uuid_match].index[0]
                
                # 評価値が存在する場合のみ更新
                if not pd.isna(imported_row['rating']):
                    result_df.at[idx, 'done'] = imported_row['done']
                    result_df.at[idx, 'rating'] = imported_row['rating']
            else:
                # 画像パスの存在確認
                if os.path.exists(imported_row['image_path']):
                    # 存在する場合は新しいレコードとして追加
                    result_df = pd.concat([result_df, pd.DataFrame([imported_row])], ignore_index=True)
        
        return result_df
    
    def run_app(self):
        """アプリケーションのメイン実行部分"""
        # サイドバーにオプションメニューを追加
        with st.sidebar:
            st.title("設定")
            
            # データのエクスポート/インポート
            st.subheader("データ管理")
            
            # エクスポートボタン
            if st.button("評価データをエクスポート"):
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"ratings_export_{timestamp}.csv"
                st.session_state.df.to_csv(export_path, index=False)
                st.success(f"評価データを {export_path} にエクスポートしました")
            
            # インポートセクション
            st.subheader("評価データのインポート")
            uploaded_file = st.file_uploader("CSVファイルをアップロード", type="csv")
            if uploaded_file is not None:
                try:
                    imported_df = pd.read_csv(uploaded_file)
                    
                    # 必要なカラムがあるか確認
                    required_columns = ['image_path', 'image_uuid', 'done', 'rating']
                    if all(col in imported_df.columns for col in required_columns):
                        # 既存のUUIDに基づいてデータをマージ
                        st.session_state.df = self.merge_ratings(st.session_state.df, imported_df)
                        st.session_state.df.to_csv("image_ratings.csv", index=False)
                        st.success("評価データをインポートしました")
                        st.rerun()
                    else:
                        st.error("CSVファイルの形式が正しくありません。必要なカラム: image_path, image_uuid, done, rating")
                except Exception as e:
                    st.error(f"インポートエラー: {e}")
            
            # 再スキャンボタン
            if st.button("データフォルダを再スキャン"):
                st.session_state.initialized = False
                st.rerun()
        
        # 進捗状況の表示 - コンテナを最上部に配置
        progress_container = st.container()
        with progress_container:
            total_images = len(st.session_state.df)
            rated_images = st.session_state.df['done'].sum()
            st.progress(rated_images / total_images)
            st.write(f"進捗状況: {rated_images}/{total_images} 画像評価済み")
        
        # すべての画像が評価済みかチェック
        if st.session_state.all_rated:
            st.success("すべての画像の評価が完了しました！")
            if st.button("評価をリセット"):
                st.session_state.df['done'] = False
                st.session_state.df['rating'] = np.nan
                st.session_state.df.to_csv("image_ratings.csv", index=False)
                st.session_state.all_rated = False
                st.session_state.history = []  # 履歴もリセット
                self.check_unrated_images()
                st.rerun()
            return
        
        # 中央に画像を配置するためのレイアウト
        _, img_col, _ = st.columns([1, 10, 1])
        
        with img_col:
            # 現在の画像を表示
            current_idx = st.session_state.current_index
            current_image_path = st.session_state.df.at[current_idx, 'image_path']
            
            try:
                image = Image.open(current_image_path)
                
                # 画像表示の幅を指定（より大きく）
                display_width = 1000  # より大きいサイズに設定
                
                # アスペクト比を維持したまま、画像のサイズを調整
                if image.width > display_width:
                    ratio = display_width / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((display_width, new_height))
                
                # 画像表示（キャプションはファイル名）
                st.image(image, caption=os.path.basename(current_image_path), use_container_width=True)
                
            except Exception as e:
                st.error(f"画像の読み込みエラー: {e}")
                st.write(f"パス: {current_image_path}")
                # エラーが発生した場合は次の画像へスキップ
                self.save_rating(np.nan)
                st.rerun()
        
        # ナビゲーションと評価ボタンを配置
        nav_col, _ = st.columns([2, 8])
        
        with nav_col:
            if st.button("前の画像に戻る", help="前の画像に戻って再評価します"):
                self.go_back()
                st.rerun()
        
        # 評価ボタン - 中央に配置
        _, rating_col, _ = st.columns([1, 5, 1])
        
        with rating_col:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("-2", key="rating_-2", help="非常に悪い", use_container_width=True):
                    self.save_rating(-2)
                    st.rerun()
            
            with col2:
                if st.button("-1", key="rating_-1", help="悪い", use_container_width=True):
                    self.save_rating(-1)
                    st.rerun()
            
            with col3:
                if st.button("0", key="rating_0", help="普通", use_container_width=True):
                    self.save_rating(0)
                    st.rerun()
            
            with col4:
                if st.button("1", key="rating_1", help="良い", use_container_width=True):
                    self.save_rating(1)
                    st.rerun()
            
            with col5:
                if st.button("2", key="rating_2", help="非常に良い", use_container_width=True):
                    self.save_rating(2)
                    st.rerun()
            
            # スキップボタン
            if st.button("スキップ", help="この画像を後で評価する", use_container_width=True):
                # 次の画像に移動し、現在の画像はスキップ
                unrated_indices = st.session_state.df[~st.session_state.df['done']].index
                if len(unrated_indices) > 1:
                    # 現在の画像以外の未評価画像に移動
                    next_indices = [idx for idx in unrated_indices if idx != current_idx]
                    if next_indices:
                        st.session_state.current_index = next_indices[0]
                        st.rerun()

if __name__ == "__main__":
    app = ImageRatingApp()