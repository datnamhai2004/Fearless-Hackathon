from fastapi import FastAPI
from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI()
load_dotenv()

DATA_FOLDER = "icm20948_data"  # Thư mục lưu file CSV

os.makedirs(DATA_FOLDER, exist_ok=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
print("OpenAI API Key:", openai_api_key)

# Mô hình dữ liệu cho từng mẫu
class ICM20948Data(BaseModel):
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float

record_count = 1079  # Khởi đầu từ 207 để tạo file từ readings_207_digit_2
digit_count = 9   # Bắt đầu từ digit 2
current_file_path = None  # Đường dẫn tới file CSV hiện tại
icm20948_data_storage = []  # Biến để lưu trữ dữ liệu ICM-20948

# Endpoint nhận dữ liệu từ cảm biến, bây giờ nhận danh sách các mẫu
@app.post("/icm20948-data")
async def receive_icm20948_data(data: List[ICM20948Data]):  # Nhận danh sách các mẫu
    global current_file_path, icm20948_data_storage

    print(f"Received {len(data)} data samples")  # Hiển thị số lượng mẫu nhận được
    icm20948_data_storage.extend([d.dict() for d in data])  # Lưu trữ tất cả các mẫu dữ liệu vào danh sách

    # Append data to the current file if it exists
    if current_file_path is not None:
        append_batch_to_csv(data, current_file_path)  # Gọi hàm append mới cho dữ liệu theo lô
    else:
        print("No active file. Please create a new file session first.")

    return {"status": "success", "data_count": len(data)}

@app.post("/new-file")
async def create_new_csv_file():
    global record_count, digit_count, current_file_path

    # Create a new CSV file and reset the current file path
    current_file_path = create_new_file(record_count, digit_count)
    record_count += 1  # Tăng record_count thêm 1 để tạo các file liên tiếp
    return {"status": "new file created", "file": current_file_path.name}

def create_new_file(record_id, digit_id):
    # Create a new file based on the record count and digit count
    filename = f"readings_{record_id}_digit_{digit_id}.csv"
    file_path = Path(DATA_FOLDER) / filename  # Path to the new file
    print(f"Tạo file mới: {filename}")
    return file_path

# Hàm mới để append danh sách dữ liệu vào CSV
def append_batch_to_csv(data: List[ICM20948Data], file_path):
    # Convert list of data to DataFrame
    df = pd.DataFrame([d.dict() for d in data])

    # Append batch of data to the current file
    df.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)
    print(f"Lưu {len(data)} mẫu dữ liệu vào file: {file_path.name}")

@app.get("/icm20948-data")
async def get_icm20948_data():
    global icm20948_data_storage
    return {"icm20948_data": icm20948_data_storage}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
