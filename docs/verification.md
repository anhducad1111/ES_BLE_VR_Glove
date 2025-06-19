# Hướng Dẫn Kiểm Thử Phần Mềm

## 1. Kiểm Thử Connection

### 1.1 Wireless Connect

Cách thực hiện:

1. Chuẩn bị:
   - Thiết bị VR Glove đã sạc đầy
   - Laptop có BLE 4.0+
   - Phần mềm đã cài đặt

2. Test Auto-discovery:
   - Bật thiết bị
   - Khởi động phần mềm
   - Bấm giờ từ lúc bắt đầu scan
   - Ghi nhận thời gian phát hiện (yêu cầu <3s)

3. Test Connection:
   - Click connect khi thấy thiết bị
   - Bấm giờ đến khi kết nối thành công
   - Ghi nhận thời gian (yêu cầu <10s)
   - Lặp lại 100 lần để test độ ổn định

4. Test Stability:
   - Để thiết bị kết nối liên tục 24h
   - Theo dõi log disconnect
   - Ghi nhận số lần mất kết nối

5. Test Auto-reconnect:
   - Ngắt kết nối (tắt thiết bị)
   - Bật lại thiết bị
   - Bấm giờ đến khi tự kết nối lại
   - Kiểm tra thời gian (yêu cầu <5s)

### 1.2 Battery Info

1. Test Monitor:
   - Kết nối thiết bị
   - Kiểm tra hiển thị pin (0-100%)
   - So sánh với đồng hồ đo (sai số cho phép ±1%)

2. Test Charging:
   - Cắm sạc thiết bị
   - Kiểm tra update trạng thái charging
   - Theo dõi % pin tăng

### 1.3 Device Info

1. Kiểm tra hiển thị:
   - Firmware version
   - Hardware version
   - Model name
   - Manufacturer

2. Verify thông tin:
   - So sánh với thông số thực tế
   - Kiểm tra format hiển thị

## 2. Kiểm Thử Motion Sensors

### 2.1 IMU Configuration

1. Test Frequency:
   - Vào phần IMU Config
   - Thử các mức tần số:
     - IMU1: 208Hz, 80Hz
     - IMU2: 416Hz, 80Hz
   - Verify tần số đã thay đổi

2. Test Range:
   - Thay đổi range cho sensors:
     - Accelerometer: ±2G
     - Gyroscope: ±250DPS
     - Magnetometer: ±4 Gauss
   - Verify range đã update

### 2.2 IMU Display

1. Test Raw Data:
   - Quan sát giá trị raw
   - Kiểm tra đơn vị:
     - Accel: mg
     - Gyro: rad/s
     - Mag: uT
   - Verify dữ liệu update realtime

2. Test Calibration:
   - Thực hiện zero calibration
   - Kiểm tra offset values
   - Verify độ drift <1%

## 3. Kiểm Thử Controls

### 3.1 Joystick

1. Test Range:
   - Di chuyển joystick full range
   - Verify giá trị 0-4095
   - Kiểm tra deadzone ±100

2. Test Center:
   - Để joystick ở giữa
   - Verify sai số ±1.5%
   - Kiểm tra response time <50ms

### 3.2 Buttons

1. Test Response:
   - Nhấn từng button
   - Verify debounce 20ms
   - Kiểm tra response <50ms

2. Test Multi-press:
   - Nhấn nhiều buttons
   - Verify detect đúng
   - Kiểm tra state updates

### 3.3 Sensors

1. Test Pressure:
   - Tác động lực khác nhau
   - Verify giá trị thay đổi
   - Kiểm tra range đo

2. Test Flex:
   - Uốn từng ngón tay
   - Verify giá trị cảm biến
   - Kiểm tra độ chính xác

## 4. Kiểm Thử Display

### 4.1 Layout Test

1. Window Sizing:
   - Thay đổi kích thước cửa sổ
   - Verify UI scale đúng
   - Kiểm tra không overlap

### 4.2 Status Display

1. Test Connection Status:
   - Theo dõi status updates
   - Verify error messages
   - Kiểm tra visibility

### 4.3 BLE Controls

1. Test On/Off:
   - Bật/tắt Bluetooth
   - Verify status updates
   - Kiểm tra error handling

2. Test Autoreconnect:
   - Disconnect thiết bị
   - Verify 5 lần retry
   - Kiểm tra interval 5s

## 5. Data Logging

### 5.1 Setup Logging

1. Chuẩn bị:
   - Tạo thư mục lưu log
   - Chọn định dạng file
   - Set log levels

2. Verify Data:
   - Kiểm tra log IMU
   - Kiểm tra log sensors
   - Verify không mất data

## 6. Lưu Ý Quan Trọng

### 6.1 Test Environment

- Windows 10/11
- BLE 4.0+ support
- USB 2.0/3.0 ports

### 6.2 Evidence Collection

1. Log Files:
   - Console logs
   - Error logs
   - Performance data

2. Test Records:
   - Screenshots
   - Video clips
   - Measurement data
