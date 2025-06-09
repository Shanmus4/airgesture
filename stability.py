import time
import numpy as np

class Stabilizer:
    def __init__(self):
        self.prev_pos = None
        self.prev_time = time.time()
        self.velocity = np.array([0.0, 0.0])
        self.alpha = 0.6  # Smoothing factor
        self.speed_boost = 2.0  # Scale faster movements
        self.min_movement_threshold = 2  # Ignore jitter under this px

    def apply(self, x, y):
        current_pos = np.array([x, y], dtype=np.float32)
        now = time.time()
        dt = now - self.prev_time

        if self.prev_pos is None:
            self.prev_pos = current_pos
            self.prev_time = now
            return int(x), int(y)

        # Calculate velocity
        raw_velocity = (current_pos - self.prev_pos) / max(dt, 1e-6)

        # Ignore tiny movements (jitter)
        if np.linalg.norm(current_pos - self.prev_pos) < self.min_movement_threshold:
            return tuple(self.prev_pos.astype(int))

        # Weighted average for smooth velocity
        self.velocity = self.alpha * self.velocity + (1 - self.alpha) * raw_velocity

        # Predict next position based on velocity (dynamic speed like touchpad)
        smoothed_pos = self.prev_pos + self.velocity * dt * self.speed_boost

        self.prev_pos = smoothed_pos
        self.prev_time = now

        return tuple(smoothed_pos.astype(int))
