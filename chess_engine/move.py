class Move:
    def __init__(self, from_pos, to_pos, piece_type, special_flag=None):
        self.from_pos = from_pos  # (row, col)
        self.to_pos = to_pos
        self.piece_type = piece_type
        self.special_flag = special_flag  # 'castle', 'en_passant', 'promotion'
        self.captured_piece = None
        self.timestamp = None

    def to_algebraic(self):
        # Convert to notation like "e2e4" or "Nf3"
        pass

    def is_capture(self):
        return self.captured_piece is not None