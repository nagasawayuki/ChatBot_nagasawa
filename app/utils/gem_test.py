import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# APIキーの設定
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(model_name="tunedModels/increment-3bmcnveces1m")
result = model.generate_content("What are the top attractions in Da Nang?")
print(result.text)
