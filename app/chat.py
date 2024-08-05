import streamlit as st
import urllib.request
import json
import os
import ssl
import random
import string
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import requests
import base64
import time
import threading
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 各種変数の定義
# AzureのText-to-Speechサービスのエンドポイント
TTS_ENDPOINT = os.getenv("TTS_ENDPOINT")

# Azure AI Speech のトークンを取得するエンドポイント
TTS_TOKEN_ENDPOINT = os.getenv("TTS_TOKEN_ENDPOINT")

# Azure AI Speech のサブスクリプションキー
TTS_SUBSCRIPTION_KEY = os.getenv("TTS_SUBSCRIPTION_KEY")

# メイン処理用 Prompt Flow エンドポイント
PROMPT_FLOW_ENDPOINT = os.getenv("PROMPT_FLOW_ENDPOINT")

# Prompt Flow の API キー
PROMPT_FLOW_API_KEY = os.getenv("PROMPT_FLOW_API_KEY")

# Prompt Flow のデプロイメント名
PROMPT_FLOW_DEPLOYMENT_NAME = os.getenv("PROMPT_FLOW_DEPLOYMENT_NAME")

# Whisper エンドポイント
WHISPER_ENDPOINT = os.getenv("WHISPER_ENDPOINT")

# Whisper の API キー
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")

# パスコード
PASSCODE = os.getenv("PASSCODE")


# ランダムなファイル名を生成する関数
def generate_random_filename(length=12, extension="wav"):
    letters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters) for i in range(length))
    return f"{random_string}.{extension}"

# 音声ファイルをテキストに変換する関数
def speech_to_text(audio_bytes: bytes):
    temp_dir = "/tmp"
    temp_file = f"{temp_dir}/{generate_random_filename()}"
    temp_file_to_remove = temp_file
    audio = AudioSegment(
        data=audio_bytes,
        sample_width=2,
        frame_rate=44100,
        channels=2
    )
    audio.export(temp_file, format='wav')

    with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        with open(temp_file.name, "rb") as f:
            file = {'file': (temp_file.name, f)}
            response = requests.post(
                WHISPER_ENDPOINT, 
                headers={"api-key": WHISPER_API_KEY}, 
                files=file, 
                data={"language": "ja", "response_format": "json"}
            )

    os.remove(temp_file_to_remove)
    st.session_state.pop('audio_bytes', None)
    st.session_state['audio_bytes'] = None  # 追加
    return response.json()['text']

# Azure AI Speech のトークンを取得する関数
def get_token(subscription_key):
    fetch_token_url = TTS_TOKEN_ENDPOINT
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)
    print(access_token)
    return access_token

# テキストを音声に変換して再生する関数 - Azure
def text_to_speech_az(input_text):

    TTS_OUTPUT = f'/tmp/{generate_random_filename(length=12, extension="wav")}'

    # AzureのText-to-Speechサービスのエンドポイント
    url = TTS_ENDPOINT

    # SSMLフォーマットのテキスト
    ssml = f"""
    <speak version='1.0' xml:lang='ja-JP'>
        <voice xml:lang='ja-JP' name='ja-JP-MayuNeural'>
            <prosody rate="+15%">
                {input_text}
            </prosody>
        </voice>
    </speak>
    """

    ssml = ssml.encode("utf-8")

    # 必要なヘッダー
    token = get_token(TTS_SUBSCRIPTION_KEY)
    headers = {
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "Content-Type": "application/ssml+xml",
        "Authorization": f"Bearer {token}",  # トークンを適切に設定
        "User-Agent": "aicontactcenter",  # アプリケーション名を設定
    }

    # リクエストを送信して音声データを取得
    response = requests.post(url, headers=headers, data=ssml)

    # 音声データが正常に返されたか確認
    if response.status_code == 200:
        # 音声データをファイルに保存
        with open(TTS_OUTPUT, "wb") as audio_file:
            audio_file.write(response.content)
            print("音声ファイルを保存しました: output.wav")
            autoplay_audio(TTS_OUTPUT)
    else:
        st.write(f"エラー: {response.status_code} - {response.text}")
        st.write(f"Headers: {headers}")
        print(f"エラー: {response.status_code} - {response.text}")

# 音声ファイルを再生する関数
def autoplay_audio(file_path: str):
    audio_placeholder = st.empty()
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        audio_placeholder.empty()
        time.sleep(0.5)
        audio_placeholder.markdown(md, unsafe_allow_html=True)

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

# お問合せ番号を生成する関数
def generate_inquiry_number():
    letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
    numbers = ''.join(random.choice(string.digits) for _ in range(6))
    return f"{letters}{numbers}"

# カスタムスタイルを設定する関数 - Chat History
def set_custom_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #30475e;
        color: white;
    }
    .custom-icon {
        font-size: 20px;
        margin-right: 8px;
    }
    .toggle-dark-light {
        position: absolute;
        top: 20px;
        right: 20px;
    }
    .chat-card {
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        padding: 20px;
        max-width: 75%;
        display: inline-block;
        position: relative;
        background: linear-gradient(135deg, #f0f0f0, #fafafa);
    }
    .chat-card:hover {
        transform: scale(1.03);
    }
    .user-msg {
        background-color: #e0f7fa;
        color: #00796b;
        text-align: left;
        border-left: 5px solid #00796b;
        margin-left: auto;
        border-radius: 15px 15px 0 15px;
    }
    .assistant-msg {
        background-color: #fce4ec;
        color: #c2185b;
        text-align: left;
        border-left: 5px solid #c2185b;
        border-radius: 15px 15px 15px 0;
    }
    .end-message {
        font-size: 24px;
        font-weight: bold;
        color: white;
        background: linear-gradient(135deg, #00796b, #004d40);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton button {
        background-color: #00796b;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #004d40;
    }
    ::-webkit-scrollbar {
        width: 12px;
    }
    ::-webkit-scrollbar-track {
        background: #f0f2f6;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #00796b;
        border-radius: 10px;
        border: 3px solid #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Prompt Flowを実行する関数
def execFlow(question, chat_history):
    result_json = {}

    data = {
        "question": question,
        "chat_history": chat_history,
    }

    print("送信データ:")
    print(data)

    body = str.encode(json.dumps(data))

    url = PROMPT_FLOW_ENDPOINT
    api_key = PROMPT_FLOW_API_KEY
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': PROMPT_FLOW_DEPLOYMENT_NAME} 

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        result_json = json.loads(result.decode('utf-8'))
        print("返信データ:")
        print(result_json)
        answer = result_json['answer']

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

    return result_json

# Streamlitアプリの設定
st.set_page_config(page_title="Contact Center Assistant", page_icon="📞")
st.title('📞 Contact Center Assistant')
st.subheader('Powered by Azure OpenAI Service + Prompt Flow')

set_custom_styles()

# セッションステートの初期化
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'passcode' not in st.session_state:
    st.session_state['passcode'] = ""

if 'isEnd' not in st.session_state:
    st.session_state['isEnd'] = "0"

if 'execCount' not in st.session_state:
    st.session_state['execCount'] = 0

st.session_state['audio_bytes'] = None

if 'inquiry_number' not in st.session_state:
    st.session_state['inquiry_number'] = generate_inquiry_number()

passcode_input = st.text_input("PassCode (入力しないと使えません)", value=st.session_state['passcode'], type='password')
st.session_state['passcode'] = passcode_input

if 'audio_processed' not in st.session_state:
    st.session_state['audio_processed'] = False

if st.session_state['isEnd'] == "0":
    st.session_state['audio_bytes'] = audio_recorder(text="")

if st.session_state['audio_bytes'] is not None:
    st.session_state['audio_processed'] = False  # 音声入力があるたびにフラグをリセット


# お問合せ番号を表示
if 'chat_history' in st.session_state and st.session_state['chat_history']:
    st.subheader(f"お問合せ番号: {st.session_state['inquiry_number']}")


# 音声入力がある場合、音声を文字起こししてPrompt Flowを実行
if st.session_state['isEnd'] == "0" and st.session_state['audio_bytes'] is not None and st.session_state['audio_bytes'] != b'' and not st.session_state['audio_processed'] and st.session_state['passcode'] == PASSCODE:
    progress_text = "処理を開始します"
    placeholder_status = st.progress(0, text=progress_text)
    placeholder_user = st.empty()
    st.session_state['execCount'] = st.session_state['execCount'] + 1
    autoplay_audio("./data/button83.mp3") # for local debug: /workspaces/contact-center-assistant/app/data/button83.mp3
    progress_text = "音声からテキストを生成しています"
    placeholder_status.progress(30, text=progress_text)
    user_prompt_input = speech_to_text(st.session_state['audio_bytes'])
    autoplay_audio("./data/button16.mp3") # for local debug: /workspaces/contact-center-assistant/app/data/button16.mp3
    placeholder_status.empty()
    progress_text = "AIが回答を生成しています"
    placeholder_status.progress(65, text=progress_text)
    placeholder_user.markdown(f'<div class="chat-card user-msg"><i class="fas fa-user custom-icon"></i><strong>あなた:</strong><br> {user_prompt_input}</div>', unsafe_allow_html=True)
    llm_completion_output = execFlow(user_prompt_input, st.session_state['chat_history'])
    new_chat_entry = {
        "inputs": {
            "question": user_prompt_input
        },
        "outputs": {
            "answer": llm_completion_output['answer'],
            "isSummary": llm_completion_output['isSummary']
        }
    }
    st.session_state['chat_history'].append(new_chat_entry)
    st.session_state['isEnd'] = llm_completion_output['isEnd']
    st.session_state['audio_processed'] = True
    autoplay_audio("./data/button83.mp3") # for local debug: /workspaces/contact-center-assistant/app/data/button83.mp3
    placeholder_status.empty()
    progress_text = "回答用の音声を合成しています"
    placeholder_status.progress(100, text=progress_text)
    text_to_speech_az(llm_completion_output['answer'])
    placeholder_status.empty()

if st.session_state['isEnd'] == "1":
    st.markdown('<div class="end-message">この会話は終了しました。ご利用ありがとうございました。</div>', unsafe_allow_html=True)

# チャット履歴を表示
for idx, chat in enumerate(reversed(st.session_state['chat_history'])):
    if 'outputs' in chat and 'answer' in chat['outputs']:
        st.markdown(f'<div class="chat-card assistant-msg"><i class="fas fa-robot custom-icon"></i><strong>Assistant:</strong><br>{chat["outputs"]["answer"]}</div>', unsafe_allow_html=True)
    if 'inputs' in chat and 'question' in chat['inputs']:
        if idx == 0:
            placeholder_user.empty()
        st.markdown(f'<div class="chat-card user-msg"><i class="fas fa-user custom-icon"></i><strong>あなた:</strong><br>{chat["inputs"]["question"]}</div>', unsafe_allow_html=True)