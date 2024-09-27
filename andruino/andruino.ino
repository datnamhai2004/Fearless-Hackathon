#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ICM20948_WE.h>  // Thư viện ICM20948_WE
#include <vector>

#define ICM20948_ADDR 0x68  // Địa chỉ I2C của ICM20948
#define BUTTON_PIN 5         // Khai báo chân GPIO của nút nhấn

// Cấu hình Wi-Fi
const char* ssid = "Swinburne";         
const char* password = "Swinburne@2019";  

// Cấu hình server
const char* serverNameICM = "https://2c85-58-187-108-123.ngrok-free.app/icm20948-data";  
const char* serverNameNewFile = "https://2c85-58-187-108-123.ngrok-free.app/new-file";  // Endpoint tạo file mới

ICM20948_WE myIMU(ICM20948_ADDR);  // Khởi tạo đối tượng ICM20948_WE

// Biến để kiểm tra trạng thái ghi dữ liệu
bool isRecording = false;  
bool buttonWasPressed = false; // Trạng thái nút trước đó

std::vector<String> dataBatch; // Mảng lưu trữ dữ liệu theo lô
const int batchSize = 10;      // Kích thước của lô dữ liệu trước khi gửi

void setup() {
  Serial.begin(115200);
  Serial.println("Setup bắt đầu");

  // Kết nối Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối Wi-Fi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("Đã kết nối Wi-Fi");

  // Khởi động cảm biến ICM-20948
  Serial.println("Khởi động ICM20948");
  Wire.begin();
  if (!myIMU.init()) {
    Serial.println("ICM20948 không phản hồi");
    while (1);
  }
  Serial.println("ICM20948 đã kết nối");

  // Hiệu chuẩn cảm biến
  Serial.println("Đặt cảm biến ICM20948 trên mặt phẳng, đang hiệu chuẩn...");
  delay(1000);
  myIMU.autoOffsets();
  Serial.println("Hiệu chuẩn hoàn tất!");

  // Cấu hình cảm biến ICM20948 cho 200 Hz
  Serial.println("Cấu hình cảm biến ICM20948 cho 200 Hz");
  myIMU.setAccRange(ICM20948_ACC_RANGE_2G);         // Thiết lập dải đo gia tốc
  myIMU.setAccDLPF(ICM20948_DLPF_6);                // Lọc thông dải
  myIMU.setAccSampleRateDivider(4);                 // Thiết lập bộ chia tần số mẫu để đạt 200 Hz
  myIMU.setGyrSampleRateDivider(4);                 // Thiết lập bộ chia tần số mẫu của con quay hồi chuyển để đạt 200 Hz

  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Thiết lập nút nhấn
  Serial.println("Setup hoàn tất");
}

void createNewFile() {
  Serial.println("Bắt đầu tạo file mới");
  // Gửi yêu cầu tạo file mới tới server
  HTTPClient http;
  http.begin(serverNameNewFile);
  int httpResponseCode = http.POST("");  // Gửi yêu cầu POST tới endpoint tạo file mới

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Mã phản hồi HTTP (Tạo file mới): "); Serial.println(httpResponseCode);
    Serial.println("Phản hồi từ server: " + response);
  } else {
    Serial.print("Lỗi khi gửi yêu cầu tạo file mới: ");
    Serial.println(httpResponseCode);
  }

  http.end();  // Đóng kết nối
  Serial.println("Hoàn tất tạo file mới");
}

void sendBatchData() {
  if (dataBatch.size() == 0) {
    return;  // Không có dữ liệu để gửi
  }
  
  String jsonPayload = "[" + join(dataBatch, ",") + "]"; // Kết hợp các dữ liệu thành một chuỗi JSON
  sendData(jsonPayload); // Gửi dữ liệu
  dataBatch.clear(); // Xóa mảng sau khi gửi
}

String join(const std::vector<String>& vec, const String& delimiter) {
  String result;
  for (size_t i = 0; i < vec.size(); i++) {
    result += vec[i];
    if (i < vec.size() - 1) result += delimiter;
  }
  return result;
}

void sendData(String jsonPayload) {
  unsigned long startTime = millis();
  Serial.println("Bắt đầu gửi dữ liệu");
  HTTPClient http;
  http.begin(serverNameICM);
  http.addHeader("Content-Type", "application/json");  // Thiết lập kiểu dữ liệu là JSON

  int httpResponseCode = http.POST(jsonPayload);  // Gửi yêu cầu POST
  unsigned long sendTime = millis() - startTime;
  Serial.print("Thời gian gửi dữ liệu: "); Serial.println(sendTime);  // Thời gian gửi dữ liệu

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Mã phản hồi HTTP: "); Serial.println(httpResponseCode);
    Serial.println("Phản hồi từ server: " + response);
  } else {
    Serial.print("Lỗi khi gửi yêu cầu POST: ");
    Serial.println(httpResponseCode);
  }

  http.end();  // Đóng kết nối
  Serial.println("Hoàn tất gửi dữ liệu");
}

void loop() {
  Serial.println("Bắt đầu loop");

  // Đọc trạng thái hiện tại của nút nhấn
  bool buttonPressed = digitalRead(BUTTON_PIN) == LOW;
  Serial.print("Trạng thái nút nhấn: ");
  Serial.println(buttonPressed ? "Được nhấn" : "Không nhấn");

  if (buttonPressed && !buttonWasPressed) {  // Khi nút nhấn được kích hoạt lần đầu tiên
    Serial.println("Nút nhấn được kích hoạt");
    createNewFile();  // Gọi hàm tạo file mới
    isRecording = true;  // Bắt đầu ghi
    Serial.println("Ghi dữ liệu: ON");
  } else if (!buttonPressed && buttonWasPressed) {  // Khi nút nhấn được nhả ra
    if (isRecording) {
      Serial.println("Nút nhấn được nhả ra, dừng ghi dữ liệu");
      isRecording = false;  // Dừng ghi
      Serial.println("Ghi dữ liệu: OFF");
      sendBatchData(); // Gửi bất kỳ dữ liệu còn lại nào khi dừng ghi
    }
  }

  buttonWasPressed = buttonPressed;  // Cập nhật trạng thái nút

  Serial.print("Wi-Fi trạng thái: ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "Đã kết nối" : "Chưa kết nối");

  if (WiFi.status() == WL_CONNECTED && isRecording) {
    Serial.println("Đang ghi dữ liệu từ cảm biến");

    // Đọc dữ liệu từ cảm biến ICM-20948
    myIMU.readSensor();

    xyzFloat accRaw = myIMU.getAccRawValues();   // Lấy giá trị gia tốc
    xyzFloat gVal = myIMU.getGValues();          // Lấy giá trị con quay hồi chuyển

    // Tạo JSON cho từng mẫu dữ liệu
    String jsonPayloadICM = "{\"acc_x\": " + String(accRaw.x) + 
                            ", \"acc_y\": " + String(accRaw.y) + 
                            ", \"acc_z\": " + String(accRaw.z) + 
                            ", \"gyro_x\": " + String(gVal.x) + 
                            ", \"gyro_y\": " + String(gVal.y) + 
                            ", \"gyro_z\": " + String(gVal.z) + "}";

    // Lưu vào mảng
    dataBatch.push_back(jsonPayloadICM);

    // Nếu mảng có đủ số lượng mẫu, gửi tất cả lên server
    if (dataBatch.size() >= batchSize) {
      sendBatchData();
    }

    delay(3.5);  // Giảm độ trễ để đạt gần 200 Hz (1/200 = 5ms)
  } else {
    Serial.println("Không ghi dữ liệu: Điều kiện không thỏa mãn");
  }

  Serial.println("Kết thúc loop");
}
