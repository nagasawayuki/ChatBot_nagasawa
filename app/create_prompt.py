'''geminiにユーザーごとの自然な会話を成立させるためのプロンプト作成関数'''
from .db import db
from typing import List, Dict
from .models.message import Message

def fetch_recent_messages(sender_id: str, max_turns: int = 10) -> List[Dict[str, str]]:
    """
    データベースから最新の会話履歴を取得。

    :param sender_id: ユーザーの一意のID
    :param max_turns: 最大取得数（質問＋応答のペア数）
    :return: 会話履歴リスト（[{role: "user", content: "text"}, ...]）
    """
    # 最新のメッセージを取得
    recent_messages = (
        db.session.query(Message)
        .filter_by(sender_id=sender_id)
        .order_by(Message.timestamp.desc())  # 時系列で降順（最新が先）
        .limit(max_turns * 2)  # 質問と応答を合わせて取得
        .all()
    )

    # 時系列順に並べ替え
    conversation_history = []
    for msg in reversed(recent_messages):  # 最新→古い順から、古い→最新順に変更
        if msg.user_message:
            conversation_history.append({"role": "user", "content": msg.user_message})
        if msg.ai_response:
            conversation_history.append({"role": "assistant", "content": msg.ai_response})

    return conversation_history

def create_prompt(sender_id: str, user_message: str, max_turns: int = 10) -> List[Dict[str, str]]:
    """
    Gemini APIに送信するプロンプトを作成。
    最新の会話履歴と新しいユーザーメッセージを組み合わせる。
    :param sender_id: ユーザーの一意のID
    :param user_message: 現在のユーザーのメッセージ
    :param max_turns: 最大の会話履歴数（ユーザー質問＋AI応答のペア数）
    :return: プロンプトリスト（[{role: "user", content: "text"}, ...]）
    """
    # 最新の会話履歴を取得
    conversation_history = fetch_recent_messages(sender_id=sender_id, max_turns=max_turns)

    # 現在のユーザーメッセージを履歴に追加
    conversation_history.append({"role": "user", "content": user_message})

    return conversation_history