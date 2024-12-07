import requests
from flask import Blueprint, jsonify, request, current_app, render_template, redirect, flash
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
    current_app.logger.error(f"test errrrrrrror:")
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
    # 任意のトークン/Meta developerのCall-back-URL認証に使用
    if token == current_app.config["META_TOKEN"]:
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

                db.session.query(Review).filter(
                    Review.message_id == message_id).delete()
                db.session.commit()

                review = Review(review=reaction, message_id=message_id)
                db.session.add(review)
                db.session.commit()

            else:  # reactionが無ければ(unreact)、message_id要素を削除
                message_id = data['entry'][0]['messaging'][0]['reaction']['mid']
                try:
                    db.session.query(Review).filter(
                        Review.message_id == message_id).delete()
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(
                        f"Delete operation failed for message_id={message_id}: {e}")

        # メッセージイベントの確認
        if 'message' in data['entry'][0]['messaging'][0]:
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            # ユーザーのメッセージを取得
            user_message = data['entry'][0]['messaging'][0]['message']['text']

            # ユーザーからのチャットが1000文字以上ならエラー
            if len(user_message) > 200:
                raise LongTextException(len(user_message))

            # ユーザーからのチャットに空白が含まれないならエラー
            if " " not in user_message:
                raise NoMeaningException()

            # Gemini APIにユーザーのメッセージを渡して応答を取得
            ai_response = get_ai_response(user_message)
            print(f"ai_responseの中身:{ai_response}")

            # Geminiが生成したテキストがNoneの場合エラー。stripで文字以外の余計な部分を削除
            if ai_response.strip() == "None.":
                print("Errorをキャッチ")
                raise NoMeaningException()

            # 返答メッセージのIDを取得
            message_id = send_message(sender_id, ai_response)

            message = Message(sender_id=sender_id, user_message=user_message,
                              ai_response=ai_response, message_id=message_id)
            db.session.add(message)
            db.session.commit()
        
        else:
            raise FormatError

    except LongTextException as e:
        send_message(sender_id, f"Your text is so long({
                     e.text_length}). Please less than 200 text.")
        current_app.logger.warning("LongTextException")

    except NoMeaningException:
        send_message(sender_id, "Can't understand. Please enter question sentence.")
        current_app.logger.warning("NoMeaningException")

    except GeminiException as e:
        send_message(sender_id, "Gemini AI error. Please retry or contact us.")
        current_app.logger.error(f"GeminiException: {str(e)}")
    
    except FormatError as e:
        send_message(sender_id, "This chat accepts text only.")
        current_app.logger.error(f"Format Error: not text request")

    except MessengerAPIError as e:
        current_app.logger.error(f"Mesenger API Error:{e}")
        print("Messenger API Error")

    except HTTPRequestError as e:
        current_app.logger.error(f"Post Error:{e}")
        print("Request Post Error")

    except Exception as e:
        send_message(
            sender_id, "An unexpected error occurred. Please report it to the admins.")
        # 想定外のエラー全てが出力される
        current_app.logger.error(f"Exception: {str(e)}")

    finally:  # Webhookドキュメントの決まりで、必ず200を返す
        return jsonify({"status": "success"}), requests.codes.ok
