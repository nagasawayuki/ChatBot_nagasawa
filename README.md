## Overview
#### ChatBotアプリのサーバーアプリケーション
※このコードだけでは実装できません。meta-developerからmessenger-webhook登録とGemini-apiを取得して、それらの情報をまとめたenvファイルを作成してください。
- 使用環境：messenger
- 回答作成：Gemini-AI(ダナンについてのファインチューニング済)
- 開発言語：Flask
- データベース：Postgresql

#### システムフロー
1. サーバーアプリの構築:
   - Flaskを用いてサーバーアプリケーションを作成しました。
     
2. Webhookの公開と認証:
   - Ngrokを使用してローカルサーバーをインターネット上に公開し、Meta Developer Platformで認証を行いました。
   - これにより、Facebook MessengerからChatbot宛に送信されるメッセージをサーバーが受け取れるように設定しました。
     
3. ユーザーからのメッセージ処理:
   - Facebook Messengerを通じてユーザーから送信されたメッセージを受け取り、そのテキストをChatbot側で取得します。
     
4. Gemini APIへのプロンプト送信:
   - 取得したメッセージをGemini AIのプロンプトとして送信し、AIによるテキスト生成を行います。
     
5. Messenger APIによる応答送信:
   - Gemini AIが生成した応答メッセージをMessenger APIを通じて、ユーザーのチャットに送信します。


## Guide


- Copy app/config.example.py to app/config.py

- Prepare Virtual env

  > python3 -m venv venv

- Start Virtual env

  > source venv/bin/activate

- Install new lib

  > pip install lib

  > pip install -r requirements.txt

- Set Messenger API SetUp through Meta-developer

- Set Gemini API SetUp through Google-AI-Studio
  
- Create .env file and Set API of Messenger and Gemini
  ```
  PAGE_ACCESS_TOKEN = "meta-developper accsess token"
  API_KEY = "Gemini api"
  ```

- Start project
  > python run.py

- Start ngrok
  > ngrok http (Same Port-number as this app)

## 実装動画

<img src="https://github.com/user-attachments/assets/2fc2db85-1ee4-4b1b-8e6a-ac09b3b54a39" width="50%" />
<img src = "https://github.com/user-attachments/assets/2fc2db85-1ee4-4b1b-8e6a-ac09b3b54a39">
<img src ="https://github.com/user-attachments/assets/5af674a8-0d8f-4ff4-9713-c4c3de2c8696">
## システム構造

<img src="https://github.com/user-attachments/assets/a6f5ba3c-72e6-412b-a016-597b456b9a01" width="50%" />
<img width="583" alt="スクリーンショット 2024-12-02 13 19 27" src="https://github.com/user-attachments/assets/d447b31f-bf96-4fe0-a7c6-40b23b968c77">

