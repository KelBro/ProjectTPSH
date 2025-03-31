from ultralytics import YOLO
model = YOLO('./help/best.pt')
path = './4.jpg'
while True:
    a = model(path)
    asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])

    print(True if 'clothing' in str(asw) else False)
    path = input('path:   ')
