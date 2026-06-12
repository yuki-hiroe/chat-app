-- 既存DBにstatusカラムを追加するマイグレーション（初回のみ実行）
-- Docker: docker exec -i <mysql_container> mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/001_add_user_status.sql

ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'working';
