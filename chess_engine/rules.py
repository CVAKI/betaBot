class Rules:
    @staticmethod
    def is_in_check(board, color):
        # Check if king is under attack
        king = board.find_king(color)
        if not king:
            return False
        return board.is_square_attacked(king.row, king.col,
                                        'black' if color == 'white' else 'white')

    @staticmethod
    def is_checkmate(board, game_state, color):
        # Check if in check with no legal moves
        pass

    @staticmethod
    def is_stalemate(board, game_state, color):
        # Check if no legal moves but not in check
        pass

    @staticmethod
    def get_legal_moves_for_piece(piece, board, game_state):
        # Generate all legal moves for a piece
        pass