class KingValidator:
    def __init__(self):
        self.veto_count = 0

    def validate_move(self, queen_decision, board, game_state):
        risk = self._assess_risk(queen_decision, board)

        if risk > 0.75 and self.veto_count < 3:
            self.veto_count += 1
            return {
                'approved': False,
                'reason': 'Risk too high',
                'veto_count': self.veto_count
            }

        return {'approved': True, 'reason': 'Acceptable'}