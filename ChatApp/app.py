from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from datetime import timedelta, date
import hashlib
import uuid
import re
import os

from models import User, Channel, Message, Task, Activity
from util.assets import bundle_css_files


# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 60
AVATAR_ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
AVATAR_MAX_SIZE = 2 * 1024 * 1024  # 2MB

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

# 静的ファイルをキャッシュする設定。開発中はコメントアウト推奨。
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2678400
bundle_css_files(app)


def _user_color_index(uid):
    """uidから一意の色インデックス(0-6)を算出。メンバー・タスク画面で同一ユーザーに同じ色を割り当てる"""
    if not uid:
        return 6
    return sum(ord(c) for c in str(uid)) % 7


@app.template_filter('user_color_index')
def user_color_index_filter(uid):
    return _user_color_index(uid)


@app.context_processor
def inject_active_nav():
    """サイドバーの active_nav が未定義でもエラーにしない（ビューから渡された値で上書きされる）"""
    return {'active_nav': ''}


# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('dashboard_view'))


# サインアップページの表示（ログイン/新規登録の統合ページを表示）
@app.route('/signup', methods=['GET'])
def signup_view():
    return render_template('auth/signup.html')


# サインアップ処理
@app.route('/signup', methods=['POST'])
def signup_process():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    passwordConfirmation = request.form.get('password-confirmation')

    if name == '' or email =='' or password == '' or passwordConfirmation == '':
        flash('空のフォームがあるようです')
    elif password != passwordConfirmation:
        flash('二つのパスワードの値が違っています')
    elif re.match(EMAIL_PATTERN, email) is None:
        flash('正しいメールアドレスの形式ではありません')
    else:
        uid = uuid.uuid4()
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        registered_user = User.find_by_email(email)

        if registered_user != None:
            flash('既に登録されているようです')
        else:
            User.create(uid, name, email, password)
            UserId = str(uid)
            session['uid'] = UserId
            return redirect(url_for('dashboard_view'))
        
    return redirect(url_for('signup_view'))


# ログインページの表示（認証ページを表示）
@app.route('/login', methods=['GET'])
def login_view():
    return render_template('auth/login.html')


# ログイン処理
@app.route('/login', methods=['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')

    if email =='' or password == '':
        flash('空のフォームがあるようです')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('このユーザーは存在しません')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('パスワードが間違っています！')
            else:
                session['uid'] = user["uid"]
                try:
                    Activity.create(user["uid"], Activity.TYPE_LOGIN, f'{user.get("user_name", "ユーザー")}がログインしました')
                except Exception:
                    pass
                return redirect(url_for('dashboard_view'))

    return redirect(url_for('login_view'))


# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_view'))


# ダッシュボードの表示
@app.route('/dashboard', methods=['GET'])
def dashboard_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    try:
        channels = Channel.get_all()
        channels = list(reversed(channels))
    except Exception:
        channels = []
    try:
        users = User.get_all()
    except Exception:
        users = []

    # タスクDBから統計を取得
    try:
        stats = Task.get_stats()
        progress = Task.get_progress()
        chart_total = int((progress['completed'] / progress['total'] * 100)) if progress['total'] > 0 else 0
        categories = Task.get_stats_by_tag()
        member_activity = Task.get_member_activity()
        activities = Activity.get_recent(limit=10)
        # ドーナツチャート用のconic-gradientを構築
        cumul = 0
        gradient_parts = []
        for cat in categories:
            gradient_parts.append(f"{cat['color']} {cumul}% {cumul + cat['share']}%")
            cumul += cat['share']
        chart_gradient = ', '.join(gradient_parts) if gradient_parts else 'transparent 0% 100%'
    except Exception:
        stats = {'total': 0, 'completed': 0, 'in_progress': 0, 'blocked': 0}
        chart_total = 0
        categories = []
        member_activity = []
        activities = []
        chart_gradient = 'transparent 0% 100%'

    return render_template('dashboard.html', channels=channels, users=users, uid=uid, active_nav='dashboard', stats=stats, chart_total=chart_total, chart_gradient=chart_gradient, categories=categories, member_activity=member_activity, activities=activities)


# 設定ページの表示
@app.route('/settings', methods=['GET'])
def settings_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    user = User.get_by_uid(uid) or {}
    return render_template('settings.html', uid=uid, user=user, active_nav='settings')


# プロフィール更新
@app.route('/settings/profile', methods=['POST'])
def update_profile():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    uid = str(uid)
    user_name = (request.form.get('user_name') or '').strip()
    email = (request.form.get('email') or '').strip()
    avatar_url = None

    # プロフィール画像のアップロード処理
    if 'avatar' in request.files:
        f = request.files['avatar']
        if f and f.filename:
            ext = (f.filename.rsplit('.', 1)[-1] or '').lower()
            if ext in AVATAR_ALLOWED_EXT:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)
                if size <= AVATAR_MAX_SIZE:
                    upload_dir = os.path.join(app.static_folder, 'uploads', 'avatars')
                    os.makedirs(upload_dir, exist_ok=True)
                    safe_ext = ext if ext != 'jpeg' else 'jpg'
                    filename = f"{uid}.{safe_ext}"
                    filepath = os.path.join(upload_dir, filename)
                    f.save(filepath)
                    avatar_url = f"uploads/avatars/{filename}"
                else:
                    flash('画像サイズは2MB以下にしてください')
            else:
                flash('画像形式は PNG, JPG, GIF, WEBP のみ対応しています')
        elif request.form.get('avatar_remove') == '1':
            avatar_url = ''

    if not user_name:
        flash('ユーザー名を入力してください')
    elif not email:
        flash('メールアドレスを入力してください')
    elif re.match(EMAIL_PATTERN, email) is None:
        flash('正しいメールアドレスの形式ではありません')
    else:
        try:
            existing_by_name = User.find_by_user_name(user_name)
            if existing_by_name and str(existing_by_name['uid']) != uid:
                flash('そのユーザー名は既に使用されています')
            else:
                existing_by_email = User.find_by_email(email)
                if existing_by_email and str(existing_by_email['uid']) != uid:
                    flash('そのメールアドレスは既に登録されています')
                else:
                    db_avatar = avatar_url if avatar_url != '' else (None if avatar_url is None else avatar_url)
                    if avatar_url == '':
                        db_avatar = None  # 削除
                    elif avatar_url:
                        db_avatar = avatar_url
                    User.update_profile(uid, user_name, email, db_avatar)
                    flash('プロフィールを更新しました')
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash('プロフィールの更新に失敗しました。コンソールログを確認してください。')
    return redirect(url_for('settings_view'))


# パスワード変更
@app.route('/settings/password', methods=['POST'])
def update_password():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    current = request.form.get('current_password') or ''
    new_pass = request.form.get('new_password') or ''
    confirm = request.form.get('password_confirm') or ''
    if not current:
        flash('現在のパスワードを入力してください')
    elif not new_pass:
        flash('新しいパスワードを入力してください')
    elif new_pass != confirm:
        flash('新しいパスワードと確認が一致しません')
    elif len(new_pass) < 6:
        flash('新しいパスワードは6文字以上で入力してください')
    else:
        stored_hash = User.get_password_hash(uid)
        current_hash = hashlib.sha256(current.encode('utf-8')).hexdigest()
        if current_hash != stored_hash:
            flash('現在のパスワードが正しくありません')
        else:
            new_hash = hashlib.sha256(new_pass.encode('utf-8')).hexdigest()
            User.update_password(uid, new_hash)
            flash('パスワードを変更しました')
    return redirect(url_for('settings_view'))


# ステータス更新
VALID_STATUSES = ('working', 'break', 'away', 'review')

@app.route('/settings/status', methods=['GET', 'POST'])
def update_status():
    """POST: ステータスを更新して設定ページへリダイレクト。GET: 設定ページへリダイレクト。"""
    if request.method == 'GET':
        return redirect(url_for('settings_view'))
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    uid = str(uid)
    status = request.form.get('status') or ''
    if status not in VALID_STATUSES:
        flash('無効なステータスです')
    else:
        try:
            User.update_status(uid, status)
            status_labels = {'working': '作業中', 'break': '休憩中', 'away': '離席中', 'review': 'レビュー待ち'}
            user_data = User.get_by_uid(uid) or {}
            desc = f'{user_data.get("user_name", "ユーザー")}のステータスが{status_labels.get(status, status)}に変更されました'
            Activity.create(uid, Activity.TYPE_STATUS_CHANGE, desc, 'user', uid)
            flash('ステータスを更新しました')
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash('ステータスの更新に失敗しました。statusカラムがDBに存在するか確認してください。')
    return redirect(url_for('settings_view'))


# タスク管理ページの表示
@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        if not title:
            flash('タスクのタイトルを入力してください')
            return redirect(url_for('tasks_view'))
        status = request.form.get('status') or 'not_started'
        assignee_uid = request.form.get('assignee_uid') or None
        if assignee_uid == '':
            assignee_uid = None
        tag = request.form.get('tag') or 'other'
        due_date_str = request.form.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = date.fromisoformat(due_date_str)
            except (ValueError, TypeError):
                pass
        try:
            Task.create(uid=uid, title=title, status=status, assignee_uid=assignee_uid, tag=tag, due_date=due_date)
            user_data = User.get_by_uid(uid) or {}
            desc = f'{user_data.get("user_name", "ユーザー")}がタスク「{title}」を追加しました'
            Activity.create(uid, Activity.TYPE_TASK_ADD, desc, 'task', None)
            flash('タスクを追加しました')
        except Exception:
            flash('タスクの追加に失敗しました')
        return redirect(url_for('tasks_view'))
    filter_mode = request.args.get('filter', 'all')
    assignee_uid = uid if filter_mode == 'mine' else None
    tasks = Task.get_all(assignee_uid=assignee_uid)
    progress = Task.get_progress(assignee_uid=assignee_uid)
    completed = progress['completed']
    total = progress['total']
    percent = int((completed / total * 100)) if total > 0 else 0
    tag_labels = {'backend': 'バックエンド', 'frontend': 'フロントエンド', 'doc': 'ドキュメント',
                  'design': 'デザイン', 'prototype': 'プロトタイプ', 'other': 'その他'}
    try:
        users = User.get_all()
    except Exception:
        users = []
    return render_template(
        'tasks.html',
        uid=uid,
        tasks=tasks,
        users=users,
        progress_percent=percent,
        progress_completed=completed,
        progress_total=total,
        filter_mode=filter_mode,
        today=date.today(),
        tag_labels=tag_labels,
        active_nav='tasks'
    )


@app.route('/tasks/<int:task_id>/status', methods=['POST'])
def task_update_status(task_id):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    status = request.form.get('status')
    valid_statuses = ('not_started', 'in_progress', 'review', 'done')
    if status not in valid_statuses:
        flash('無効なステータスです')
        return redirect(url_for('tasks_view'))
    try:
        task = Task.find_by_id(task_id)
        if task is None:
            flash('タスクが見つかりません')
            return redirect(request.referrer or url_for('tasks_view'))
        assignee = task.get('assignee_uid')
        if assignee is None or _normalize_uid(assignee) != _normalize_uid(uid):
            flash('担当者のみステータスを変更できます')
            return redirect(request.referrer or url_for('tasks_view'))
        Task.update_status(task_id, status)
        if task:
            user_data = User.get_by_uid(uid) or {}
            status_labels = {'not_started': '未着手', 'in_progress': '作業中', 'review': 'レビュー待ち', 'done': '完了'}
            desc = f'{user_data.get("user_name", "ユーザー")}がタスク「{task.get("title", "")}」を{status_labels.get(status, status)}に変更'
            Activity.create(uid, Activity.TYPE_TASK_STATUS, desc, 'task', task_id)
        flash('タスクのステータスを更新しました')
    except Exception:
        flash('ステータスの更新に失敗しました')
    return redirect(request.referrer or url_for('tasks_view'))


def _normalize_uid(value):
    """DB・セッション由来の uid を比較用に正規化（bytes 差異の吸収）"""
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='replace').strip()
    return str(value).strip()


def _get_members_with_status():
    """メンバー一覧（ステータス付き）を取得"""
    try:
        users = User.get_all_with_status()
    except Exception:
        return []
    status_labels = {'working': '作業中', 'break': '休憩中', 'away': 'オフライン', 'review': 'レビュー待ち'}
    status_colors = {'working': 'green', 'break': 'yellow', 'away': 'gray', 'review': 'blue'}
    return [{
        'uid': u.get('uid'),
        'user_name': u.get('user_name', 'Unknown'),
        'avatar_url': u.get('avatar_url'),
        'status': status_labels.get((u.get('status') or 'working').strip(), '作業中'),
        'status_color': status_colors.get((u.get('status') or 'working').strip(), 'gray'),
    } for u in users]


# チャンネル一覧ページの表示（チャンネルがあれば最初のチャンネルへリダイレクト）
@app.route('/channels', methods=['GET'])
def channels_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    channels = Channel.get_all()
    channels = list(reversed(channels))
    if channels:
        return redirect(url_for('detail', cid=channels[0]['id']))
    try:
        members = _get_members_with_status()
    except Exception:
        members = []
    try:
        channel_unread = Message.get_unread_counts(uid)
    except Exception:
        channel_unread = {}
    return render_template('channels.html', channels=channels, members=members, channel_unread=channel_unread, uid=uid, active_nav='channels')


# チャンネルの作成
@app.route('/channels', methods=['POST'])
def create_channel():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    channel_name = request.form.get('channelTitle')
    channel = Channel.find_by_name(channel_name)
    if channel == None:
        channel_description = request.form.get('channelDescription')
        Channel.create(uid, channel_name, channel_description)
        try:
            user_data = User.get_by_uid(uid) or {}
            desc = f'{user_data.get("user_name", "ユーザー")}がチャンネル #{channel_name} を作成しました'
            Activity.create(uid, Activity.TYPE_CHANNEL_CREATE, desc, 'channel', None)
        except Exception:
            pass
        return redirect(url_for('channels_view'))
    else:
        error = '既に同じ名前のチャンネルが存在しています'
        return render_template('error/error.html', error_message=error)


# チャンネルの更新
@app.route('/channels/update/<cid>', methods=['POST'])
def update_channel(cid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    channel_name = request.form.get('channelTitle')
    channel_description = request.form.get('channelDescription')

    Channel.update(uid, channel_name, channel_description, cid)
    return redirect(f'/channels/{cid}/messages')


# チャンネルの削除
@app.route('/channels/delete/<cid>', methods=['POST'])
def delete_channel(cid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    channel = Channel.find_by_cid(cid)
    if channel is None:
        flash('チャンネルが見つかりません')
        return redirect(url_for('channels_view'))

    if str(channel.get('uid', '')) != str(uid):
        flash('チャンネルは作成者のみ削除可能です')
    else:
        try:
            Channel.delete(cid)
            flash('チャンネルを削除しました')
        except Exception:
            flash('チャンネルの削除に失敗しました')
    return redirect(url_for('channels_view'))


# チャンネル詳細ページの表示（各チャンネル内で、そのチャンネルに属している全メッセージを表示させる）
@app.route('/channels/<cid>/messages', methods=['GET'])
def detail(cid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    channel = Channel.find_by_cid(cid)
    if channel is None:
        abort(404)
    Message.mark_channel_read(uid, cid)
    messages = Message.get_all(cid)
    channels = Channel.get_all()
    channels = list(reversed(channels))
    try:
        members = _get_members_with_status()
    except Exception:
        members = []
    try:
        channel_unread = Message.get_unread_counts(uid)
    except Exception:
        channel_unread = {}
    # ログイン済みユーザーには編集ボタンを表示（チャンネル名・説明の変更）
    can_edit_channel = True
    # 削除は作成者のみ（モーダル内の削除セクション用）
    can_delete_channel = _normalize_uid(uid) == _normalize_uid(channel.get('uid'))

    return render_template(
        'messages.html',
        messages=messages,
        channel=channel,
        channels=channels,
        members=members,
        channel_unread=channel_unread,
        uid=uid,
        can_edit_channel=can_edit_channel,
        can_delete_channel=can_delete_channel,
        active_nav='channels',
    )


# メッセージの投稿
@app.route('/channels/<cid>/messages', methods=['POST'])
def create_message(cid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    message = request.form.get('message')

    if message:
        Message.create(uid, cid, message)
        try:
            channel = Channel.find_by_cid(cid)
            user_data = User.get_by_uid(uid) or {}
            ch_name = channel.get('name', 'チャンネル') if channel else 'チャンネル'
            desc = f'{user_data.get("user_name", "ユーザー")}が #{ch_name} にメッセージを投稿しました'
            Activity.create(uid, Activity.TYPE_MESSAGE, desc, 'channel', cid)
        except Exception:
            pass

    return redirect('/channels/{cid}/messages'.format(cid = cid))


# メッセージの削除
@app.route('/channels/<cid>/messages/<message_id>', methods=['POST'])
def delete_message(cid, message_id):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))

    if message_id:
        Message.delete(message_id)
    return redirect('/channels/{cid}/messages'.format(cid = cid))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'),404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error/500.html'),500


# メンバー管理ページの表示
@app.route('/members', methods=['GET'])
def members_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    try:
        users = User.get_all_with_status()
    except Exception:
        users = []
    try:
        incomplete_tasks_map = Task.get_incomplete_tasks_by_assignee()
    except Exception:
        incomplete_tasks_map = {}
    try:
        member_activity_list = Task.get_member_activity()
        member_activity = {r['name']: r for r in member_activity_list}
    except Exception:
        member_activity = {}
    status_labels = {'working': '作業中', 'break': '休憩中', 'away': 'オフライン', 'review': 'レビュー待ち'}
    status_colors = {'working': 'green', 'break': 'yellow', 'away': 'gray', 'review': 'blue'}
    members = []
    for u in users:
        user_status = (u.get('status') or 'working').strip()
        name = u.get('user_name', 'Unknown')
        task_list = incomplete_tasks_map.get(u['uid'], [])
        activity = member_activity.get(name, {})
        done = activity.get('done', 0)
        total = activity.get('total', 0)
        if not task_list and user_status == 'break':
            task_list = [{'title': '休憩中', 'task_status': ''}]
        elif not task_list and user_status == 'away':
            task_list = [{'title': 'オフライン', 'task_status': ''}]
        elif not task_list and user_status == 'review':
            task_list = [{'title': 'レビュー待ち', 'task_status': ''}]
        progress_pct = int((done / total * 100)) if total and total > 0 else 0
        members.append({
            'uid': u['uid'],
            'name': name,
            'avatar_url': u.get('avatar_url'),
            'status_raw': user_status,
            'status': status_labels.get(user_status, user_status or '作業中'),
            'status_color': status_colors.get(user_status, 'gray'),
            'current_tasks': task_list,
            'progress_pct': progress_pct,
        })
    filter_val = request.args.get('filter', 'all') or 'all'
    if filter_val and filter_val != 'all':
        members = [m for m in members if m['status_raw'] == filter_val]
    return render_template('members.html', uid=uid, members=members, filter_val=filter_val, active_nav='members')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)