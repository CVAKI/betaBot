"""
Timer Utilities
"""

import time


class Timer:
    """Simple timer for tracking elapsed time"""

    def __init__(self):
        self.start_time = None
        self.elapsed = 0.0
        self.is_running = False

    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.is_running = True

    def stop(self) -> float:
        """Stop the timer and return elapsed time"""
        if self.is_running:
            self.elapsed = time.time() - self.start_time
            self.is_running = False
        return self.elapsed

    def get_elapsed(self) -> float:
        """Get elapsed time (without stopping)"""
        if self.is_running:
            return time.time() - self.start_time
        return self.elapsed

    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.elapsed = 0.0
        self.is_running = False


def wait(milliseconds: int):
    """Wait for specified milliseconds"""
    time.sleep(milliseconds / 1000.0)


def get_fps(frame_times: list, window_size: int = 60) -> float:
    """Calculate FPS from frame time history"""
    if len(frame_times) < 2:
        return 0.0

    recent_times = frame_times[-window_size:]
    time_diff = recent_times[-1] - recent_times[0]

    if time_diff == 0:
        return 0.0

    return len(recent_times) / time_diff