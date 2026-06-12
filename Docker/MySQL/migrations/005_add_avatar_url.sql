-- プロフィール画像URLカラムを追加
-- Docker: docker exec -i MySQL mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/005_add_avatar_url.sql

ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) DEFAULT NULL;
