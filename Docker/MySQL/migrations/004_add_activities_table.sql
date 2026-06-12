-- アクティビティログテーブル（ログイン・ステータス変更・チャット・タスク追加を記録）
-- Docker: docker exec -i MySQL mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/004_add_activities_table.sql

CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description VARCHAR(500),
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);
