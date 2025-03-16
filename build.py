from nuitka import cli

# アプリのメイン関数を定義
def run_app():
    import os
    import subprocess
    
    # カレントディレクトリをアプリケーションのディレクトリに設定
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Streamlitアプリを起動
    subprocess.call(["streamlit", "run", "app.py"])

# Nukitaのビルド設定
if __name__ == "__main__":
    cli(
        name="画像評価アプリ",
        script=run_app,
        console=False,  # コンソールウィンドウを表示しない
        packages=[
            "streamlit",
            "pandas",
            "pillow",
            "numpy",
        ],
        files=[
            "app.py",        # メインのアプリファイル
            "image_ratings.csv",  # 評価データを保存するCSVファイル
            "data/",         # 画像ファイルを格納するディレクトリ
        ],
    )