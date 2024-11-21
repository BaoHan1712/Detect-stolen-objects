import cv2
import numpy as np
from ultralytics import YOLO


def main():
    detector = YOLO('yolo11n-seg.onnx')
    cap = cv2.VideoCapture(0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Đang chụp frame tham chiếu...")
    

    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < 3:
        ret, ref_frame = cap.read()
        if ret:
            cv2.imshow("Chuẩn bị tham chiếu", ref_frame)
            if cv2.waitKey(1) & 0xFF == ord('c'):  
                break
    
    ret, ref_frame = cap.read()
    if not ret:
        print("Không thể đọc camera!")
        return
    
    try:
        cv2.destroyWindow("Chuẩn bị tham chiếu")
    except:
        pass
    
    print("Đã chụp frame tham chiếu!")
    
    # Phát hiện đối tượng trong frame tham chiếu
    ref_results = detector.predict(ref_frame, imgsz=480, conf=0.4)
    
    # Tạo mask tổng hợp cho frame tham chiếu
    ref_combined_mask = np.zeros(ref_frame.shape[:2], dtype=np.uint8)
    if len(ref_results) > 0:
        for result in ref_results:
            if result.masks is not None:
                for mask in result.masks.data:
                    mask_np = mask.cpu().numpy()
                    mask_resized = cv2.resize(mask_np, 
                                           (ref_frame.shape[1], ref_frame.shape[0]))
                    binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255
                    ref_combined_mask = cv2.bitwise_or(ref_combined_mask, binary_mask)
    
    # Lưu contours của frame tham chiếu
    ref_contours, _ = cv2.findContours(ref_combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ref_contours = [cont for cont in ref_contours if cv2.contourArea(cont) > 500]  # Lọc nhiễu nhỏ
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        current_results = detector.predict(frame, imgsz=480, conf=0.4)
        

        current_objects = []
        if len(current_results) > 0:
            for result in current_results[0].boxes.data:
                x1, y1, x2, y2, conf, class_id = result
                class_id = int(class_id)
                class_name = detector.names[class_id]
                current_objects.append({
                    'name': class_name,
                    'box': (int(x1), int(y1), int(x2), int(y2)),
                    'conf': conf
                })
        
        # Tạo mask cho frame hiện tại
        current_combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        if len(current_results) > 0:
            for result in current_results:
                if result.masks is not None:
                    for mask in result.masks.data:
                        mask_np = mask.cpu().numpy()
                        mask_resized = cv2.resize(mask_np, (frame.shape[1], frame.shape[0]))
                        binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255
                        current_combined_mask = cv2.bitwise_or(current_combined_mask, binary_mask)
        
        # Tìm sự khác biệt
        diff_mask = cv2.absdiff(ref_combined_mask, current_combined_mask)
        
        # Xử lý nhiễu
        kernel = np.ones((3,3), np.uint8)
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_OPEN, kernel)
        diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_CLOSE, kernel)
        
        # Vẽ vùng bị mất
        contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)

        # Tạo overlay cho vùng ban đầu
        overlay = frame.copy()

        # Tô màu vị trí ban đầu của vật thể 
        for contour in ref_contours:
            cv2.fillPoly(overlay, [contour], (0,255,0))

        # Vẽ viền đỏ cho vùng hiện tại của vật thể bị di chuyển
        for contour in contours:
            if cv2.contourArea(contour) > 10:  
                cv2.drawContours(frame, [contour], -1, (0,0,255), 2)

            
        alpha = 0.3 
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        for obj in current_objects:
            x1, y1, x2, y2 = obj['box']
            label = f"{obj['name']} ({obj['conf']:.2f})"
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.imshow("Object Detection", frame)
        cv2.imshow("Difference Mask", diff_mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()