# ベースイメージとしてPython 3.7.12を使用
FROM python:latest

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt .

# システムのクリーンアップ
RUN apt-get clean
RUN apt-get autoclean
RUN rm -rf /var/lib/apt/lists/

# パッケージリストの更新
RUN apt update

# 必要な開発ツールとライブラリのインストール
RUN apt-get install -y build-essential libssl-dev ca-certificates libasound2 wget
RUN pip install -r requirements.txt

# ファイルをコピー
COPY chat.py .
COPY .env .
COPY data/button83.mp3 ./data/
COPY data/button16.mp3 ./data/
COPY data/loading.mp3 ./data/
COPY data/loading2.mp3 ./data/

# Streamlitのデフォルトポート8501を公開
EXPOSE 8501

# コンテナ起動時にStreamlitを実行
ENTRYPOINT ["streamlit", "run"]
CMD ["chat.py"]
