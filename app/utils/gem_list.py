import os
import google.generativeai as genai
from dotenv import load_dotenv

'''
Gemini-APIのモデル一覧を表示
'''
load_dotenv()
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

for model_info in genai.list_tuned_models():
    print(model_info.name)
