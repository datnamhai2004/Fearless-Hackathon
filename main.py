from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse 
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import JSONResponse
import os
import datetime
from gtts import gTTS
import openai

import speech_recognition as sr
from pydub import AudioSegment
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
AUDIO_FOLDER = "frontend/audio" 
os.makedirs(AUDIO_FOLDER, exist_ok=True)
openai.api_key = os.getenv('OPENAI_API_KEY')
AUDIO_FOLDER = "frontend/audio" 
CHAT_HISTORY_FILE = "chat_history.txt"
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
templates = Jinja2Templates(directory="frontend")
app.mount("/static", StaticFiles(directory="frontend"), name="static")
Name = ' bien '
Age = 20
can = '56 kg'
cao = '1m7'

def generate_response(user_input):

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Bạn là một trợ lý về sức khỏe của tôi bạn hãy đọc kĩ và ghi nhớ thông tin của tôi. Tôi là {Name} tôi {Age} tuổi tôi cao {cao}số cân của tôi là {can}"},
            {"role": "user", "content": user_input}
        ]
    )
    response_text = completion.choices[0].message['content']

    # Tạo audio từ văn bản phản hồi
    tts = gTTS(response_text, lang='vi')
    audio_filename = f"response_audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    audio_filepath = os.path.join("frontend/audio", audio_filename)
    tts.save(audio_filepath)

    return response_text, audio_filename
def save_chat_history(user_input: str, response: str):
    with open(CHAT_HISTORY_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        f.write(f"{timestamp} - User: {user_input}\n")
        f.write(f"{timestamp} - Bot: {response}\n\n")

def generate_voice_response(response: str):
    tts = gTTS(response, lang='en')
    filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    audio_path = os.path.join(AUDIO_FOLDER, filename)
    tts.save(audio_path)
    return filename


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=JSONResponse)
async def chat(user_input: str = Form(...)):
    response_text, audio_filename = generate_response(user_input)
    save_chat_history(user_input, response_text)
    
    return {
        "user_input": user_input,
        "response": response_text,
        "audio_url": f"/frontend/audio/{audio_filename}"
    }

def convert_audio_to_wav(input_file_path: str, output_file_path: str):
    audio = AudioSegment.from_file(input_file_path)
    audio.export(output_file_path, format="wav")
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            lines = f.readlines()
            formatted_lines = []
            for line in lines:
                # Phân biệt User và Bot
                if "User:" in line:
                    formatted_lines.append(f"<div class='chat-message user'>{line.strip()}</div>")
                else:
                    formatted_lines.append(f"<div class='chat-message bot'>{line.strip()}</div>")

          
            return formatted_lines
    return []

@app.post("/chat-voice", response_class=JSONResponse)
async def chat_voice(voice: UploadFile = File(...)):
    # Save the uploaded file
    audio_path = os.path.join(AUDIO_FOLDER, voice.filename)
    with open(audio_path, "wb") as f:
        f.write(voice.file.read())

    # Convert the uploaded audio file to WAV format
    wav_audio_path = audio_path.rsplit(".", 1)[0] + ".wav"
    convert_audio_to_wav(audio_path, wav_audio_path)

    # Convert audio to text using speech_recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_audio_path) as source:
        audio_data = recognizer.record(source)
        user_input = recognizer.recognize_google(audio_data, language="vi-VN")

    # Generate response and save it as an audio file
    response_text, audio_filename = generate_response(user_input)

    return {
        "response": response_text,
        "audio_url": f"/frontend/audio/{audio_filename}"
    }

@app.get("/chats", response_class=HTMLResponse)
async def read_chats(request: Request):
    chat_history = load_chat_history()
   
    return templates.TemplateResponse("chats.html", {"request": request, "chat_history": chat_history})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


