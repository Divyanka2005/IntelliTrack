class Analytics:
    """
    Generates simple analytics from tracked objects:
    total unique object count, movement direction, and size classification.
    """

    def __init__(self, direction_threshold=15):
        self.seen_ids = set()
        self.total_count = 0
        self.last_positions = {}  # object_id -> last centroid (x, y)
        self.direction_threshold = direction_threshold  # min pixel movement to count as a direction

    def classify_size(self, box):
        """Rough size classification based on bounding box area."""
        _, _, w, h = box
        area = w * h
        if area < 3000:
            return "Small"
        elif area < 15000:
            return "Medium"
        else:
            return "Large"

    def get_direction(self, object_id, box):
        """Determines movement direction by comparing current and last centroid."""
        x, y, w, h = box
        cx, cy = x + w // 2, y + h // 2

        direction = "—"
        if object_id in self.last_positions:
            prev_cx, prev_cy = self.last_positions[object_id]
            dx = cx - prev_cx
            if abs(dx) > self.direction_threshold:
                direction = "Right" if dx > 0 else "Left"

        self.last_positions[object_id] = (cx, cy)
        return direction

    def update(self, tracked_objects):
        """
        tracked_objects: dict {object_id: (x, y, w, h)} from CentroidTracker.update()
        Returns: dict with analytics info for display
        """
        frame_data = {}

        for object_id, box in tracked_objects.items():
            if object_id not in self.seen_ids:
                self.seen_ids.add(object_id)
                self.total_count += 1

            frame_data[object_id] = {
                "box": box,
                "size": self.classify_size(box),
                "direction": self.get_direction(object_id, box)
            }

        return {
            "objects": frame_data,
            "total_unique_count": self.total_count,
            "currently_tracked": len(tracked_objects)
        }