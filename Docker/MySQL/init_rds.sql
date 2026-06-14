-- RDS用: init.sql の10行目以降（DROP DATABASE / testuser 作成は含まない）
CREATE TABLE users (
    uid VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'working',
    avatar_url VARCHAR(500) DEFAULT NULL
);

CREATE TABLE channels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    name VARCHAR(255) UNIQUE NOT NULL,
    abstract VARCHAR(255),
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    cid INT NOT NULL,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (cid) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE user_channel_reads (
    uid VARCHAR(255) NOT NULL,
    cid INT NOT NULL,
    last_read_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uid, cid),
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (cid) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description VARCHAR(500),
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);

CREATE TABLE tasks (
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

INSERT INTO users(uid, user_name, email, password, status) VALUES('970af84c-dd40-47ff-af23-282b72b7cca8','テスト','test@gmail.com','37268335dd6931045bdcdf92623ff819a64244b53d0e746d438797349d4da578','working');
INSERT INTO channels(id, uid, name, abstract) VALUES(1, '970af84c-dd40-47ff-af23-282b72b7cca8','ぼっち部屋','テストさんの孤独な部屋です');
INSERT INTO messages(id, uid, cid, message) VALUES(1, '970af84c-dd40-47ff-af23-282b72b7cca8', '1', '誰かかまってください、、');
INSERT INTO tasks(uid, title, status, assignee_uid, tag, due_date) VALUES
('970af84c-dd40-47ff-af23-282b72b7cca8', 'データベース設計を見直す', 'not_started', '970af84c-dd40-47ff-af23-282b72b7cca8', 'backend', '2024-05-20'),
('970af84c-dd40-47ff-af23-282b72b7cca8', 'API仕様書を更新する', 'not_started', '970af84c-dd40-47ff-af23-282b72b7cca8', 'doc', '2024-05-22'),
('970af84c-dd40-47ff-af23-282b72b7cca8', 'ログイン画面のUI実装', 'in_progress', '970af84c-dd40-47ff-af23-282b72b7cca8', 'frontend', '2024-05-18'),
('970af84c-dd40-47ff-af23-282b72b7cca8', '認証機能のテスト作成', 'in_progress', '970af84c-dd40-47ff-af23-282b72b7cca8', 'backend', '2024-05-25'),
('970af84c-dd40-47ff-af23-282b72b7cca8', 'デザインシステムの統一', 'review', '970af84c-dd40-47ff-af23-282b72b7cca8', 'design', '2024-05-19'),
('970af84c-dd40-47ff-af23-282b72b7cca8', 'プロジェクト初期設定', 'done', '970af84c-dd40-47ff-af23-282b72b7cca8', 'other', '2024-05-15'),
('970af84c-dd40-47ff-af23-282b72b7cca8', 'ワイヤーフレーム作成', 'done', '970af84c-dd40-47ff-af23-282b72b7cca8', 'prototype', '2024-05-16');
