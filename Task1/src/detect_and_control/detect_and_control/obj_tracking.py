import cv2
from ultralytics import solutions
import json
import os
from datetime import datetime, timezone
import uuid # For generating unique item_ids if needed, though we'll use a simple counter here

# === Configuration ===
video_path = "bottles_moving2.mp4"
output_json_path = "tracked_bottles_data.json"
frames_output_dir = "frames"
# Create directory for cropped frames
os.makedirs(frames_output_dir, exist_ok=True)

# Placeholder for defect detection - assume all are good for now
# You will integrate the defect detection model here later
def is_bottle_defective(cropped_image, track_id):
    # TODO: Implement actual defect detection logic here
    # For now, always return False
    return False

# === Video source ===
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Failed to open video.")
    exit()

# Read a frame to get dimensions if needed for dynamic region setting
ret, frame = cap.read()
if not ret:
    print("❌ Failed to read video.")
    exit()
h, w = frame.shape[:2]

# Re-initialize capture to start from the beginning
cap.release()
cap = cv2.VideoCapture(video_path)

# === Initialize ObjectCounter (Handles Detection, Tracking, and Counting) ===
counter = solutions.ObjectCounter(
    model="yolov8x.pt",           # 1. Object Detection Model
    region=[(1000, 0), (1000, h)], # Counting line (Ensure this line is appropriate for your video)
    classes=[39],                 # Filter for 'bottle' (COCO ID 39)
    conf=0.7,                     # Detection confidence
    iou=0.6,                      # NMS IoU threshold
    tracker="botsort.yaml",       # 2. Tracking algorithm (internally applied)
    show=True,                    # Show live output (visualizes detection & tracking)
    line_width=2,
    show_labels=True,
    show_conf=True,
    show_in=True,          # 3. Show counting results
    show_out=True,
    verbose=False
)

# === Data Collection ===
tracked_items_data = []
frame_id_counter = 0
# Use a simple counter for item_id for now, replace with UUID or other logic if needed
item_counter = 0

# === Process Video Frames ===
while True:
    ret, frame = cap.read()
    if not ret:
        print("⏹️ Video ended.")
        break

    # This single call performs:
    # - Detection (using yolov8x.pt)
    # - Tracking (using botsort.yaml)
    # - Counting (based on crossing the region line)
    # - Visualization (if show=True)
    results = counter(frame) # results is a SolutionResults object

    # --- Extract Detailed Tracking Data ---
    # The 'results' object from SolutionResults likely wraps the original YOLO Results
    # Access the original results if needed (might be results.result or similar depending on exact implementation)
    # Let's assume results has an attribute .result or similar that gives the YOLO Results object
    # Or it might directly have boxes, ids etc. Check the actual attributes.
    # Based on typical usage, let's try accessing the underlying result if needed.
    # However, the SolutionResults might already provide necessary info or the original results.
    # Let's assume it wraps the original results in .result attribute.

    # Check if results has a .result attribute (original YOLO Results)
    # This is a common pattern but might vary slightly
    original_results = getattr(results, 'result', None)
    if original_results is None:
        # If not, try accessing directly (less likely but possible structure)
        # Or access the model's results directly if SolutionResults doesn't wrap it cleanly
        # For now, let's assume the SolutionResults object behaves like the original Results
        # when iterating or accessing boxes/ids. Let's try that.
        # The documentation example shows using results.plot() etc.
        # Let's assume 'results' itself is the YOLO Results object for data access.
        # This is the most likely scenario based on how solutions are usually structured.
        original_results = results # Assume results object itself has boxes, ids etc.

    # Now access boxes, ids from original_results
    # Ensure tracking IDs exist
    if hasattr(original_results, 'boxes') and original_results.boxes is not None and \
       hasattr(original_results.boxes, 'id') and original_results.boxes.id is not None:

        # Get boxes, track IDs, classes, confidences
        boxes = original_results.boxes.xywh.cpu().numpy() # xywh format
        track_ids = original_results.boxes.id.int().cpu().tolist()
        classes = original_results.boxes.cls.int().cpu().tolist()
        confidences = original_results.boxes.conf.cpu().numpy()

        # Iterate through each detected/tracked object
        for i, (box, track_id, cls, conf) in enumerate(zip(boxes, track_ids, classes, confidences)):
            # Filter for bottles only (just in case classes filter isn't 100% strict in all contexts)
            if cls == 39: # COCO class ID for 'bottle'
                x, y, w_box, h_box = box # xywh format

                # --- Crop Image ---
                # Convert xywh to x1, y1, x2, y2 for cropping
                x1, y1, x2, y2 = int(x - w_box/2), int(y - h_box/2), int(x + w_box/2), int(y + h_box/2)
                # Ensure crop coordinates are within frame bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                cropped_img = frame[y1:y2, x1:x2]

                # --- Defect Detection (Placeholder) ---
                # is_defective = is_bottle_defective(cropped_img, track_id)
                # qc_status = "fail" if is_defective else "pass"

                qc_status = "pass"
                is_defective = "no"

                # --- Save Image ---
                image_filename = f"track_{int(track_id)}.jpg"
                image_path_full = os.path.join(frames_output_dir, image_filename)
                # Only save if the image crop is valid and file doesn't exist already
                # (or overwrite if preferred, but let's avoid duplicates for now)
                if cropped_img.size > 0 and not os.path.exists(image_path_full):
                   success = cv2.imwrite(image_path_full, cropped_img)
                   if not success:
                       print(f"Warning: Failed to save image {image_path_full}")
                       image_path_full = None # Indicate failure
                elif cropped_img.size == 0:
                    print(f"Warning: Empty crop for track_id {track_id}, frame {frame_id_counter}")
                    image_path_full = None
                # else: file exists, don't overwrite, use existing path

                # --- Generate Data ---
                # Use a simple counter for item_id for now
                item_counter += 1
                # Format spawn_time for current item (assuming generation time is spawn time)
                # You might want to use video timestamp if available
                spawn_time_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                item_data = {
                    "item_id": f"SYN_{item_counter:05d}", # Simple synthetic ID
                    "spawn_time": spawn_time_iso,
                    "frame_id": frame_id_counter,
                    "tracking_id": int(track_id),
                    "class": "Bottle", # Assuming class 39 is always 'Bottle'
                    "is_defective": is_defective,
                    "qc_status": qc_status,
                    "bounding_box": [int(x), int(y), int(w_box), int(h_box)], # xywh format
                    # "pose": { "position": [], "orientation": [] }, # Placeholder for 3D pose
                    "image_path": image_path_full if image_path_full and os.path.exists(image_path_full) else ""
                }

                tracked_items_data.append(item_data)
                print(f"Tracked Item: {item_data}") # Optional: Print for debugging

    else:
        print(f"Frame {frame_id_counter}: No valid tracking data found.")

    frame_id_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Final Results (Counting) ===
print(f"\n✅ Final Count Summary:")
print(f"   Inward Count: {counter.in_count}")
print(f"   Outward Count: {counter.out_count}")
# Note: counter.total_tracks might not exist, check SolutionResults attributes
# total_tracks might be accessible via results.total_tracks if returned by counter(frame)
# Or calculate from unique track_ids in tracked_items_data
unique_track_ids = set(item['tracking_id'] for item in tracked_items_data)
print(f"   Unique Tracks Processed (from data): {len(unique_track_ids)}")

# === Save Data to JSON ===
try:
    with open(output_json_path, 'w') as f:
        json.dump(tracked_items_data, f, indent=4)
    print(f"\n✅ Saved tracked item data to {output_json_path}")
except Exception as e:
    print(f"\n❌ Error saving JSON data: {e}")

# === Cleanup ===
cap.release()
cv2.destroyAllWindows()
