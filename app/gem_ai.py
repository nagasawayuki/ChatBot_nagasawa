import os
from dotenv import load_dotenv
import google.generativeai as genai
from tenacity import retry, stop_after_attempt
from .error import GeminiException
from .db_operation import *

# .envファイルを読み込む
load_dotenv()

# APIキーの設定
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

# モデルを設定
model = genai.GenerativeModel("tunedModels/increment-3bmcnveces1m")

def create_prompt(prompt: str, sender_id: str) -> str:
    # sender_idをキーに、タイムスタンプが最新のものから最大10件のデータを取得
    messages = message_filter_get(sender_id,10)

    # 時系列順にソート (最新順で取得しているため逆順にする)
    messages = messages[::-1]

    # テキストを整形
    result = []
    # base_prompt = "Please answer in 100 characters or less. If the word is meaningless, please send None.:"
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

# model = genai.GenerativeModel("gemini-1.5-flash")
# retry : 内部的にtry exceptionをもっているため。reraise=Trueにすることで、関数内のエラーハントリングを使用できるようになる
@retry(stop=stop_after_attempt(2), reraise=True)
def get_ai_response(prompt):

    try:
        response = model.generate_content(prompt)
        print(f"Geminiの答え:{response.text}")
    except Exception as e:
        raise GeminiException(e)

    return response.text
