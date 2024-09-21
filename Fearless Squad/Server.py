from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse 
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import datetime
from gtts import gTTS
import openai
from dotenv import load_dotenv 
app = FastAPI() 
load_dotenv() 
templates = Jinja2Templates(directory="templates") 
UPLOAD_FOLDER = "uploads" 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')


def generate_response(user_input): 
    completion = openai.ChatCompletion.create( 
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Bạn hãy đọc kỹ yêu cầu là bạn là ai và công việc của bạn là gì..."},
            {"role": "user", "content": user_input}
        ]
    )
    response = completion.choices[0].message['content'] 
    return response

def generate_audio_file(text):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    filename = f"speech_{timestamp}.mp3"
    speech_file_path = Path(UPLOAD_FOLDER) / filename
    tts = gTTS(text=text, lang='en')
    tts.save(speech_file_path)
    return filename

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=HTMLResponse) 
async def chat(request: Request, user_input: str = Form(...)): 
    response = generate_response(user_input) 
    audio_file = generate_audio_file(response)  
    return templates.TemplateResponse("index.html", { 
        "request": request,
        "user_input": user_input,
        "response": response,
        "audio_file": audio_file
    })

@app.get("/audio/{filename}", response_class=FileResponse) 
async def audio(filename: str): 
    file_path = Path(UPLOAD_FOLDER) / filename
    return FileResponse(file_path) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
     