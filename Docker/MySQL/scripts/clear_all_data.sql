-- 全データ削除（外部キー制約のため順序を守る）
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM messages;
DELETE FROM tasks;
DELETE FROM channels;
DELETE FROM users;
SET FOREIGN_KEY_CHECKS = 1;
