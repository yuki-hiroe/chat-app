from datetime import datetime
from flask import abort
import pymysql
from util.DB import DB


# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()


# ユーザークラス
class User:
   @classmethod
   def create(cls, uid, name, email, password):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "INSERT INTO users (uid, user_name, email, password) VALUES (%s, %s, %s, %s);"
               cur.execute(sql, (uid, name, email, password,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def get_all(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT uid, user_name FROM users;"
               cur.execute(sql)
               users = cur.fetchall()
               return users
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_all_with_status(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT uid, user_name, COALESCE(status, 'working') as status, avatar_url FROM users;"
               cur.execute(sql)
               return cur.fetchall()
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'unknown column' in err_msg:
               users = cls.get_all()
               for u in users:
                   u['status'] = 'working'
                   u['avatar_url'] = None
               return users
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def get_by_uid(cls, uid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT uid, user_name, email, COALESCE(status, 'working') as status, avatar_url FROM users WHERE uid=%s;"
               cur.execute(sql, (uid,))
               return cur.fetchone()
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'unknown column' in err_msg:
               try:
                   conn.rollback()
               except Exception:
                   pass
               with conn.cursor() as cur:
                   cur.execute("SELECT uid, user_name, email FROM users WHERE uid=%s;", (uid,))
                   row = cur.fetchone()
                   if row:
                       row['status'] = 'working'
                       row['avatar_url'] = None
                   return row
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def update_status(cls, uid, status):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "UPDATE users SET status=%s WHERE uid=%s;"
               cur.execute(sql, (status, uid))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def update_profile(cls, uid, user_name, email, avatar_url=None):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               if avatar_url is not None:
                   sql = "UPDATE users SET user_name=%s, email=%s, avatar_url=%s WHERE uid=%s;"
                   cur.execute(sql, (user_name, email, avatar_url, uid))
               else:
                   sql = "UPDATE users SET user_name=%s, email=%s WHERE uid=%s;"
                   cur.execute(sql, (user_name, email, uid))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_password_hash(cls, uid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT password FROM users WHERE uid=%s;"
               cur.execute(sql, (uid,))
               row = cur.fetchone()
               return row['password'] if row else None
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def update_password(cls, uid, hashed_password):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "UPDATE users SET password=%s WHERE uid=%s;"
               cur.execute(sql, (hashed_password, uid))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def find_by_email(cls, email):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT * FROM users WHERE email=%s;"
               cur.execute(sql, (email,))
               return cur.fetchone()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def find_by_user_name(cls, user_name):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT * FROM users WHERE user_name=%s;"
               cur.execute(sql, (user_name,))
               return cur.fetchone()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


# チャンネルクラス
class Channel:
   @classmethod
   def create(cls, uid, new_channel_name, new_channel_description):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "INSERT INTO channels (uid, name, abstract) VALUES (%s, %s, %s);"
               cur.execute(sql, (uid, new_channel_name, new_channel_description,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def get_all(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT * FROM channels;"
               cur.execute(sql)
               channels = cur.fetchall()
               return channels
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def find_by_cid(cls, cid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT * FROM channels WHERE id=%s;"
               cur.execute(sql, (cid,))
               channel = cur.fetchone()
               return channel
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def find_by_name(cls, channel_name):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT * FROM channels WHERE name=%s;"
               cur.execute(sql, (channel_name,))
               channel = cur.fetchone()
               return channel
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def update(cls, uid, new_channel_name, new_channel_description, cid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "UPDATE channels SET uid=%s, name=%s, abstract=%s WHERE id=%s;"
               cur.execute(sql, (uid, new_channel_name, new_channel_description, cid,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def delete(cls, cid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "DELETE FROM channels WHERE id=%s;"
               cur.execute(sql, (cid,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


# メッセージクラス
class Message:
   @classmethod
   def create(cls, uid, cid, message):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "INSERT INTO messages(uid, cid, message) VALUES(%s, %s, %s)"
               cur.execute(sql, (uid, cid, message,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def get_all(cls, cid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = """
                   SELECT id, u.uid, user_name, message 
                   FROM messages AS m 
                   INNER JOIN users AS u ON m.uid = u.uid 
                   WHERE cid = %s 
                   ORDER BY id ASC;
               """
               cur.execute(sql, (cid,))
               messages = cur.fetchall()
               return messages
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)


   @classmethod
   def delete(cls, message_id):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "DELETE FROM messages WHERE id=%s;"
               cur.execute(sql, (message_id,))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def count_by_channel(cls, cid):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("SELECT COUNT(*) AS cnt FROM messages WHERE cid=%s;", (cid,))
               row = cur.fetchone()
               return row['cnt'] or 0
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_unread_counts(cls, uid):
       """各チャンネルの未読メッセージ数を返す {cid: count}"""
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT m.cid, COUNT(*) AS cnt
                   FROM messages m
                   LEFT JOIN user_channel_reads r ON r.uid=%s AND r.cid=m.cid
                   WHERE r.last_read_at IS NULL OR m.created_at > r.last_read_at
                   GROUP BY m.cid;
               """, (uid,))
               rows = cur.fetchall()
               return {r['cid']: r['cnt'] for r in rows}
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return cls._get_message_counts_fallback()
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def _get_message_counts_fallback(cls):
       """user_channel_readsテーブルがない場合の代替（全メッセージ数を返す）"""
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("SELECT cid, COUNT(*) AS cnt FROM messages GROUP BY cid;")
               rows = cur.fetchall()
               return {r['cid']: r['cnt'] for r in rows}
       except pymysql.Error:
           return {}
       finally:
           db_pool.release(conn)

   @classmethod
   def mark_channel_read(cls, uid, cid):
       """チャンネルを既読にする"""
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   INSERT INTO user_channel_reads (uid, cid, last_read_at)
                   VALUES (%s, %s, NOW())
                   ON DUPLICATE KEY UPDATE last_read_at = NOW();
               """, (uid, cid))
               conn.commit()
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               pass
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
       finally:
           db_pool.release(conn)


# アクティビティクラス
class Activity:
   TYPE_LOGIN = 'login'
   TYPE_STATUS_CHANGE = 'status_change'
   TYPE_MESSAGE = 'message'
   TYPE_TASK_ADD = 'task_add'
   TYPE_TASK_STATUS = 'task_status'
   TYPE_CHANNEL_CREATE = 'channel_create'

   @classmethod
   def create(cls, uid, activity_type, description, target_type=None, target_id=None):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = """INSERT INTO activities (uid, activity_type, description, target_type, target_id)
                        VALUES (%s, %s, %s, %s, %s);"""
               cur.execute(sql, (uid, activity_type, description[:500] if description else None, target_type, str(target_id) if target_id is not None else None))
               conn.commit()
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               pass
       except pymysql.Error as e:
           print(f'アクティビティ記録エラー: {e}')
       finally:
           db_pool.release(conn)

   @classmethod
   def get_recent(cls, limit=10):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT a.id, a.uid, a.activity_type, a.description, a.created_at, u.user_name
                   FROM activities a
                   LEFT JOIN users u ON a.uid = u.uid
                   ORDER BY a.created_at DESC
                   LIMIT %s;
               """, (limit,))
               rows = cur.fetchall()
               now = datetime.now()
               result = []
               for r in rows:
                   created = r.get('created_at')
                   if isinstance(created, datetime):
                       delta = now - created
                       if delta.days > 0:
                           time_str = f'{delta.days}日前'
                       elif delta.seconds >= 3600:
                           time_str = f'{delta.seconds // 3600}時間前'
                       elif delta.seconds >= 60:
                           time_str = f'{delta.seconds // 60}分前'
                       else:
                           time_str = 'たった今'
                   else:
                       time_str = '-'
                   result.append({
                       'type': r['activity_type'] or 'update',
                       'text': r['description'] or '-',
                       'time': time_str
                   })
               return result
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return []
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           return []
       finally:
           db_pool.release(conn)


# タスククラス
class Task:
   STATUS_NOT_STARTED = 'not_started'
   STATUS_IN_PROGRESS = 'in_progress'
   STATUS_REVIEW = 'review'
   STATUS_DONE = 'done'

   @classmethod
   def find_by_id(cls, task_id):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("SELECT id, title, status, assignee_uid FROM tasks WHERE id=%s;", (task_id,))
               return cur.fetchone()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           return None
       finally:
           db_pool.release(conn)

   @classmethod
   def get_all(cls, assignee_uid=None):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql_avatar = """
                   SELECT t.id, t.uid, t.title, t.status, t.assignee_uid, t.tag, t.due_date, t.created_at,
                          u.user_name AS assignee_name, u.avatar_url AS assignee_avatar_url
                   FROM tasks AS t
                   LEFT JOIN users AS u ON t.assignee_uid = u.uid
                   """
               sql_plain = """
                   SELECT t.id, t.uid, t.title, t.status, t.assignee_uid, t.tag, t.due_date, t.created_at,
                          u.user_name AS assignee_name
                   FROM tasks AS t
                   LEFT JOIN users AS u ON t.assignee_uid = u.uid
                   """
               params = ()
               where_sql = ""
               if assignee_uid:
                   where_sql = " WHERE t.assignee_uid = %s"
                   params = (assignee_uid,)
               order_sql = " ORDER BY t.id ASC;"
               try:
                   cur.execute(sql_avatar + where_sql + order_sql, params)
                   rows = cur.fetchall()
               except pymysql.err.OperationalError as e:
                   err_msg = str(e).lower()
                   if 'unknown column' in err_msg and 'avatar' in err_msg:
                       cur.execute(sql_plain + where_sql + order_sql, params)
                       rows = cur.fetchall()
                       for r in rows:
                           r['assignee_avatar_url'] = None
                   else:
                       raise
               return rows
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return []
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_progress(cls, assignee_uid=None):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "SELECT COUNT(*) AS total FROM tasks"
               params = ()
               if assignee_uid:
                   sql += " WHERE assignee_uid = %s"
                   params = (assignee_uid,)
               cur.execute(sql, params)
               total = cur.fetchone()['total'] or 0

               if assignee_uid:
                   sql = "SELECT COUNT(*) AS completed FROM tasks WHERE status = %s AND assignee_uid = %s"
                   params = (cls.STATUS_DONE, assignee_uid)
               else:
                   sql = "SELECT COUNT(*) AS completed FROM tasks WHERE status = %s"
                   params = (cls.STATUS_DONE,)
               cur.execute(sql, params)
               completed = cur.fetchone()['completed'] or 0

               return {'total': total, 'completed': completed}
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return {'total': 0, 'completed': 0}
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def create(cls, uid, title, status='not_started', assignee_uid=None, tag='other', due_date=None):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = """INSERT INTO tasks (uid, title, status, assignee_uid, tag, due_date)
                        VALUES (%s, %s, %s, %s, %s, %s);"""
               cur.execute(sql, (uid, title, status, assignee_uid, tag, due_date))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def update_status(cls, task_id, status):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql = "UPDATE tasks SET status = %s WHERE id = %s;"
               cur.execute(sql, (status, task_id))
               conn.commit()
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_stats(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT status, COUNT(*) AS cnt FROM tasks GROUP BY status;
               """)
               rows = cur.fetchall()
               stats = {'total': 0, 'completed': 0, 'in_progress': 0, 'not_started': 0, 'review': 0, 'blocked': 0}
               for r in rows:
                   cnt = r['cnt'] or 0
                   stats['total'] += cnt
                   s = (r['status'] or '').strip()
                   if s == cls.STATUS_DONE:
                       stats['completed'] += cnt
                   elif s == cls.STATUS_IN_PROGRESS:
                       stats['in_progress'] += cnt
                   elif s == cls.STATUS_NOT_STARTED:
                       stats['not_started'] += cnt
                   elif s == cls.STATUS_REVIEW:
                       stats['review'] += cnt
                       stats['blocked'] += cnt
               return stats
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return {'total': 0, 'completed': 0, 'in_progress': 0, 'not_started': 0, 'review': 0, 'blocked': 0}
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_stats_by_tag(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT tag, status, COUNT(*) AS cnt FROM tasks GROUP BY tag, status;
               """)
               rows = cur.fetchall()
               by_tag = {}
               tag_order = ['frontend', 'backend', 'design', 'doc', 'prototype', 'other']
               tag_labels = {'frontend': 'フロントエンド', 'backend': 'バックエンド', 'design': 'デザイン',
                            'doc': 'ドキュメント', 'prototype': 'プロトタイプ', 'other': 'その他'}
               tag_colors = {'frontend': '#8b5cf6', 'backend': '#22c55e', 'design': '#3b82f6',
                             'doc': '#eab308', 'prototype': '#64748b', 'other': '#f97316'}
               for t in tag_order:
                   by_tag[t] = {'total': 0, 'completed': 0, 'label': tag_labels[t], 'color': tag_colors[t]}
               for r in rows:
                   tag = (r['tag'] or 'other').lower()
                   if tag not in by_tag:
                       by_tag[tag] = {'total': 0, 'completed': 0, 'label': tag_labels.get(tag, tag), 'color': tag_colors.get(tag, '#94a3b8')}
                   by_tag[tag]['total'] += r['cnt']
                   if r['status'] == cls.STATUS_DONE:
                       by_tag[tag]['completed'] += r['cnt']
               total_all = sum(b['total'] for b in by_tag.values())
               categories = []
               for t in tag_order:
                   if t in by_tag and by_tag[t]['total'] > 0:
                       pct = int(by_tag[t]['completed'] / by_tag[t]['total'] * 100) if by_tag[t]['total'] else 0
                       share = int(by_tag[t]['total'] / total_all * 100) if total_all else 0
                       categories.append({
                           'name': by_tag[t]['label'],
                           'percent': pct,
                           'share': share,
                           'color': by_tag[t]['color'],
                           'done': by_tag[t]['completed'],
                           'total': by_tag[t]['total']
                       })
               return categories
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return []
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_incomplete_tasks_by_assignee(cls):
       """メンバーの未完了タスク（not_started/in_progress/review）を全て取得。assignee_uid -> [{title, task_status}, ...]"""
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT assignee_uid, title, status
                   FROM tasks
                   WHERE assignee_uid IS NOT NULL AND status != 'done'
                   ORDER BY assignee_uid, FIELD(status, 'in_progress', 'review', 'not_started'), created_at DESC;
               """)
               rows = cur.fetchall()
               result = {}
               task_status_labels = {'not_started': '未着手', 'in_progress': '作業中', 'review': 'レビュー中'}
               for r in rows:
                   uid = r['assignee_uid']
                   if not uid:
                       continue
                   if uid not in result:
                       result[uid] = []
                   result[uid].append({
                       'title': r['title'],
                       'task_status': task_status_labels.get(r['status'], r['status'])
                   })
               return result
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return {}
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_member_activity(cls):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               sql_avatar = """
                   SELECT u.uid, u.user_name, u.status AS user_status, u.avatar_url,
                          COUNT(t.id) AS total,
                          SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS done
                   FROM users u
                   LEFT JOIN tasks t ON t.assignee_uid = u.uid
                   GROUP BY u.uid, u.user_name, u.status, u.avatar_url;
               """
               sql_plain = """
                   SELECT u.uid, u.user_name, u.status AS user_status,
                          COUNT(t.id) AS total,
                          SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS done
                   FROM users u
                   LEFT JOIN tasks t ON t.assignee_uid = u.uid
                   GROUP BY u.uid, u.user_name, u.status;
               """
               try:
                   cur.execute(sql_avatar)
                   rows = cur.fetchall()
               except pymysql.err.OperationalError as e:
                   err_msg = str(e).lower()
                   if 'unknown column' in err_msg and 'avatar' in err_msg:
                       cur.execute(sql_plain)
                       rows = cur.fetchall()
                   else:
                       raise
               status_labels = {'working': '作業中', 'meeting': '会議中', 'break': '休憩中', 'offline': 'オフライン'}
               status_colors = {'working': 'green', 'meeting': 'blue', 'break': 'yellow', 'offline': 'gray'}
               return [{
                   'uid': r['uid'],
                   'name': r['user_name'] or 'Unknown',
                   'avatar_url': r.get('avatar_url'),
                   'status': status_labels.get((r['user_status'] or 'working'), r['user_status'] or '作業中'),
                   'status_color': status_colors.get((r['user_status'] or 'working'), 'gray'),
                   'done': r['done'] or 0,
                   'total': r['total'] or 0
               } for r in rows]
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return []
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)

   @classmethod
   def get_recent_activities(cls, limit=5):
       conn = db_pool.get_conn()
       try:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT t.id, t.title, t.status, t.created_at, u.user_name
                   FROM tasks t
                   LEFT JOIN users u ON t.assignee_uid = u.uid
                   ORDER BY t.created_at DESC
                   LIMIT %s;
               """, (limit,))
               rows = cur.fetchall()
               status_labels = {'not_started': '未着手', 'in_progress': '作業中', 'review': 'レビュー待ち', 'done': '完了'}
               now = datetime.now()
               result = []
               for r in rows:
                   created = r.get('created_at')
                   if isinstance(created, datetime):
                       delta = now - created
                       if delta.days > 0:
                           time_str = f'{delta.days}日前'
                       elif delta.seconds >= 3600:
                           time_str = f'{delta.seconds // 3600}時間前'
                       elif delta.seconds >= 60:
                           time_str = f'{delta.seconds // 60}分前'
                       else:
                           time_str = 'たった今'
                   else:
                       time_str = '-'
                   result.append({
                       'type': 'update',
                       'text': f'タスク「{r["title"]}」が追加されました ({status_labels.get(r["status"], r["status"])})',
                       'time': time_str
                   })
               return result
       except pymysql.err.OperationalError as e:
           err_msg = str(e).lower()
           if 'does not exist' in err_msg or "doesn't exist" in err_msg:
               return []
           raise
       except pymysql.Error as e:
           print(f'エラーが発生しています：{e}')
           abort(500)
       finally:
           db_pool.release(conn)