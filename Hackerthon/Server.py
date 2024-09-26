from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import pandas as pd

app = FastAPI()
load_dotenv()
templates = Jinja2Templates(directory="templates")
DATA_FOLDER = "icm20948_data"  # Thư mục lưu file CSV

os.makedirs(DATA_FOLDER, exist_ok=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
print("OpenAI API Key:", openai_api_key)

class ICM20948Data(BaseModel):
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float

record_count = 1  # Biến đếm để tạo tên file mới cho mỗi lần ghi
current_file_path = None  # Đường dẫn tới file CSV hiện tại
icm20948_data_storage = []  # Biến để lưu trữ dữ liệu ICM-20948

@app.get("/display_data", response_class=HTMLResponse)
async def display_data(request: Request):
    return templates.TemplateResponse("display_data.html", {"request": request})

@app.post("/icm20948-data")
async def receive_icm20948_data(data: ICM20948Data):
    global current_file_path, icm20948_data_storage

    print("Received data:", data)  # Hiển thị dữ liệu nhận được
    icm20948_data_storage.append(data.dict())  # Lưu trữ dữ liệu vào danh sách

    # Append data to the current file if it exists
    if current_file_path is not None:
        append_data_to_csv(data, current_file_path)
    else:
        print("No active file. Please create a new file session first.")

    return {"status": "success", "data": data}

@app.post("/new-file")
async def create_new_csv_file():
    global record_count, current_file_path

    # Create a new CSV file and reset the current file path
    current_file_path = create_new_file(record_count)
    record_count += 1
    return {"status": "new file created", "file": current_file_path.name}

def create_new_file(record_id):
    # Create a new file based on the record count
    filename = f"readings_{record_id}_digit_0.csv"
    file_path = Path(DATA_FOLDER) / filename  # Path to the new file
    print(f"Tạo file mới: {filename}")
    return file_path

def append_data_to_csv(data: ICM20948Data, file_path):
    # Convert data to DataFrame
    df = pd.DataFrame([data.dict()])

    # Append data to the current file
    df.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)
    print(f"Lưu dữ liệu vào file: {file_path.name}")

@app.get("/icm20948-data")
async def get_icm20948_data():
    global icm20948_data_storage
    return {"icm20948_data": icm20948_data_storage}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
