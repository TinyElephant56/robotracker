import cv2
from ultralytics import YOLO
import numpy as np
import math
import torch
import json
import csv 


file_id = 482

print("imports...")
cap = cv2.VideoCapture(f"dontcommit/{file_id}/cropped.mp4")
ret, frame = cap.read()

model = YOLO("best.pt")
confidence_threshold = 0.7

bluebots = []
redbots = []

with open(f'dontcommit/{file_id}/corners.json', 'r') as f:
    corners_data = json.load(f)

src_points = np.array([corners_data[0], corners_data[1], corners_data[2], corners_data[3]], dtype="float32")
dst_points = np.array([(0, 0), (555, 0), (555, 271), (0, 271)], dtype="float32")
matrix = cv2.getPerspectiveTransform(src_points, dst_points)

with open(f"dontcommit/{file_id}/bluecords.csv", 'w') as f:
    f.truncate
with open(f"dontcommit/{file_id}/redcords.csv", 'w') as f:
    f.truncate

trail = np.zeros((271, 555, 3), dtype=np.uint8)
darkness = np.zeros_like(trail)
alpha = 0.98
beta = 1 - alpha
lastpoints = None

colors = [[(255, 0, 0), (255, 0, 179), (255, 225, 0)], [(0, 0, 255), (0, 68, 255), (0, 149, 255)]]

def track_robots(robots, cords, color, name):

    if robots and cords:
        incomplete = True
        assignments = 0
        while incomplete:
            closest = 999999
            bestc = None
            bestb = None
            for b in range(len(robots)): #go through all the robots...
                if robots[b][1] != 0: #...robots that havent already been used
                    for c in range(len(cords)): #for each coordinate...
                        distance = math.dist(robots[b][0], cords[c]) #find its distance to the robot
                        spread = True
                        for x in range(len(robots)):
                            if robots[x][1] == 0:
                                if math.dist(robots[x][0], cords[c]) < 15:
                                    spread = False
                                    #print("avoided")             
                        if distance < closest and distance < 200 and spread: #check if it is the closest possible distance
                            bestb = b
                            bestc = c
                            closest = distance
            if bestc is not None:
                robots[bestb] = [cords[bestc], 0]
                cords.pop(bestc)
            assignments += 1
            if assignments == 3 or len(cords) == 0:
                incomplete = False
    if len(robots) < 3 and cords:
        print('yyee')
        for c in cords:
            robots.append([c, 1])
            print(f"created robot at {c}")
            snippet = frame[c[1]-25:c[1]+25, c[0]-25:c[0]+25]
            cv2.imwrite(f"dontcommit/{file_id}/{name}_{len(robots)}.jpg", snippet)


    for i in range(len(robots)):
        robots[i][1] += 1
        cv2.circle(frame, robots[i][0], 5, color, 2)
        cv2.putText(frame, f"{i}", robots[i][0], 0, 0.5, (255, 255, 0), 2)

def dewarp_robots(bluebots, redbots):
    blue_data = []
    red_data = []
    for team_bots, color, bot_data in [(bluebots, (255, 0, 0), blue_data), (redbots, (0, 0, 255), red_data)]:
        for robot in range(len(team_bots)):
            x, y = team_bots[robot][0]
            point = np.array([[[x, y]]], dtype="float32")
            transformed_point = cv2.perspectiveTransform(point, matrix)
            transformed_x, transformed_y = transformed_point[0][0]
            bot_data.append([[int(transformed_x), int(transformed_y)], team_bots[robot][1]])
            cv2.circle(final, (int(transformed_x), int(transformed_y)), 5, color, 2)


    flattened_data = [item for sublist in bluebots for pair in sublist if isinstance(pair, tuple) for item in pair]
    #chatgpt wrote this line lmao
    with open(f'dontcommit/{file_id}/bluecords.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(flattened_data)
    
    flattened_data = [item for sublist in redbots for pair in sublist if isinstance(pair, tuple) for item in pair]
    with open(f'dontcommit/{file_id}/redcords.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(flattened_data)


def draw_robot_elements(robot_idx, row_data, team_idx):
    global trail
    x, y = row_data[team_idx][robot_idx][0]
    color = colors[team_idx][robot_idx]
    if lastpoints and lastpoints[team_idx]:
        last_x, last_y = lastpoints[team_idx][robot_idx][0]
        if math.dist((x, y), (last_x, last_y)) < 150:
            cv2.line(trail, (x, y), (last_x, last_y), color, 2)
            cv2.putText(final, str(robot_idx), (x, y), 0, 0.5, color, 1)
            cv2.rectangle(final, (x - 15, y - 15), (x + 15, y + 15), color, 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for pt in src_points:
        cv2.circle(frame, (int(pt[0]), int(pt[1])), 5, (0, 0, 0), -1)

    final = cv2.imread("darkfield2023flipped.png")
    results = model(frame, device="mps", verbose=False, iou=0.8)
    result = results[0]
    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    confidences = np.array(result.boxes.conf.cpu())
    classes = np.array(result.boxes.cls.cpu(), dtype="int")
    bluecords, redcords = [], []

    for cls, bbox, conf in zip(classes, bboxes, confidences):
        (x1, y1, x2, y2) = bbox
        cord = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        if conf > confidence_threshold:
            cv2.putText(frame, f"{conf*100:.0f}", (x1, y1 - 5), 0, 0.5, (255, 255, 255), 2)
            if cls == 0:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (225, 0, 0), 2)
                bluecords.append(cord)
            elif cls == 1:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 225), 2)
                redcords.append(cord)

    track_robots(bluebots, bluecords, (255, 0, 0), "blue")
    track_robots(redbots, redcords, (0, 0, 225), "red")
    dewarp_robots(bluebots, redbots)

    # Process JSON data for top-down view
    # with open(f"{file_id}.json", 'r') as f:
    #     data = json.load(f)
    # if data:
    #     row = data[-1]
    #     for team_idx, team_data in enumerate(row):
    #         if team_data:
    #             for robot in range(3):
    #                 draw_robot_elements(robot, row, team_idx)

    # lastpoints = row
    # trail = cv2.addWeighted(trail, alpha, darkness, beta, 0)
    # final = cv2.add(final, trail)

    cv2.imshow("does anyone ever read these greyed out headers", frame)
    cv2.imshow("sussy baka ohio skibidi sigma", final)

    if cv2.waitKey(1) == 27:
        break

print("done!")
cap.release()
cv2.destroyAllWindows()
