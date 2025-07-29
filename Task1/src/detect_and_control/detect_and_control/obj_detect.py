import cv2

video_path = "bottles_moving1.mp4"
cap = cv2.VideoCapture(video_path)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Video width (w): {w}, height (h): {h}")
cap.release()