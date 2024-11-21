# Hệ Thống Phát Hiện Vật Thể Bị Đánh Cắp

<div align="center">

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" />
  <img src="https://img.shields.io/badge/OpenCV-4.5+-green.svg" />
  <img src="https://img.shields.io/badge/YOLO-v8-yellow.svg" />
  <img src="https://img.shields.io/badge/Flask-2.0+-red.svg" />
</p>

## Sơ đồ hoạt động

```mermaid
graph TD
    A[Camera Input] --> B[Frame tham chiếu]
    B --> C{Phát hiện vật thể}
    C --> |YOLO| D[Tạo mask]
    D --> E[So sánh với frame hiện tại]
    E --> F{Kiểm tra mất vật thể}
    F --> |>90%| G[Cảnh báo]
    G --> H[WebSocket]
    H --> I[Thông báo]
    F --> |<90%| J[Tiếp tục theo dõi]
    J --> E
```

```mermaid
sequenceDiagram
    participant Camera
    participant YOLO
    participant Server
    participant WebSocket
    participant UI

    Camera->>YOLO: Gửi frame
    YOLO->>Server: Phát hiện vật thể
    Server->>Server: Xử lý mask
    Server->>Server: So sánh frame
    Server->>WebSocket: Gửi cảnh báo
    WebSocket->>UI: Hiển thị thông báo
    UI->>UI: Animation & Sound
```

## Chức năng chính

<details>
<summary>1. Phát hiện và theo dõi vật thể 🔍</summary>

- Phát hiện vật thể trong khung hình
- Tạo mask cho các vật thể được phát hiện  
- Theo dõi vị trí và trạng thái theo thời gian thực

</details>

<details>
<summary>2. Xác định frame tham chiếu 📸</summary>

- Cho phép người dùng chọn frame tham chiếu bằng phím 'q'
- Lưu trữ thông tin vị trí và mask của vật thể
- Làm cơ sở so sánh với các frame tiếp theo

</details>

<details>
<summary>3. Phát hiện vật thể bị mất 🚨</summary>

- So sánh frame hiện tại với frame tham chiếu
- Tính toán tỷ lệ diện tích bị mất
- Phát hiện khi vật thể bị mất >90% diện tích

</details>

<details>
<summary>4. Giao diện web thời gian thực 💻</summary>

- Hiển thị luồng video từ camera
- Hiển thị trạng thái hệ thống
- Danh sách cảnh báo gần đây
- Thông báo pop-up khi phát hiện mất

</details>

## Cài đặt và Sử dụng

<div class="animate__animated animate__fadeIn">

1. Clone repository:

```bash
git clone https://github.com/yourusername/object-detection.git
```

2. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
python app.py
```

4. Truy cập: http://localhost:5000

</div>

## Công nghệ sử dụng

<div class="tech-stack animate__animated animate__fadeInUp">

- 🔹 YOLO (You Only Look Once)
- 🔸 OpenCV 
- 🔹 Flask & Flask-SocketIO
- 🔸 WebSocket
- 🔹 HTML/CSS/JavaScript

</div>

<style>
.animate__animated {
  animation-duration: 1s;
}

.animate__fadeIn {
  animation-name: fadeIn;
}

.animate__fadeInUp {
  animation-name: fadeInUp;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 40px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.tech-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}
</style>
```
