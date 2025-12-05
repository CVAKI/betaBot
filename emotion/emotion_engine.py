class EmotionEngine:
    def determine_emotion(self, piece, game_state, board):
        # Analyze threats
        if self._is_under_threat(piece, board):
            return 'SCARED'

        # Check if supporting ally
        if self._is_supporting_ally(piece, board):
            return 'CONFIDENT'

        return 'NEUTRAL'