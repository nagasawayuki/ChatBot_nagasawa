import requests
from flask import Blueprint, jsonify, request, current_app, render_template, redirect, flash
from flask_login import login_user
from werkzeug.security import check_password_hash
from .db_operation import *
from .messenger import send_message
from .error import *
from .models.message import Message
from .models.review import Review
from .response import response


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
    user = user_get(username)

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
                review_delate(message_id)

                review = Review(review=reaction, message_id=message_id)
                review_upload(review)

            else:  # reactionが無ければ(unreact)、message_id要素を削除
                message_id = data['entry'][0]['messaging'][0]['reaction']['mid']
                review_delate(message_id)

        # メッセージイベントの確認
        if 'message' in data['entry'][0]['messaging'][0]:
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            message_data = data['entry'][0]['messaging'][0]['message']

            # text以外のファイルがあればエラー出力
            if 'attachments' in message_data:
                # MessengerのGood_Stampのみ、DBに保存する
                attachment = message_data['attachments'][0]['payload']
                if 'sticker_id' in attachment and attachment['sticker_id'] == 369239263222822:
                    message_id = send_message(sender_id, "Thank you!!!")
                    message = Message(sender_id=sender_id, user_message='Good_Stamp',
                                      ai_response='Thank you!!!', message_id=message_id)
                    message_upload(message)
                    return

                raise FormatError("include other faile in request.")

            user_message = message_data['text']

            response(user_message, sender_id)

    except LongTextException as e:
        send_message(sender_id, f"Your text is so long({
                     e.text_length}). Please less than 100 text.")
        current_app.logger.warning("LongTextException")

    except NoMeaningException:
        send_message(
            sender_id, "Can't understand. Please enter question sentence.")
        current_app.logger.warning("NoMeaningException")

    except FormatError as e:
        send_message(sender_id, "This chat accepts text only.")
        current_app.logger.warning(f"Format Error: not text request:{e}")

    except GeminiException as e:
        send_message(sender_id, "Gemini AI error. Please retry or contact us.")
        current_app.logger.error(f"GeminiException: {str(e)}")

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
