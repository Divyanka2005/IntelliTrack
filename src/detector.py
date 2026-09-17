import cv2
from src.preprocessing import preprocess_frame, clean_mask


class MotionDetector:
    """
    Detects moving objects in a video stream using background subtraction (MOG2).
    """

    def __init__(self, history=500, var_threshold=40, detect_shadows=True, min_area=800):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=detect_shadows
        )
        self.min_area = min_area

    def detect(self, frame):
        processed = preprocess_frame(frame)
        fg_mask = self.bg_subtractor.apply(processed)
        _, thresh_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        clean = clean_mask(thresh_mask)
        contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            if cv2.contourArea(cnt) < self.min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append((x, y, w, h))

        return boxes


