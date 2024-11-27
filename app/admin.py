from flask import redirect, url_for, Response
from io import StringIO
import csv
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user,logout_user
from sqlalchemy.orm import joinedload
from .db import db
from .models.user import User  # 認証用のユーザーモデル
from .models.message import Message
from .models.review import Review

# ModelViewデフォルトの新規作成、編集を削除
# Viewへのアクセス制御

class SecureModelView(ModelView):
    can_create = False  # 新規作成を無効化
    can_edit = False    # 編集を無効化
    
    def is_accessible(self):
        # login_userでcurrent_userがtrueにする
        return current_user.is_authenticated  # 認証されているユーザーのみアクセスを許可

    def inaccessible_callback(self, name, **kwargs):
        #return self.render('admin_panel.html') # 認証されていない場合はログインページにリダイレクト
        return redirect('/login')
    
# カスタムAdminIndexView
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login')

        # ログイン済みの場合はデフォルトの管理画面トップページを表示
        return super(MyAdminIndexView, self).index()  # 親クラスのindexメソッドを呼び出す

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')
    

# ユーザーとGemini-AIのチャット情報と、ユーザーの評価をビューで表示
class MessageReviewView(SecureModelView):
    def get_query(self):
        return (
            self.session.query(
                Message.id,
                Message.sender_id,
                Message.user_message,
                Message.ai_response,
                Review.review,  
                Message.timestamp
                )
            # SQLAlchemy は自動的に外部キーのリレーション（ForeignKey）に基づいて結合条件を決定
            .outerjoin(Review, Message.message_id == Review.message_id)  
        )
    
    # @action デコレーターは、ModelView クラスで用意されているメソッド
    # 管理画面には出力していない、message.timestampを出力するように設計
    @action('export_csv', 'Export to CSV', 'Are you sure you want to export selected rows to CSV?')
    def export_csv(self, ids):# ids=選択されたIdのリスト
        # 選択された行のクエリを取得
        query = self.get_query().filter(Message.id.in_(ids))

        # CSV用のストリームを作成
        si = StringIO()
        writer = csv.writer(si)

        # ヘッダー行を作成
        writer.writerow(['Sender ID', 'User Message', 'AI Response', 'Review','Message Time'])

        for row in query.all():
            writer.writerow([row.sender_id, row.user_message, row.ai_response, row.review, row.timestamp])

        # CSVレスポンスを作成
        output = Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=export.csv"},
        )
        return output
   
    column_list = ("sender_id", "user_message", "ai_response", "review")

    column_labels = {
        "sender_id": "Sender ID",
        "user_message": "User Message",
        "ai_response": "AI Response",
        "review": "Review",
    }

# 管理画面の初期化
def init_admin(app):
    admin = Admin(app, name='admin Panel', index_view=MyAdminIndexView())
    admin.add_view(SecureModelView(User, db.session))  # ユーザーモデルを管理画面に追加
    admin.add_view(MessageReviewView(Message, db.session)) # messageとreviewの統合表示
    admin.add_view(LogoutView(name="Logout",endpoint='/logout')) #ログアウトビュー
