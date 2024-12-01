import cv2
from ultralytics import YOLO
import numpy as np
import math
import json
import time
import multiprocessing as mp

file_id = 482

print("imports...")
cap = cv2.VideoCapture(f"{file_id}_cropped.mp4")
ret, frame = cap.read()

model = YOLO("best.pt")
confidence_threshold = 0.4

# fps = round(cap.get(cv2.CAP_PROP_FPS))
# total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
# print(f"we be going through this many frames: {total_frames}")
# print(f"the fps is {fps}")
# print(f"video clip in seconds: {total_frames/fps}")


def run_through_frames(start, end, device):
    starttime = time.time()
    print("initialized!")
    cap = cv2.VideoCapture(f"{file_id}_cropped.mp4")
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    currentframe = start
    while currentframe < end:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, device=device, verbose=False, iou=0.8)
        result = results[0]
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        confidences = np.array(result.boxes.conf.cpu())
        classes = np.array(result.boxes.cls.cpu(), dtype="int")
        
        bluedetections, reddetections = [], []

        for cls, bbox, conf in zip(classes, bboxes, confidences):
            (x1, y1, x2, y2) = bbox
            cord = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            if conf > confidence_threshold:
                if cls == 0:
                    bluedetections.append(cord)
                elif cls == 1:
                    reddetections.append(cord)
        if currentframe%100 == 0:
            print(currentframe)
        currentframe+=1
    endtime = time.time()
    print(f"A thread was done that took:{endtime-starttime}")

if __name__ == "__main__":
    starttime = time.time()
    print('running...')
    processes = [
        mp.Process(target=run_through_frames, args = (0, 500, "mps") ),
        mp.Process(target=run_through_frames, args = (500, 1000, "mps")),
        mp.Process(target=run_through_frames, args = (1000, 1500, "mps")),
        mp.Process(target=run_through_frames, args = (1500, 2000, "mps")),
        
        # mp.Process(target=run_through_frames, args = (2000, 2500, "mps")),
        # mp.Process(target=run_through_frames, args = (2500, 3000, "mps")),
        # mp.Process(target=run_through_frames, args = (3000, 3500, "mps")),
        # mp.Process(target=run_through_frames, args = (3500, 4000, "mps")),
    ]
    # t3 = threading.Thread(target=run_through_frames, args = (1500, 2000, "auto"))
    for p in processes:
        p.start()
    # t3.start()
    for p in processes:
        p.join()
    # t3.join()
    # run_through_frames()
    print("total times:")
    endtime = time.time()
    print(f"Elapsed time:{endtime-starttime}")
cap.release()
cv2.destroyAllWindows()
