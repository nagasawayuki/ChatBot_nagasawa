# app/messenger.py
import os
import requests
from dotenv import load_dotenv
from .error import *

# .envファイルを読み込む
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')


def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v15.0/me/messages?access_token={
        PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise HTTPRequestError(e)

    if response.status_code != requests.codes.ok:
        raise MessengerAPIError(response.status_code)

    # ユーザーへの回答idを返す→チャットとスタンプをDBで関連させるため
    return response.json()['message_id']
