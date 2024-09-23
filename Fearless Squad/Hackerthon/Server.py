from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse 
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import datetime
from gtts import gTTS
import openai
from dotenv import load_dotenv 
from pydantic import BaseModel

app = FastAPI() 
load_dotenv() 
templates = Jinja2Templates(directory="templates") 
UPLOAD_FOLDER = "uploads" 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key
print("OpenAI API Key:", openai_api_key)

# Định nghĩa lớp dữ liệu cảm biến lực
class SensorData(BaseModel):
    sensor1: int
    sensor2: int
    sensor3: int

# Định nghĩa lớp dữ liệu ADXL345
class ADXL345Data(BaseModel):
    adxl_x: float
    adxl_y: float
    adxl_z: float

sensor_data_storage = []  # Biến để lưu trữ dữ liệu cảm biến lực
adxl345_data_storage = []  # Biến để lưu trữ dữ liệu ADXL345

@app.get("/display-data", response_class=HTMLResponse)
async def display_data(request: Request):
    return templates.TemplateResponse("display_data.html", {"request": request})

# API nhận dữ liệu POST từ cảm biến lực và lưu trữ
@app.post("/display-data")
async def receive_sensor_data(data: SensorData):
    sensor_data_storage.append(data.dict())  # Lưu trữ dữ liệu cảm biến lực
    return {"status": "success", "data": data}

# API nhận dữ liệu POST từ cảm biến ADXL345 và lưu trữ
@app.post("/adxl345-data")
async def receive_adxl345_data(data: ADXL345Data):
    adxl345_data_storage.append(data.dict())
    return {"status": "success", "data": data}

@app.get("/sensor-data")
async def get_sensor_data():
    return {"sensor_data": sensor_data_storage}

@app.get("/adxl345-data")
async def get_adxl345_data():
    return {"adxl345_data": adxl345_data_storage}

# Xóa dữ liệu cảm biến
@app.post("/clean-sensor-data")
async def clean_sensor_data():
    global sensor_data_storage
    sensor_data_storage = []  
    return {"status": "success"}

# Xóa dữ liệu ADXL345
@app.post("/clean-adxl345-data")
async def clean_adxl345_data():
    global adxl345_data_storage  
    adxl345_data_storage = []  
    return {"status": "success"}

def generate_response(user_input):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn hãy đọc kỹ yêu cầu là bạn là ai và công việc của bạn là gì..."},
                {"role": "user", "content": user_input}
            ]
        )
        response = completion.choices[0].message['content']
        return response
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Error generating response."

def generate_audio_file(text):
    try:
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        filename = f"speech_{timestamp}.mp3"
        speech_file_path = Path(UPLOAD_FOLDER) / filename
        tts = gTTS(text=text, lang='vi')
        tts.save(speech_file_path)
        return filename
    except Exception as e:
        print(f"Error generating audio file: {e}")
        return None

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
