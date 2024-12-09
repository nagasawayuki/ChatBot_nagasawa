'''geminiにユーザーごとの自然な会話を成立させるためのプロンプト作成関数'''
from .db import db
from .models.message import Message

def create_prompt(prompt: str, sender_id: str) -> str:
    print("------Step8.6-----------")
    # sender_idをキーに、タイムスタンプが最新のものから最大10件のデータを取得
    messages = (
        db.session.query(Message.user_message, Message.ai_response)
        .filter(Message.sender_id == sender_id)
        .order_by(Message.timestamp.desc())
        .limit(10)
        .all()
    )
    print("------Step8.7-----------")
    # 時系列順にソート (最新順で取得しているため逆順にする)
    messages = messages[::-1]

    # テキストを整形
    result = []
    #base_prompt = "Please answer in 100 characters or less. If the word is meaningless, please send None.:"
    base_prompt = (
        "Below are the past 10 interactions between the user and the AI in chronological order:\n"
        "Please generate a concise response (100 characters or less) based on the main question at the end.\n"
        "If the main question alone is meaningless, respond with 'None.'\n"
    )
    result.append(base_prompt)
    
    for user_message, ai_response in messages:
        result.append(f"User: {user_message}\nAI: {ai_response}")

    # 最後にプロンプトを追加
    result.append(f"User: {prompt}")

    # 結果を結合して返す
    return "\n\n".join(result)

if __name__ == "__main__":
    prompt_text = "What is the weather like today?"
    sender_id = "9179700495376227"
    formatted_text = create_prompt(prompt_text, sender_id)
    print(formatted_text)