import math


class CentroidTracker:
    """
    Assigns and maintains unique IDs for objects across video frames
    by tracking the centroid (center point) of each bounding box.
    """

    def __init__(self, max_disappeared=30, max_distance=50):
        self.next_object_id = 0
        self.objects = {}          # object_id -> centroid (x, y)
        self.disappeared = {}      # object_id -> frames since last seen
        self.max_disappeared = max_disappeared  # remove ID after this many missed frames
        self.max_distance = max_distance        # max pixel distance to match same object

    def _register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def _deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, boxes):
        """
        boxes: list of (x, y, w, h) from MotionDetector.detect()
        Returns: dict {object_id: (x, y, w, h)} for currently tracked objects
        """
        # No detections this frame -> mark all existing objects as disappeared
        if len(boxes) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            return {}

        # Compute centroids for current detections
        input_centroids = []
        for (x, y, w, h) in boxes:
            cx = x + w // 2
            cy = y + h // 2
            input_centroids.append((cx, cy))

        # No existing tracked objects -> register all as new
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self._register(centroid)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Build distance matrix: existing objects vs new detections
            distances = []
            for oc in object_centroids:
                row = []
                for ic in input_centroids:
                    dist = math.hypot(oc[0] - ic[0], oc[1] - ic[1])
                    row.append(dist)
                distances.append(row)

            used_rows = set()
            used_cols = set()

            # Match closest pairs first (greedy matching)
            pairs = []
            for r in range(len(distances)):
                for c in range(len(distances[r])):
                    pairs.append((distances[r][c], r, c))
            pairs.sort(key=lambda p: p[0])

            for dist, r, c in pairs:
                if r in used_rows or c in used_cols:
                    continue
                if dist > self.max_distance:
                    continue
                object_id = object_ids[r]
                self.objects[object_id] = input_centroids[c]
                self.disappeared[object_id] = 0
                used_rows.add(r)
                used_cols.add(c)

            # Unmatched existing objects -> mark disappeared
            unused_rows = set(range(len(object_centroids))) - used_rows
            for r in unused_rows:
                object_id = object_ids[r]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)

            # Unmatched detections -> register as new objects
            unused_cols = set(range(len(input_centroids))) - used_cols
            for c in unused_cols:
                self._register(input_centroids[c])

        # Build result mapping id -> bounding box (match centroid back to original box)
        result = {}
        for object_id, centroid in self.objects.items():
            closest_box = min(
                boxes,
                key=lambda b: math.hypot((b[0] + b[2] // 2) - centroid[0], (b[1] + b[3] // 2) - centroid[1])
            )
            result[object_id] = closest_box

        return result