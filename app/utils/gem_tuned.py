import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
import json

# .envファイルを読み込む
load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir,"../gem_tunedData.json")
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)

base_model = "models/gemini-1.5-flash-001-tuning"

with open(json_file_path,"r") as f:
    training_data = json.load(f)
print("Please check training_file: ",training_data[:3])

operation = genai.create_tuned_model(
    # You can use a tuned model here too. Set `source_model="tunedModels/..."`
    display_name="increment",
    source_model=base_model,
    epoch_count=20,
    batch_size=1,
    learning_rate=0.001,
    training_data=training_data,
)

for status in operation.wait_bar():
    time.sleep(10)

result = operation.result()
print(result)



