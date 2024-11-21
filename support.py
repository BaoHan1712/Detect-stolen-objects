from ultralytics import YOLO

model = YOLO('yolo11n-seg.pt')
model.export(format='onnx', simplify=True, opset=12, imgsz=480)
# model.predict(source=0, show=True, imgsz=320)

