from .error import *
from .gem_ai import *
from .messenger import send_message
from .db_operation import *


def response(user_message, sender_id):
    # ユーザーからのチャットが1000文字以上ならエラー
    if len(user_message) > 100:
        raise LongTextException(len(user_message))

    # ユーザーからのチャットに空白が含まれないならエラー
    if " " not in user_message:
        raise NoMeaningException()

    prompt = create_prompt(user_message, sender_id)
    # Gemini APIにユーザーのメッセージを渡して応答を取得
    print(f"--send-prompt--")
    print(prompt)
    print("--------------")
    ai_response = get_ai_response(prompt)
    print(f"ai_responseの中身:{ai_response}")

    # Geminiが生成したテキストがNoneの場合エラー。stripで文字以外の余計な部分を削除
    if ai_response.strip() == "None.":
        print("Errorをキャッチ")
        raise NoMeaningException()

    # 返答メッセージのIDを取得
    message_id = send_message(sender_id, ai_response)
    message = Message(sender_id=sender_id, user_message=user_message,
                      ai_response=ai_response, message_id=message_id)
    message_upload(message)
