import streamlit as st
import cv2
import tempfile
import pandas as pd

from src.detector import MotionDetector
from src.tracker import CentroidTracker
from src.analytics import Analytics

st.set_page_config(page_title="IntelliTrack", layout="wide")
st.title("IntelliTrack — Motion Detection, Tracking & Analytics")

st.markdown(
    "Upload a video to detect moving objects, track them across frames, "
    "and view live analytics (count, direction, size)."
)

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Save uploaded file to a temp location so OpenCV can read it
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture(tfile.name)

    detector = MotionDetector()
    tracker = CentroidTracker()
    analytics = Analytics()

    col1, col2 = st.columns([3, 1])
    frame_display = col1.empty()
    stats_display = col2.empty()

    start_button = st.button("Start Processing")

    if start_button:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            boxes = detector.detect(frame)
            tracked = tracker.update(boxes)
            data = analytics.update(tracked)

            # Draw boxes + IDs + direction on frame
            for object_id, info in data["objects"].items():
                x, y, w, h = info["box"]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"ID {object_id} | {info['size']} | {info['direction']}"
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_display.image(frame_rgb, channels="RGB", use_container_width=True)

            with stats_display.container():
                st.metric("Total Unique Objects", data["total_unique_count"])
                st.metric("Currently Tracked", data["currently_tracked"])

                if data["objects"]:
                    table_rows = [
                        {"ID": oid, "Size": info["size"], "Direction": info["direction"]}
                        for oid, info in data["objects"].items()
                    ]
                    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        cap.release()
        st.success("Processing complete.")
else:
    st.info("Please upload a video to begin.")