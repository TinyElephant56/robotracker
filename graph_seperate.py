import json
import cv2
import numpy as np
import math
file_id = 482

with open(f"{file_id}.json", 'r') as f:
    data = json.load(f)

trails = [np.zeros((271, 555, 3), dtype=np.uint8) for _ in range(6)]
darkness = np.zeros_like(trails[0])
size = 15
alpha = 1
beta = 1 - alpha

titlenames = ["Blue A", "Blue B", "Blue C", "Red A", "Red B", "Red C"]
lastpoints = [None]*6
hueshift = 1

def draw_robot_elements(robot, row, team):
    global trails
    #team is 0 or 1
    #robot is 0, 1, or 2
    x, y = row[team][robot][0]
    color = colors[team][robot]
    color = (int(color[0]), int(color[1]), int(color[2]))
    if lastpoints and lastpoints[team]:
        last_x, last_y = lastpoints[team][robot][0]
        if math.dist((x, y), (last_x, last_y)) < 150:
            cv2.line(trails[robot + team*3], (x, y), (last_x, last_y), color, 1, cv2.LINE_AA) #+math.floor(row[team][robot][1]/20)
            cv2.putText(finals[robot + team*3], str(robot), (x, y), 0, 0.5, color, 2)
            cv2.rectangle(finals[robot + team*3], (x - size, y - size), (x + size, y + size), color, 2)
    else:
        cv2.circle(trails[robot + team*3], (x, y), 5, color, -1)

for row in data:
    finals = [cv2.imread("darkfield2023 copy.png") for _ in range(6)]

    hueshift += 0.003
    colors = [[(255, 0, 0), (255, 0, 179), (255, 225, 0)], [(0, 0, 255), (0, 68, 255), (0, 149, 255)]]
    for i in range(len(colors)):
        for j in range(3):
            hsv_color = cv2.cvtColor(np.uint8([[colors[i][j]]]), cv2.COLOR_BGR2HSV)[0][0]
            hsv_color[0] = (hsv_color[0] + hueshift)%180
            if row[i]:
                hsv_color[1] = max(hsv_color[1] - row[i][j][1], 100)
                hsv_color[2] = max(hsv_color[1] - row[i][j][1], 100)
            colors[i][j] = tuple(cv2.cvtColor(np.uint8([[hsv_color]]), cv2.COLOR_HSV2BGR)[0][0])
    if row[0]:
        for robot in range(3):
            draw_robot_elements(robot, row, 0)
    else:
        cv2.putText(finals[0], "no blue found", (10, 10), 0, 0.5, (225, 255, 0), 1)

    if row[1]:
        for robot in range(3):
            draw_robot_elements(robot, row, 1)
    else:
        cv2.putText(finals[3], "no red found", (300, 10), 0, 0.5, (0, 0, 255), 1)
    
    lastpoints = row
    
    for i in range(6):
        trails[i] = cv2.addWeighted(trails[i], alpha, darkness, beta, 0)
        finals[i] = cv2.add(finals[i], trails[i])
        cv2.imshow(f'{titlenames[i]}', finals[i])


    key = cv2.waitKey(1)
    if key == 27:  # Exit on ESC key
        break

while True:
    # Display each robot's final image
    for i in range(6):
        cv2.imshow(f'{titlenames[i]}', finals[i])
    
    key = cv2.waitKey(1)
    if key == 27: #ord('q')
        break

cv2.destroyAllWindows()
