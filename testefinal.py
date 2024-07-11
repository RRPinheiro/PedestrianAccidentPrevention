from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

# Load the YOLOv8 model
model = YOLO("./yolov8n.pt").cuda()
tracker = sv.ByteTrack()
window_width = 1280
window_height = 736
frame_counter = 0
skip_frames = 3
colisao = False
previous_box_sizes = defaultdict(list)  # Initialize to 0 for all new IDs

# Initialize annotators
box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Create the window
cv2.namedWindow("YOLOv8 Tracking", cv2.WINDOW_AUTOSIZE)

# Resize the window
cv2.resizeWindow("YOLOv8 Tracking", window_width, window_height)

# Open the video file
video_path = r""
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    
    if not success:
        break
    
    frame_counter += 1
    if frame_counter % skip_frames == 0:
        
        # Resize the frame to the original resolution (1280x736)
        frame = cv2.resize(frame, (1280, 736))
        
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.predict(frame, imgsz=(1280, 736), verbose=False, conf=0.6, classes=0)
        
        detections = sv.Detections.from_ultralytics(results[0])
        detections = tracker.update_with_detections(detections)
        
        total_area = frame.shape[0] * frame.shape[1]
        
        # Define the ROI as a percentage of the frame size
        roi_top = int(frame.shape[0] * 0.5)
        roi_bottom = int(frame.shape[0] * 1)
        roi_left = int(frame.shape[1] * 0.2)
        roi_right = int(frame.shape[1] * 0.8)
        
        # Calculate the area of the ROI
        roi_area = (roi_bottom - roi_top) * (roi_right - roi_left)
        area_threshold = 0.02 * roi_area

        caution_roi_left_top = int(frame.shape[0] * 0.5)
        caution_roi_left_bottom = int(frame.shape[0] * 1)
        caution_roi_left_left = int(frame.shape[1] * 0)
        caution_roi_left_right = int(frame.shape[1] * 0.2)

        caution_roi_right_top = int(frame.shape[0] * 0.5)
        caution_roi_right_bottom = int(frame.shape[0] * 1)
        caution_roi_right_left = int(frame.shape[1] * 0.8)
        caution_roi_right_right = int(frame.shape[1] * 1)

        caution_roi_left_area = (caution_roi_left_bottom - caution_roi_left_top) * (caution_roi_left_right - caution_roi_left_left)
        caution_roi_right_area = (caution_roi_right_bottom - caution_roi_right_top) * (caution_roi_right_right - caution_roi_right_left)

        caution_area_threshold_left = 0.02 * caution_roi_left_area
        caution_area_threshold_right = 0.02 * caution_roi_right_area
        
        grow_roi_top = int(frame.shape[0] * 0.5)
        grow_roi_bottom = int(frame.shape[0] * 1)
        
        # Check if results is not None and contains valid boxes
        if results is not None and len(results) > 0 and results[0].boxes is not None:
            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu().numpy()
            # Assuming 'detections' is the result from tracker.update_with_detections()
            ids = detections.tracker_id if detections.tracker_id is not None else [None] * len(detections.boxes)
            
            annotated_frame = box_annotator.annotate(frame.copy(), detections=detections)
            labels = [
                f"#{tracker_id}"
                for tracker_id
                in detections.tracker_id
            ]
            annotated_frame = label_annotator.annotate(annotated_frame, detections=detections, labels=labels)
            active_ids = set(ids)  # Track currently active IDs

            for box, tracker_id in zip(boxes, ids):
                x, y, w, h = box
                box_area = w * h
                previous_box_sizes[tracker_id].append(box_area)
                if tracker_id is not None:
                    # Calculate the percentage growth
                    if len(previous_box_sizes[tracker_id]) > 2:
                        growth_percentages = []
                        for i in range(len(previous_box_sizes[tracker_id]) - 1, 1, -1):
                            current_box_size = previous_box_sizes[tracker_id][i]
                            last_box_size = previous_box_sizes[tracker_id][i - 1]
                            growth_percentage = ((current_box_size - last_box_size) / last_box_size) * 100
                            growth_percentages.append(growth_percentage)
                        average_growth_percentage = sum(growth_percentages) / len(growth_percentages)

                        if grow_roi_top <= y <= grow_roi_bottom:
                            if average_growth_percentage > 7:  # Check if the growth percentage is more than 15%
                                cv2.putText(annotated_frame, "Atencao", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                                
                                
                    # Check if the box is inside the ROI
                    if roi_left <= x <= roi_right and roi_top <= y <= roi_bottom:
                        # If the box area exceeds the threshold, do something
                        if box_area > area_threshold:
                            cv2.putText(annotated_frame, "Risco de Colisao", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            colisao = True
                    
                    if caution_roi_left_left <= x <= caution_roi_left_right and caution_roi_left_top <= y <= caution_roi_left_bottom and not colisao:
                        if box_area > caution_area_threshold_left:
                            cv2.putText(annotated_frame, "Atencao", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    if caution_roi_right_left <= x <= caution_roi_right_right and caution_roi_right_top <= y <= caution_roi_right_bottom and not colisao:
                        if box_area > caution_area_threshold_right:
                            cv2.putText(annotated_frame, "Atencao", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    
                    colisao = False
            
            # Remove IDs that are no longer active
            for tracker_id in list(previous_box_sizes.keys()):
                if tracker_id not in active_ids:
                    del previous_box_sizes[tracker_id]
            
            cv2.rectangle(annotated_frame, (caution_roi_left_left, caution_roi_left_top), (caution_roi_left_right, caution_roi_left_bottom), (255, 255, 255), 3)
            cv2.rectangle(annotated_frame, (caution_roi_right_left, caution_roi_right_top), (caution_roi_right_right, caution_roi_right_bottom), (255, 255, 255), 3)
            cv2.rectangle(annotated_frame, (roi_left, roi_top), (roi_right, roi_bottom), (0, 255, 255), 3)
            cv2.imshow("YOLOv8 Tracking", annotated_frame)
            
        if cv2.waitKey(1) & 0xFF == ord(" "):
            while True:
                if cv2.waitKey(1) & 0xFF == ord(" "):
                    break
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
    else:
        continue

cap.release()
cv2.destroyAllWindows()
