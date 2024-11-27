import os
from flask import Flask
from flask_login import LoginManager
from .db import db
from .models.message import *
from .models.review import *
# github push test
import logging
#admin用に追加
from .models.user import User  # 認証用のユーザーモデルをインポート
from .admin import init_admin  # 管理画面の初期化関数をインポート
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash  # パスワードハッシュ化関数をインポート

load_dotenv()

def create_admin_user():
   admin_username=os.getenv("ADMIN_USERNAME")
   admin_password = os.getenv("ADMIN_PASSWORD")

   if not admin_username or not admin_password:
      print("管理者アカウントが登録されていません。.evnファイルを確認してください") 
      return
   if not User.query.filter_by(username=admin_username).first():
      # アプリ作成時、既存のアカウントを全て削除する
      db.session.query(User).delete()
      db.session.commit()

      # Admin Userを作成
      admin_user = User(username=admin_username, password=generate_password_hash(admin_password))
      db.session.add(admin_user)
      db.session.commit()
      print(f"管理者アカウント '{admin_username}' が作成されました。")

def create_app():

  app = Flask(__name__)
  logging.basicConfig(filename='record.log', level=logging.DEBUG)
  # Import the routes
  from .routes import main
  app.register_blueprint(main)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")=='True'
  app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") # セッションやクッキーの安全性を保つための秘密鍵
  app.config['META_TOKEN'] = os.getenv("META_TOKEN")

  with app.app_context():
    db.init_app(app)
    db.create_all()  # DB内のテーブル作成
    db.reflect()     # DBに既にあるテーブルを反映

    create_admin_user()

  # Flask-Loginの設定
  login_manager = LoginManager(app)
  login_manager.login_view = '/login'  # 認証されていない場合のリダイレクト先

  @login_manager.user_loader
  # 裏でユーザーを見つけるときにload_userが呼び出される
  def load_user(user_id):
      # userMixin
      return User.query.get(int(user_id))
  
  # viewリスポンス
  init_admin(app)

  return app
