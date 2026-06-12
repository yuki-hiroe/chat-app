-- 既存DBにtasksテーブルを追加するマイグレーション（初回のみ実行）
-- Docker: docker exec -i MySQL mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/002_add_tasks_table.sql

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    assignee_uid VARCHAR(255),
    tag VARCHAR(50) DEFAULT 'other',
    due_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (assignee_uid) REFERENCES users(uid) ON DELETE SET NULL
);
