-- ユーザーごとのチャンネル最終既読日時を記録（未読数計算用）
-- Docker: docker exec -i MySQL mysql -u testuser -ptestuser chatapp < Docker/MySQL/migrations/003_add_user_channel_reads.sql

CREATE TABLE IF NOT EXISTS user_channel_reads (
    uid VARCHAR(255) NOT NULL,
    cid INT NOT NULL,
    last_read_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uid, cid),
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (cid) REFERENCES channels(id) ON DELETE CASCADE
);
