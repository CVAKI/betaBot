"""
Move Animator - Smooth piece movement animations
"""

import pygame
import time
import config


class MoveAnimator:
    """Handles smooth animation of piece movements"""

    def __init__(self):
        self.is_animating = False
        self.animation_start_time = None
        self.animation_duration = config.MOVE_ANIMATION_DURATION
        self.animating_piece = None
        self.start_pos = None
        self.end_pos = None
        self.current_pos = None

    def start_animation(self, piece, from_pos, to_pos):
        """Start animating a move"""
        self.is_animating = True
        self.animation_start_time = time.time()
        self.animating_piece = piece
        self.start_pos = from_pos
        self.end_pos = to_pos
        self.current_pos = list(from_pos)

    def update(self) -> bool:
        """
        Update animation state

        Returns:
            True if animation is complete
        """
        if not self.is_animating:
            return True

        elapsed = time.time() - self.animation_start_time
        progress = min(1.0, elapsed / self.animation_duration)

        # Easing function (ease-out)
        progress = self._ease_out(progress)

        # Calculate current position
        start_x, start_y = self.start_pos
        end_x, end_y = self.end_pos

        self.current_pos[0] = start_x + (end_x - start_x) * progress
        self.current_pos[1] = start_y + (end_y - start_y) * progress

        # Check if complete
        if progress >= 1.0:
            self.is_animating = False
            return True

        return False

    def _ease_out(self, t):
        """Ease-out cubic easing"""
        return 1 - pow(1 - t, 3)

    def get_current_position(self):
        """Get current animated position"""
        if self.is_animating:
            return tuple(self.current_pos)
        return self.end_pos

    def animate_capture(self, piece):
        """Animate a piece being captured (fade out)"""
        # Simple implementation - could be enhanced
        pass

    def is_animating_move(self) -> bool:
        """Check if currently animating"""
        return self.is_animating