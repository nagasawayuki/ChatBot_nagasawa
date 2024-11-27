import requests
from flask import Blueprint, jsonify, request, current_app, render_template, redirect,flash
from flask_login import login_user
from .db import db
from .messenger import send_message
from .gem_ai import get_ai_response
from .error import *
from .models.message import Message
from .models.review import Review
from .models.user import User
from werkzeug.security import check_password_hash
# mainブループリントを登録
main = Blueprint('main', __name__)

@main.route('/')
def index():
  return redirect("/login")

# Admin login
@main.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Auth login
@main.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password'] 
    # usernameから一致するレコードを取得
    user = User.query.filter_by(username=username).first()
 
    if user != None and check_password_hash(user.password, password):
        login_user(user)
        flash('ログイン成功！')
        return redirect("/admin")  # 管理画面にリダイレクト
    else:
        flash('ユーザー名またはパスワードが間違っています。')
        return redirect("/login")


@main.route('/webhook', methods=['GET'])
def verify_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == current_app.config["META_TOKEN"]:  # 任意のトークン/Meta developerのCall-back-URL認証に使用
        return challenge
    return "Invalid verification token", 403

@main.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    print(f"Received webhook event: {data}")

    # メッセージイベントの確認
    try:
        # メッセージスタンプの格納
        # reactionの種類　[other,like]
        if 'reaction' in data['entry'][0]['messaging'][0]:
           if 'react' == data['entry'][0]['messaging'][0]['reaction']['action']:
              
              reaction = data['entry'][0]['messaging'][0]['reaction']['reaction']
              message_id = data['entry'][0]['messaging'][0]['reaction']['mid']

              # スタンプが更新されたときに、前のスタンプを削除
              try:
               db.session.query(Review).filter(Review.message_id==message_id).delete()
               db.session.commit()
              except Exception as e:
                  main.logger.error(f"DataBase Error: {e}")
              
              try:
               review = Review(review = reaction,message_id=message_id)
               db.session.add(review)
               db.session.commit()
              except Exception as e:
                  main.logger.error(f"DataBase Error: {e}")

           else: #reactionが無ければ(unreact)、message_id要素を削除
              message_id = data['entry'][0]['messaging'][0]['reaction']['mid']
              try:
               db.session.query(Review).filter(Review.message_id==message_id).delete()
               db.session.commit() 
              except Exception as e:
                main.logger.error(f"Delete operation failed for message_id={message_id}: {e}")
      


        #メッセージイベントの確認
        if 'message' in data['entry'][0]['messaging'][0]:
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            user_message = data['entry'][0]['messaging'][0]['message']['text']  # ユーザーのメッセージを取得

            #ユーザーからのチャットが1000文字以上ならエラー
            if len(user_message) > 1000:
              raise LongTextException(len(user_message))
            
            #ユーザーからのチャットに空白が含まれないならエラー
            if " " not in user_message:
               raise NoMeaningException()
            
            # Gemini APIにユーザーのメッセージを渡して応答を取得
            ai_response = get_ai_response(user_message)
            # ai_response = "hello!!!"

            # Geminiが生成したテキストがNoneの場合エラー
            if ai_response =="None":
               raise NoMeaningException()
            
            # 返答メッセージのIDを取得
            message_id = send_message(sender_id, ai_response)

            try:
               message = Message(sender_id=sender_id, user_message=user_message, ai_response=ai_response,message_id=message_id)
               db.session.add(message)
               db.session.commit()
            except Exception as e:
               raise DB_UploadError(e)

    except LongTextException as e:
         send_message(sender_id, f"Your text is so long({e.text_length}). Please less than 1000 text.")
         main.logger.warning("LongTextException")

    except NoMeaningException:
         send_message(sender_id, "Can't understand. Please enter question sentence.")
         main.logger.warning("NoMeaningException")

    except GeminiException as e:
         send_message(sender_id, "Gemini AI error. Please retry or contact us.")
         main.logger.error(f"GeminiException: {str(e)}")
    
    except MessengerAPIError as e:
        main.logger.error(f"Mesenger API Error:{e}")
        print("Messenger API Error")
    
    except HTTPRequestError as e:
       main.logger.error(f"Post Error:{e}")
       print("Request Post Error")
    
    except Exception as e:
        send_message(sender_id, "An unexpected error occurred. Please report it to the admins.")
        #想定外のエラー全てが出力される
        main.logger.error(f"Exception: {str(e)}")

    finally: #Webhookドキュメントの決まりで、必ず200を返す
      return jsonify({"status": "success"}), requests.codes.ok