#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Cấu hình Wi-Fi
const char* ssid = "TP-Link_C7FE";         
const char* password = "62270557";  

// Cấu hình server
const char* serverNameForce = "https://c72b-14-231-178-6.ngrok-free.app/display-data";  
const char* serverNameADXL = "https://c72b-14-231-178-6.ngrok-free.app/adxl345-data";  

// Cấu hình chân cảm biến
const int sensorPin1 = 32;  // GPIO 32
const int sensorPin2 = 34;  // GPIO 34
const int sensorPin3 = 35;  // GPIO 35

// Khởi tạo cảm biến ADXL345
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();

void setup() {
  Serial.begin(115200);
  
  // Kết nối Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối Wi-Fi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("Đã kết nối Wi-Fi");

  // Khởi động cảm biến ADXL345
  if (!accel.begin()) {
    Serial.println("Không thể tìm thấy ADXL345");
    while (1);
  }
  
  // Thiết lập độ nhạy của cảm biến
  accel.setRange(ADXL345_RANGE_16_G);
}

void sendData(const char* serverName, String jsonPayload) {
  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");  // Thiết lập kiểu dữ liệu là JSON

  int httpResponseCode = http.POST(jsonPayload);  // Gửi yêu cầu POST

  // Kiểm tra phản hồi
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("HTTP Response code: "); Serial.println(httpResponseCode);
    Serial.println("Response from server: " + response);
  } else {
    Serial.print("Error in sending POST request: ");
    Serial.println(httpResponseCode);
  }

  http.end();  // Đóng kết nối
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Đọc giá trị từ cảm biến lực
    int sensorValue1 = analogRead(sensorPin1);
    int sensorValue2 = analogRead(sensorPin2);
    int sensorValue3 = analogRead(sensorPin3);

    // Đọc dữ liệu từ cảm biến ADXL345
    sensors_event_t event;
    accel.getEvent(&event);

    // In giá trị ra serial monitor
    Serial.print("Sensor 1: "); Serial.println(sensorValue1);
    Serial.print("Sensor 2: "); Serial.println(sensorValue2);
    Serial.print("Sensor 3: "); Serial.println(sensorValue3);
    Serial.print("ADXL345 - X: "); Serial.print(event.acceleration.x); 
    Serial.print(" m/s^2, Y: "); Serial.print(event.acceleration.y); 
    Serial.print(" m/s^2, Z: "); Serial.println(event.acceleration.z); 

    // Tạo JSON để gửi cho cảm biến lực
    String jsonPayloadForce = "{\"sensor1\": " + String(sensorValue1) + 
                               ", \"sensor2\": " + String(sensorValue2) + 
                               ", \"sensor3\": " + String(sensorValue3) + "}";

    // Tạo JSON để gửi cho ADXL345
    String jsonPayloadADXL = "{\"adxl_x\": " + String(event.acceleration.x) + 
                             ", \"adxl_y\": " + String(event.acceleration.y) + 
                             ", \"adxl_z\": " + String(event.acceleration.z) + "}";

    // Gửi dữ liệu cảm biến lực
    sendData(serverNameForce, jsonPayloadForce);

    // Gửi dữ liệu ADXL345
    sendData(serverNameADXL, jsonPayloadADXL);

  } else {
    Serial.println("Không kết nối được Wi-Fi");
  }

  delay(2000);  // Chờ 2 giây trước khi gửi dữ liệu tiếp theo
}
