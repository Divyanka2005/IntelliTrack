# Problem Statement

Manual video surveillance is time-consuming and error-prone. Security personnel and analysts
often need to review long video feeds to identify moving objects, count occurrences, and
understand movement patterns — a slow, manual process prone to human error.

## Scope
IntelliTrack automates this by:
- Detecting motion in video streams using background subtraction
- Tracking each detected object across frames using centroid-based tracking
- Generating real-time analytics: unique object counts, movement direction, and size classification

## Target Users
- Security/surveillance operators monitoring CCTV footage
- Retail analysts studying footfall patterns
- Traffic monitoring personnel

## High-Level Features
- Upload any video and get real-time motion detection
- Persistent object IDs across frames (not re-detected as "new" every frame)
- Live dashboard with total count, currently tracked objects, direction, and size