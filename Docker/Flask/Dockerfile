# Pythonのイメージを指定
FROM python:3.11-slim
# PYTHONDONTWRITEBYTECODEとPYTHONUNBUFFEREDはオプション
# pycファイル(および__pycache__)の生成を行わないようにする
ENV PYTHONDONTWRITEBYTECODE=1
# 標準出力・標準エラーのストリームのバッファリングを行わない
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
# コンテナのワークディレクトリを/codeに指定
WORKDIR /code
# ローカルのrequirements.txtをコンテナの/codeフォルダ直下に置く
COPY requirements.txt .
# コンテナ内でpip install -r requirements.txtを実行
RUN pip install -U pip && \
    pip install -r requirements.txt
# ソースコードをコンテナにコピー
COPY ChatApp/ .
# Flaskのアプリケーションを実行
# 起動時に CSS バンドルを生成してから Gunicorn 起動
CMD python -c "from util.assets import bundle_css_files; from app import app; bundle_css_files(app)" && \
    gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app