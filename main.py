import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
import threading
import queue
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Queue để truyền frame giữa các thread
frame_queue = queue.Queue(maxsize=10)
alert_queue = queue.Queue(maxsize=10)

# Thêm các biến config toàn cục
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MODEL_SIZE = 480
CONFIDENCE_THRESHOLD = 0.4
MISSING_RATIO_THRESHOLD = 0.9
MIN_CONTOUR_AREA = 500

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def alert_missing_object(class_name):
    alert_data = {
        'type': 'notification',
        'message': f'Cảnh báo: Đối tượng {class_name} đã bị mất!',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    socketio.emit('alert', alert_data)

def detection_thread():
    detector = YOLO('yolo11n-seg.onnx')
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    print("Nhấn 'q' để xác nhận frame tham chiếu...")
    
    while True:
        ret, ref_frame = cap.read()
        if not ret:
            print("Không thể đọc camera!")
            return
            
        cv2.putText(ref_frame, "Press 'q' to confirm reference frame", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Reference Frame Preview", ref_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyWindow("Reference Frame Preview")
            break
    
    print("Đã xác nhận frame tham chiếu!")
    
    ref_results = detector.predict(ref_frame, imgsz=MODEL_SIZE, conf=CONFIDENCE_THRESHOLD)
    ref_combined_mask, ref_contours = process_reference_frame(ref_frame, ref_results)
    
    prev_frame_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        current_time = time.time()
        fps = 1/(current_time - prev_frame_time)
        prev_frame_time = current_time
        
        current_results = detector.predict(frame, imgsz=MODEL_SIZE, conf=CONFIDENCE_THRESHOLD)
        current_combined_mask = process_current_frame(frame, current_results)
        
        # Xử lý nhiễu
        kernel = np.ones((3,3), np.uint8)
        diff_mask = cv2.absdiff(ref_combined_mask, current_combined_mask)
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_OPEN, kernel)
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_CLOSE, kernel)
        
        # Tạo overlay
        overlay = frame.copy()
        
        # Xử lý vật thể bị mất
        for contour in ref_contours:
            missing_ratio = calculate_missing_ratio(contour, current_combined_mask)
            cv2.fillPoly(overlay, [contour], (0,255,0))
            
            if missing_ratio >= MISSING_RATIO_THRESHOLD:
                x, y, w, h = cv2.boundingRect(contour)
                class_name = get_object_name(x, y, w, h, current_results, detector.names)
                if class_name:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
                    cv2.putText(frame, f"{class_name} MISSING", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
                    alert_missing_object(class_name)
        
        # Blend overlay
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Hiển thị FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if not frame_queue.full():
            frame_queue.put(frame)

def process_reference_frame(frame, results):
    combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    if len(results) > 0:
        for result in results:
            if result.masks is not None:
                for mask in result.masks.data:
                    mask_np = mask.cpu().numpy()
                    mask_resized = cv2.resize(mask_np, (frame.shape[1], frame.shape[0]))
                    binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255
                    combined_mask = cv2.bitwise_or(combined_mask, binary_mask)
    
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cont for cont in contours if cv2.contourArea(cont) > 500]
    return combined_mask, contours

def process_missing_objects(frame, ref_contours, current_mask, current_results, class_names):
    for contour in ref_contours:
        missing_ratio = calculate_missing_ratio(contour, current_mask)
        if missing_ratio >= 0.9:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
            
            # Tìm tên đối tượng từ kết quả hiện tại
            class_name = get_object_name(x, y, w, h, current_results, class_names)
            if class_name:
                alert_missing_object(class_name)

def start_server():
    # Khởi động thread xử lý video
    video_thread = threading.Thread(target=detection_thread)
    video_thread.daemon = True
    video_thread.start()
    
    # Khởi động Flask server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

def get_reference_frame(cap):
    """Lấy frame tham chiếu từ camera"""
    while True:
        ret, frame = cap.read()
        if ret:
            return frame
    return None

def process_current_frame(frame, results):
    """Xử lý frame hiện tại để tạo mask"""
    combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    if len(results) > 0:
        for result in results:
            if result.masks is not None:
                for mask in result.masks.data:
                    mask_np = mask.cpu().numpy()
                    mask_resized = cv2.resize(mask_np, (frame.shape[1], frame.shape[0]))
                    binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255
                    combined_mask = cv2.bitwise_or(combined_mask, binary_mask)
    return combined_mask

def calculate_missing_ratio(ref_contour, current_mask):
    # Tạo mask từ contour tham chiếu
    ref_mask = np.zeros_like(current_mask)
    cv2.fillPoly(ref_mask, [ref_contour], 255)
    
    # Tính diện tích ban đầu
    original_area = cv2.countNonZero(ref_mask)
    
    # Tính diện tích còn lại
    remaining_mask = cv2.bitwise_and(ref_mask, current_mask)
    remaining_area = cv2.countNonZero(remaining_mask)
    
    # Tính tỷ lệ mất đi
    if original_area == 0:
        return 0
    return 1 - (remaining_area / original_area)

def get_object_name(x, y, w, h, current_results, class_names):
    """Lấy tên đối tượng dựa trên vị trí bounding box"""
    center_x = x + w/2
    center_y = y + h/2
    
    if len(current_results) > 0:
        for result in current_results:
            if result.boxes is not None:
                for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
                    box = box.cpu().numpy()
                    if (box[0] <= center_x <= box[2] and 
                        box[1] <= center_y <= box[3]):
                        return class_names[int(cls)]
    return None

if __name__ == "__main__":
    start_server()