class GameState:
    def __init__(self):
        self.current_player = 'white'
        self.move_history = []
        self.castling_rights = {
            'white_kingside': True,
            'white_queenside': True,
            'black_kingside': True,
            'black_queenside': True
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.king_veto_count = 0
        self.game_phase = 'opening'  # opening, midgame, endgame

    def switch_turn(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'

    def add_move(self, move):
        self.move_history.append(move)