import yt_dlp
import cv2
import ffmpeg
import os
import math
import json
import random

file_id = random.randint(0, 999)


def download_youtube_video(youtube_url, output_path="video.mp4"):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        print(f"Downloaded video to {output_path}")

def get_frame_at_time(video_path, time_seconds):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, time_seconds * 1000)  # Set to 5 seconds in milliseconds
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Failed to capture frame.")
        return None
    
    return frame

def select_crop_rectangle(frame, aspect_ratio=(3, 1)):
    def draw_rectangle(event, x, y, flags, param):
        nonlocal start_point, cropping, crop_rect

        if event == cv2.EVENT_LBUTTONDOWN:
            start_point = (x, y)
            cropping = True
            crop_rect = None
        elif event == cv2.EVENT_MOUSEMOVE and cropping:
            width = x - start_point[0]
            height = int(width / aspect_ratio[0] * aspect_ratio[1])
            end_point = (start_point[0] + width, start_point[1] + height)
            crop_rect = (start_point, end_point)
        elif event == cv2.EVENT_LBUTTONUP:
            cropping = False
    
    start_point, cropping, crop_rect = (0, 0), False, None
    cv2.namedWindow("Select Crop")
    cv2.setMouseCallback("Select Crop", draw_rectangle)

    while True:
        temp_frame = frame.copy()
        if crop_rect:
            cv2.rectangle(temp_frame, crop_rect[0], crop_rect[1], (0, 255, 0), 2)
        cv2.imshow("Select Crop", temp_frame)

        key = cv2.waitKey(1)
        if key == ord("c"):  # Press 'c' to confirm the selection
            break
        elif key == ord("q"):  # Press 'q' to quit
            cv2.destroyAllWindows()
            return None

    cv2.destroyAllWindows()
    return crop_rect


def crop_trim_and_scale_video(video_path, crop_rect, output_path="cropped_video.mp4", start_time=5, end_time=165):
    start_x, start_y = crop_rect[0]
    end_x, end_y = crop_rect[1]
    
    # Calculate width and height and ensure they are even numbers
    width = end_x - start_x
    height = end_y - start_y
    if width % 2 != 0:  # Ensure width is even
        width -= 1
    if height % 2 != 0:  # Ensure height is even
        height -= 1

    # Crop, trim, and scale with the 'scale' filter rounding to an even number
    ffmpeg.input(video_path, ss=start_time, t=end_time - start_time) \
        .crop(start_x, start_y, width, height) \
        .filter('scale', 'iw/3', 'ih') \
        .filter('setdar', 1) \
        .output(output_path) \
        .run()
    
    print(f"Cropped, trimmed, and scaled video saved to {output_path}")

def capture_corners(video_path, output_file=f"{file_id}_corners.json"):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Failed to capture the first frame.")
        return

    corners = []
    
    def select_corners(event, x, y, flags, param):
        nonlocal corners
        if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
            corners.append((x, y))
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Select Corners", frame)
    
    cv2.namedWindow("Select Corners")
    cv2.setMouseCallback("Select Corners", select_corners)

    # Display the frame and capture up to four corner points
    while True:
        cv2.imshow("Select Corners", frame)
        key = cv2.waitKey(1)
        if key == ord("c") and len(corners) == 4:  # Confirm selection by pressing 'c' after 4 points
            break
        elif key == ord("q"):  # Quit without saving by pressing 'q'
            print("Corner selection was cancelled.")
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    # Save corners to a JSON file
    with open(output_file, "w") as f:
        json.dump(corners, f)
    print(f"Saved corner points to {output_file}")

# Main program
youtube_url = "https://www.youtube.com/watch?v=ehDxvhwvqEw"
downloaded_video_path = f"{file_id}_downloaded.mp4"
cropped_video_path = f"{file_id}_cropped.mp4"

download_youtube_video(youtube_url, downloaded_video_path)

# Capture the frame at the 5-second mark
frame = get_frame_at_time(downloaded_video_path, time_seconds=5)
print(file_id)

if frame is not None:
    crop_rect = select_crop_rectangle(frame)
    
    if crop_rect:
        # Trim from 5 seconds to 2 minutes and 45 seconds, crop, and scale
        crop_trim_and_scale_video(downloaded_video_path, crop_rect, cropped_video_path, start_time=5, end_time=165)
        capture_corners(cropped_video_path)

        
    else:
        print("Cropping was cancelled.")
else:
    print("Could not retrieve the frame at 5 seconds.")