import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from .error import GeminiException
from tenacity import retry, stop_after_attempt

# .envファイルを読み込む
load_dotenv()

# APIキーの設定
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

#モデルを設定
model = genai.GenerativeModel("gemini-1.5-flash")

# retry : 内部的にtry exceptionをもっているため。reraise=Trueにすることで、関数内のエラーハントリングを使用できるようになる
@retry(stop=stop_after_attempt(2), reraise = True)
def get_ai_response(prompt):
    
    #出力にバイアスをかける
    base_prompt = "The part after the : is the question. Please answer in 100 characters or less. Please provide information related to Da Nang city. If the word is meaningless, please send None.: "
    prompt = base_prompt +prompt

    try:
        response = model.generate_content(prompt)
       
    except Exception as e:
        raise GeminiException(e)
        
    return response.text
