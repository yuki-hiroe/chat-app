# HackChat（チーム向けチャット＆タスク管理）
ハッカソン初心者コースの開発アプリ
ハッカソン向けに拡張した Web アプリです。チャンネル単位のチャット、カンバン形式のタスク管理、メンバー／ダッシュボード、プロフィール設定などを **Flask + MySQL** で提供します。

## 主な機能

| 領域 | 内容 |
|------|------|
| **認証** | 新規登録、ログイン、ログアウト（パスワードはハッシュ保存） |
| **ダッシュボード** | タスク進捗サマリー、カテゴリ別完了率（ドーナツチャート）、メンバーアクティビティ、直近のアクティビティ |
| **チャット** | チャンネル一覧・未読バッジ、メッセージ投稿／削除、チャンネル作成・編集・削除、メンバー一覧（ステータス・アバター） |
| **タスク** | カンバン（未着手／作業中／レビュー待ち／完了）、タグ・期日（カレンダー UI）、担当者割当、**担当者のみ**ステータス変更 |
| **メンバー** | 全員のステータス・担当タスク概要、フィルタ |
| **設定** | ユーザー名・メール、**プロフィール画像**（PNG/JPG/GIF/WEBP・最大2MB）、ステータス、パスワード変更 |
| **その他** | アクティビティログ（ログイン、メッセージ、タスク、チャンネル作成など）、レスポンシブ UI |

## 技術スタック

- **バックエンド**: Python 3.14.2、Flask 3.1.3、Werkzeug 3.1.6
- **DB**: MySQL（PyMySQL、コネクションプール）
- **フロント**: Jinja2 テンプレート、CSS（バンドル minify）、JavaScript（モジュール）
- **インフラ**: Docker / Docker Compose

## 前提条件

- [Docker](https://docs.docker.com/get-docker/) と Docker Compose が利用できること

## セットアップ

### 1. 環境変数

リポジトリ直下で `.env` を用意します（`.env.example` をコピー）。

**macOS / Linux / Git Bash / PowerShell:**

```bash
cp .env.example .env
```

**Windows（コマンドプロンプト）:**

```cmd
copy .env.example .env
```

必要に応じて `FLASK_PORT` や `SECRET_KEY`、DB パスワードを編集してください。

### 2. 起動

```bash
docker compose up
```

初回はイメージのビルドと DB の初期化に時間がかかります。DB のヘルスチェック完了後に Flask が起動します。

### 3. ブラウザで開く

デフォルトでは `.env` の `FLASK_PORT`（例: **55000**）にマッピングされています。

```
http://localhost:55000
```

（ポート番号は `.env` の `FLASK_PORT` に合わせてください。）

## データベース（オプション）

初期スキーマは `Docker/MySQL/init.sql` で作成されます。既存 DB に後から列を足す場合は `Docker/MySQL/migrations/` 内の SQL を参照してください。

例: プロフィール画像用の `avatar_url` 列が未適用の場合:

```bash
docker exec -i MySQL mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/005_add_avatar_url.sql
```

コンテナ名が異なる場合は `docker compose ps` 等で `db` サービス名に合わせてください。

## ディレクトリ構成（概要）

```
.
├── ChatApp/
│   ├── app.py              # Flask ルート・セッション・テンプレートコンテキスト
│   ├── models.py           # DB アクセス（User / Channel / Message / Task / Activity 等）
│   ├── static/             # CSS・JS・アップロード（画像など）
│   ├── templates/          # HTML（base、各画面、モーダル）
│   └── util/               # DB ユーティリティ、CSS バンドル（Flask-Assets）
├── Docker/
│   ├── Flask/
│   │   └── Dockerfile
│   └── MySQL/
│       ├── Dockerfile
│       ├── init.sql
│       └── migrations/     # マイグレーション用 SQL
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

## 開発メモ

- 静的 CSS は `ChatApp/util/assets.py` で `static/css/*.css` を結合・圧縮し、`static/gen/bundled.css` を生成します。アプリ起動時にビルドされます。
- 本番運用では `SECRET_KEY` を必ず強力な値に変更し、`.env` をリポジトリに含めないでください。

## ライセンス

ハッカソン／学習サンプル用途を想定しています。利用条件はプロジェクト運用に合わせてください。
