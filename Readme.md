# Hệ Thống Phát Hiện Vật Thể Bị Đánh Cắp

Hệ thống giám sát và phát hiện vật thể bị mất sử dụng YOLO và OpenCV, với giao diện web thời gian thực.

## Chức năng chính

### 1. Phát hiện và theo dõi vật thể
- Phát hiện vật thể trong khung hình

- Tạo mask cho các vật thể được phát hiện

- Theo dõi vị trí và trạng thái của vật thể theo thời gian thực

### 2. Xác định frame tham chiếu

- Cho phép người dùng chọn frame tham chiếu bằng cách nhấn phím 'q'

- Lưu trữ thông tin về vị trí và mask của các vật thể trong frame tham chiếu

- Sử dụng làm cơ sở để so sánh với các frame tiếp theo

### 3. Phát hiện vật thể bị mất

- So sánh frame hiện tại với frame tham chiếu

- Tính toán tỷ lệ diện tích bị mất của vật thể

- Phát hiện khi vật thể bị mất với ngưỡng > 90% diện tích

### 4. Giao diện web thời gian thực

- Hiển thị luồng video từ camera

- Hiển thị trạng thái hệ thống

- Danh sách cảnh báo gần đây

- Thông báo pop-up khi phát hiện vật thể bị mất

### 5. Hệ thống cảnh báo

- Hiển thị cảnh báo trực quan trên video stream

- Gửi thông báo realtime qua WebSocket

- Lưu trữ lịch sử cảnh báo

- Phát âm thanh khi có cảnh báo

### 6. Xử lý hình ảnh

- Xử lý nhiễu sử dụng morphological operations

- Tạo overlay hiển thị vùng tham chiếu

- Vẽ khung và nhãn cho vật thể bị phát hiện

- Hiển thị FPS và thông tin performance

## Công nghệ sử dụng

- YOLO (You Only Look Once) cho object detection

- OpenCV cho xử lý hình ảnh

- Flask và Flask-SocketIO cho web server

- WebSocket cho realtime communication

- HTML/CSS/JavaScript cho frontend

<h2>Cài đặt và Sử dụng</h2>

Nên chạy app.py vì nhẹ hơn main.py
