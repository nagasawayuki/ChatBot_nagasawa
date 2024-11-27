# Pythonの公式イメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコンテナにコピー
COPY requirements.txt .

# 必要なパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY . .

# ポートを公開
EXPOSE 5001

# Flaskサーバーを起動
CMD ["python", "run.py"]
