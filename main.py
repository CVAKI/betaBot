"""
β-bot Enhanced Main Game - FULLY FIXED
Fixes:
1. Game over when king is captured (checkmate detection)
2. HUD: turn indicator, move count, material score, captured pieces
3. Game over screen with winner announcement + play again
4. Stalemate / draw detection
5. Proper chess: kings cannot be captured past game over
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import time
import random
from datetime import datetime

import config
from chess_engine.board import Board
from chess_engine.game_state import GameState
from pieces.pawn import Pawn
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.queen import Queen
from pieces.king import King
from emotion.emotion_engine import EmotionEngine
from utils.logger import setup_logger, log_info, log_error


# ─── Colours used in HUD / overlay (not in config) ────────────────────────────
WHITE       = (255, 255, 255)
BLACK_COL   = (20,  20,  20)
GOLD        = (255, 215,   0)
SILVER      = (192, 192, 192)
RED         = (220,  50,  50)
GREEN       = ( 80, 200,  80)
PANEL_BG    = ( 25,  25,  35)
PANEL_DARK  = ( 15,  15,  22)
ACCENT_BLUE = ( 70, 140, 220)
ACCENT_GOLD = (220, 170,  40)


# ─── Tiny helpers ─────────────────────────────────────────────────────────────

def draw_rounded_rect(surf, color, rect, radius=8, alpha=None):
    if alpha is not None:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)


def render_text_shadow(surf, text, font, color, pos, shadow_col=(0,0,0), offset=2):
    surf.blit(font.render(text, True, shadow_col), (pos[0]+offset, pos[1]+offset))
    surf.blit(font.render(text, True, color), pos)


# ─── Game-over overlay ────────────────────────────────────────────────────────

class GameOverScreen:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font_big   = pygame.font.Font(None, 96)
        self.font_med   = pygame.font.Font(None, 52)
        self.font_small = pygame.font.Font(None, 36)
        self.alpha = 0          # for fade-in
        self.visible = False
        self.winner = None      # 'white', 'black', 'draw'
        self.reason = ''

    def show(self, winner, reason=''):
        self.winner = winner
        self.reason = reason
        self.visible = True
        self.alpha = 0

    def hide(self):
        self.visible = False
        self.winner = None

    def update(self):
        if self.visible and self.alpha < 230:
            self.alpha = min(230, self.alpha + 8)

    def draw(self, screen):
        if not self.visible:
            return

        # Dim background
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))
        screen.blit(overlay, (0, 0))

        if self.alpha < 60:
            return   # wait for fade

        # Central card
        cw, ch = 600, 340
        cx = (self.screen_w - cw) // 2
        cy = (self.screen_h - ch) // 2
        draw_rounded_rect(screen, PANEL_DARK, (cx, cy, cw, ch), radius=18)
        pygame.draw.rect(screen, ACCENT_GOLD, (cx, cy, cw, ch), 3, border_radius=18)

        # Determine colours & text
        if self.winner == 'draw':
            title = "DRAW"
            sub   = self.reason or "Stalemate"
            t_col = SILVER
        else:
            cap = self.winner.upper() if self.winner else '?'
            title = f"{cap} WINS!"
            sub   = self.reason or "King captured"
            t_col = GOLD if self.winner == 'white' else (160, 120, 220)

        # Title
        ts = self.font_big.render(title, True, t_col)
        screen.blit(ts, ts.get_rect(center=(self.screen_w//2, cy + 90)))

        # Sub
        ss = self.font_med.render(sub, True, WHITE)
        screen.blit(ss, ss.get_rect(center=(self.screen_w//2, cy + 175)))

        # Instruction
        blink = (pygame.time.get_ticks() // 600) % 2 == 0
        if blink:
            ins = self.font_small.render("Press  R  to play again   |   ESC  to quit", True, SILVER)
            screen.blit(ins, ins.get_rect(center=(self.screen_w//2, cy + 290)))


# ─── HUD (turn, score, move counter, captured pieces) ─────────────────────────

class HUD:
    def __init__(self, layout):
        self.layout = layout
        self.font_lg  = pygame.font.Font(None, 32)
        self.font_md  = pygame.font.Font(None, 24)
        self.font_sm  = pygame.font.Font(None, 20)

    def draw(self, screen, game_manager):
        lx = self.layout['board_offset_x']
        bsize = self.layout['board_size']
        sq = self.layout['square_size']

        # ── top bar above board ───────────────────────────────────────────
        bar_y = 8
        bar_h = 38
        draw_rounded_rect(screen, PANEL_BG, (lx, bar_y, bsize, bar_h), radius=6)

        gs = game_manager.game_state
        cur = gs.current_player
        move_num = gs.move_count

        # Turn indicator
        col = WHITE if cur == 'white' else (180, 120, 240)
        dot_x = lx + 14
        pygame.draw.circle(screen, col, (dot_x, bar_y + bar_h//2), 8)
        pygame.draw.circle(screen, WHITE, (dot_x, bar_y + bar_h//2), 8, 2)
        turn_txt = self.font_lg.render(f"{cur.upper()}'S TURN", True, col)
        screen.blit(turn_txt, (dot_x + 16, bar_y + 8))

        # Move counter
        mc_txt = self.font_md.render(f"Move  {move_num}", True, SILVER)
        screen.blit(mc_txt, mc_txt.get_rect(midright=(lx + bsize - 12, bar_y + bar_h//2)))

        # ── material score bar below board ────────────────────────────────
        sb_y = self.layout['board_offset_y'] + bsize + 8
        sb_h = 36
        draw_rounded_rect(screen, PANEL_BG, (lx, sb_y, bsize, sb_h), radius=6)

        w_mat = game_manager.board.get_material_count('white')
        b_mat = game_manager.board.get_material_count('black')
        diff  = w_mat - b_mat

        w_txt = self.font_md.render(f"♙ White  {w_mat}", True, WHITE)
        b_txt = self.font_md.render(f"♟ Black  {b_mat}", True, (180, 120, 240))
        screen.blit(w_txt, (lx + 10, sb_y + 8))
        screen.blit(b_txt, b_txt.get_rect(midright=(lx + bsize - 10, sb_y + 18)))

        if diff != 0:
            leader = 'White' if diff > 0 else 'Black'
            adv_col = WHITE if diff > 0 else (180, 120, 240)
            adv_txt = self.font_sm.render(f"+{abs(diff)} {leader}", True, adv_col)
            screen.blit(adv_txt, adv_txt.get_rect(center=(lx + bsize//2, sb_y + 18)))

        # ── captured pieces strip ─────────────────────────────────────────
        self._draw_captured(screen, game_manager, lx, sb_y + sb_h + 4)

    def _draw_captured(self, screen, gm, x, y):
        symbols = {'king':'K','queen':'Q','rook':'R','bishop':'B','knight':'N','pawn':'P'}
        font = self.font_sm

        # White captured black pieces
        w_caps = [p for p in gm.pieces if p.color == 'black' and p.is_captured]
        b_caps = [p for p in gm.pieces if p.color == 'white' and p.is_captured]

        if w_caps:
            txt = "Captured by White: " + " ".join(symbols.get(p.piece_type,'?') for p in w_caps)
            screen.blit(font.render(txt, True, (200, 200, 200)), (x, y))
        if b_caps:
            txt = "Captured by Black: " + " ".join(symbols.get(p.piece_type,'?') for p in b_caps)
            screen.blit(font.render(txt, True, (200, 200, 200)), (x, y + 18))


# ─── Window ───────────────────────────────────────────────────────────────────

class EnhancedGameWindow:
    def __init__(self):
        pygame.init()
        display_info = pygame.display.Info()

        if config.USE_FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
            self.screen_width  = display_info.current_w
            self.screen_height = display_info.current_h
        else:
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            self.screen_width  = config.SCREEN_WIDTH
            self.screen_height = config.SCREEN_HEIGHT

        pygame.display.set_caption("β-bot: Multi-Agent Chess AI")
        self.layout = self._calculate_layout()

        try:
            from ui.enhanced_ui import EnhancedBoardRenderer, EnhancedPieceRenderer, EnhancedChatPanel
            self.board_renderer = EnhancedBoardRenderer(self.layout)
            self.piece_renderer = EnhancedPieceRenderer(self.layout)
            self.chat_panel     = EnhancedChatPanel(self.layout)
            log_info("Loaded enhanced UI components")
        except ImportError:
            from ui.board_renderer import BoardRenderer
            from ui.piece_renderer import PieceRenderer
            from ui.chat_panel    import ChatPanel
            self.board_renderer = BoardRenderer()
            self.piece_renderer = PieceRenderer()
            self.chat_panel     = ChatPanel()
            log_info("Using standard UI components")

        self.hud          = HUD(self.layout)
        self.game_over_sc = GameOverScreen(self.screen_width, self.screen_height)
        print(f"✅ Window initialized at {self.screen_width}x{self.screen_height}")

    def _calculate_layout(self):
        board_size = int(min(self.screen_height * 0.85, self.screen_width * 0.55))
        square_size = board_size // 8
        chat_w = self.screen_width - board_size - 150
        return {
            'board_size':       board_size,
            'square_size':      square_size,
            'board_offset_x':   50,
            'board_offset_y':   55,          # leave room for top HUD bar
            'chat_panel_width': chat_w,
            'chat_panel_height':self.screen_height - 100,
            'chat_panel_x':     board_size + 100,
            'chat_panel_y':     50,
        }

    def render(self, game_manager):
        try:
            self.screen.fill(config.BACKGROUND_COLOR)
            self.board_renderer.draw_board(self.screen)

            if hasattr(game_manager, 'board'):
                for piece in game_manager.board.get_all_pieces():
                    if not piece.is_captured:
                        self.piece_renderer.draw_piece(self.screen, piece)

            if hasattr(game_manager, 'chat_history'):
                self.chat_panel.draw(self.screen, game_manager.chat_history)

            # HUD always drawn
            self.hud.draw(self.screen, game_manager)

            # Game-over overlay on top
            self.game_over_sc.update()
            self.game_over_sc.draw(self.screen)

        except Exception as e:
            log_error(f"Render error: {e}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        config.USE_FULLSCREEN = not config.USE_FULLSCREEN
        if config.USE_FULLSCREEN:
            di = pygame.display.Info()
            self.screen = pygame.display.set_mode((di.current_w, di.current_h), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = di.current_w, di.current_h
        else:
            self.screen = pygame.display.set_mode((1600, 900))
            self.screen_width, self.screen_height = 1600, 900
        self.layout = self._calculate_layout()
        for r in (self.board_renderer, self.piece_renderer, self.chat_panel, self.hud):
            if hasattr(r, 'update_layout'):
                r.update_layout(self.layout)
        self.game_over_sc = GameOverScreen(self.screen_width, self.screen_height)


# ─── Game manager ─────────────────────────────────────────────────────────────

class IntegratedGameManager:
    """Fixed game manager with proper chess rules + game over"""

    def __init__(self):
        self.board      = Board()
        self.game_state = GameState()
        self.pieces     = []
        self.chat_history = []

        # anti-repetition
        self.recent_moves          = []
        self.position_hashes       = []
        self.piece_last_positions  = {}

        # game state
        self.game_over   = False
        self.winner      = None      # 'white' | 'black' | 'draw'
        self.game_over_reason = ''

        try:
            from ai_brain.enhanced_strategy import SmartDecisionPipeline
            self.decision_pipeline = SmartDecisionPipeline()
            self.has_enhanced_ai   = True
            log_info("Loaded enhanced AI strategy")
        except ImportError:
            self.decision_pipeline = None
            self.has_enhanced_ai   = False

        try:
            from llm_integration.active_dialogue import ActiveDialogueSystem, ProximityChatManager
            self.dialogue_system = ActiveDialogueSystem()
            self.proximity_chat  = ProximityChatManager(self.dialogue_system)
            self.has_llm = True
            log_info("Loaded LLM dialogue system")
        except ImportError:
            self.dialogue_system = None
            self.proximity_chat  = None
            self.has_llm = False

        try:
            self.emotion_engine = EmotionEngine()
        except:
            self.emotion_engine = None

        self.ai_thinking    = False
        self.last_move_time = 0
        self.move_delay     = 1.5
        self.total_moves    = 0
        self.captures       = {'white': 0, 'black': 0}

    # ── Setup ──────────────────────────────────────────────────────────────────

    def initialize_game(self):
        self._setup_pieces()
        self.position_hashes.append(self._get_position_hash())
        self._add_chat_message("System", "♟️ Game started! White to move.", "NEUTRAL")
        print("✅ Game initialized successfully")

    def _setup_pieces(self):
        self.pieces.clear()
        self.board.clear_board()

        for col in range(8):
            p = Pawn('white', 6, col)
            self.pieces.append(p); self.board.set_piece_at(6, col, p)

        for piece in [Rook('white',7,0), Knight('white',7,1), Bishop('white',7,2),
                      Queen('white',7,3), King('white',7,4),
                      Bishop('white',7,5), Knight('white',7,6), Rook('white',7,7)]:
            self.pieces.append(piece); self.board.set_piece_at(piece.row, piece.col, piece)

        for col in range(8):
            p = Pawn('black', 1, col)
            self.pieces.append(p); self.board.set_piece_at(1, col, p)

        for piece in [Rook('black',0,0), Knight('black',0,1), Bishop('black',0,2),
                      Queen('black',0,3), King('black',0,4),
                      Bishop('black',0,5), Knight('black',0,6), Rook('black',0,7)]:
            self.pieces.append(piece); self.board.set_piece_at(piece.row, piece.col, piece)

        print(f"  Created {len(self.pieces)} pieces")

    # ── Main update ────────────────────────────────────────────────────────────

    def update(self):
        if self.game_over or self.ai_thinking:
            return
        if time.time() - self.last_move_time < self.move_delay:
            return
        self.execute_ai_turn()

    # ── Game-over check ────────────────────────────────────────────────────────

    def _check_game_over(self):
        """Returns (is_over, winner, reason)"""
        w_king = self.board.find_king('white')
        b_king = self.board.find_king('black')

        if w_king is None or w_king.is_captured:
            return True, 'black', 'White king captured — Checkmate!'
        if b_king is None or b_king.is_captured:
            return True, 'white', 'Black king captured — Checkmate!'

        # Stalemate: current player has no legal moves
        cur = self.game_state.current_player
        active = [p for p in self.pieces if p.color == cur and not p.is_captured]
        any_moves = any(p.get_possible_moves(self.board) for p in active)
        if not any_moves:
            return True, 'draw', 'Stalemate — No legal moves!'

        # 50-move rule (simplified: 150 half-moves without capture)
        if self.game_state.move_count > 150 and len(self.captures['white'] if isinstance(self.captures['white'], list) else []) == 0:
            pass  # skip for now, just use move limit below

        # Hard cap: very long game → draw
        if self.game_state.move_count > 300:
            return True, 'draw', 'Draw — Game too long (300 moves)'

        return False, None, ''

    # ── AI turn ────────────────────────────────────────────────────────────────

    def execute_ai_turn(self):
        self.ai_thinking = True
        try:
            current_color = self.game_state.current_player

            if self.emotion_engine:
                try:
                    self.emotion_engine.update_all_emotions(self.board, self.game_state)
                except:
                    pass

            # repetition guard
            if self._is_threefold_repetition():
                print("⚠️  Repetition detected! Forcing new move.")
                self._force_varied_move(current_color)
                return

            active_pieces = [p for p in self.board.get_all_pieces(current_color)
                             if not p.is_captured]
            if not active_pieces:
                return

            suggestions = self._collect_suggestions(active_pieces, current_color)
            if not suggestions:
                self._add_chat_message("System", f"{current_color} has no legal moves!", "SAD")
                return

            suggestions.sort(key=lambda x: x['score'], reverse=True)

            # LLM chatter (best-effort)
            if self.has_llm and self.proximity_chat:
                self._trigger_proximity_chats(active_pieces)
            if self.has_llm and self.dialogue_system:
                queen = self._find_piece_by_type(active_pieces, 'queen')
                if queen:
                    try:
                        msg = self.dialogue_system.generate_queen_synthesis(
                            queen, suggestions[:5], self._calculate_board_evaluation())
                        self._add_chat_message(queen.id, msg, queen.current_emotion)
                    except:
                        pass

            best_move = suggestions[0]

            # King veto
            if self.has_llm and self.dialogue_system:
                king = self._find_piece_by_type(active_pieces, 'king')
                if king:
                    try:
                        risk = self._assess_move_risk(best_move)
                        kd = self.dialogue_system.generate_king_approval(
                            king, f"Move {best_move['piece'].piece_type} to {best_move['to']}", risk)
                        self._add_chat_message(king.id, kd['message'], king.current_emotion)
                        if not kd['approved'] and hasattr(king, 'veto_count') and king.veto_count < 3:
                            king.veto_count += 1
                            if len(suggestions) > 1:
                                best_move = suggestions[1]
                    except:
                        pass

            self._execute_move(best_move)

            # ── CHECK GAME OVER AFTER EVERY MOVE ──────────────────────────
            is_over, winner, reason = self._check_game_over()
            if is_over:
                self.game_over  = True
                self.winner     = winner
                self.game_over_reason = reason
                print(f"🏁 GAME OVER: {reason}")
                self._add_chat_message("System", f"🏁 {reason}", "PROUD" if winner != 'draw' else "NEUTRAL")
                return
            # ──────────────────────────────────────────────────────────────

            self.game_state.switch_turn()
            self.total_moves    += 1
            self.last_move_time  = time.time()

        except Exception as e:
            log_error(f"Error in AI turn: {e}")
            import traceback; traceback.print_exc()
        finally:
            self.ai_thinking = False

    # ── Suggestion collection ──────────────────────────────────────────────────

    def _collect_suggestions(self, active_pieces, color):
        suggestions = []
        for piece in active_pieces:
            if self.has_enhanced_ai:
                try:
                    move_data = self.decision_pipeline.get_best_move_for_piece(
                        piece, self.board, self.game_state)
                except:
                    move_data = piece.suggest_move(self.board, self.game_state)
            else:
                move_data = piece.suggest_move(self.board, self.game_state)

            if not move_data or move_data.get('score', 0) <= -999:
                continue

            to_pos = move_data['to']

            if self._would_cause_repetition(piece, to_pos):
                alt = self._find_non_repeating_move(piece)
                if alt:
                    move_data = alt
                    to_pos    = move_data['to']
                else:
                    continue

            suggestions.append({
                'piece':      piece,
                'from':       move_data['from'],
                'to':         to_pos,
                'score':      move_data.get('score', 0),
                'confidence': move_data.get('confidence', 0.5),
                'reasoning':  move_data.get('reasoning', 'strategic move'),
            })
        return suggestions

    def _would_cause_repetition(self, piece, to_pos) -> bool:
        h = self._simulate_position_hash(piece, to_pos)
        if h in self.position_hashes[-6:]:
            return True
        hist = self.piece_last_positions.get(piece.id, [])
        if to_pos in hist[-2:]:
            return True
        return False

    def _find_non_repeating_move(self, piece):
        moves = piece.get_possible_moves(self.board)
        random.shuffle(moves)
        for mv in moves:
            if not self._would_cause_repetition(piece, mv):
                return {'from': (piece.row, piece.col), 'to': mv,
                        'score': self._score_move(piece, mv), 'confidence': 0.5,
                        'reasoning': 'varied play'}
        return None

    def _score_move(self, piece, move) -> float:
        to_row, to_col = move
        score = (7 - (abs(to_row - 3.5) + abs(to_col - 3.5))) * 0.5
        target = self.board.get_piece_at(to_row, to_col)
        if target and piece.is_enemy(target):
            score += target.get_value() * 3.0
        hist = self.piece_last_positions.get(piece.id, [])
        if move in hist:
            score -= hist.count(move) * 5.0
        score += random.random() * 1.0
        return score

    # ── Repetition helpers ─────────────────────────────────────────────────────

    def _is_threefold_repetition(self) -> bool:
        if len(self.position_hashes) < 5:
            return False
        return self.position_hashes.count(self._get_position_hash()) >= 3

    def _force_varied_move(self, color):
        pieces = [p for p in self.pieces if p.color == color and not p.is_captured]
        recent_ids = {m[0] for m in self.recent_moves[-6:]}
        fresh = [p for p in pieces if p.id not in recent_ids]
        candidates = fresh if fresh else pieces
        random.shuffle(candidates)

        for piece in candidates:
            moves = piece.get_possible_moves(self.board)
            random.shuffle(moves)
            for mv in moves:
                if self._simulate_position_hash(piece, mv) not in self.position_hashes:
                    self._execute_move({'piece': piece, 'from': (piece.row, piece.col),
                                        'to': mv, 'score': 0.0})
                    self._add_chat_message(piece.id, "Trying a new approach!", "CONFIDENT")
                    is_over, winner, reason = self._check_game_over()
                    if is_over:
                        self.game_over = True; self.winner = winner
                        self.game_over_reason = reason
                        print(f"🏁 GAME OVER: {reason}")
                        self._add_chat_message("System", f"🏁 {reason}", "PROUD")
                        return
                    self.game_state.switch_turn()
                    self.total_moves   += 1
                    self.last_move_time = time.time()
                    return

        # absolute fallback
        for piece in pieces:
            moves = piece.get_possible_moves(self.board)
            if moves:
                self._execute_move({'piece': piece, 'from': (piece.row, piece.col),
                                    'to': random.choice(moves), 'score': 0.0})
                self.game_state.switch_turn()
                self.total_moves   += 1
                self.last_move_time = time.time()
                return

    def _simulate_position_hash(self, piece, move) -> str:
        positions = []
        for p in self.pieces:
            if p.is_captured:
                continue
            positions.append(f"{p.id}:{move[0]},{move[1]}" if p == piece
                             else f"{p.id}:{p.row},{p.col}")
        return "|".join(sorted(positions))

    def _get_position_hash(self) -> str:
        return "|".join(sorted(
            f"{p.id}:{p.row},{p.col}" for p in self.pieces if not p.is_captured))

    # ── Execute move (records history) ────────────────────────────────────────

    def _execute_move(self, move_data):
        piece    = move_data['piece']
        from_row, from_col = move_data['from']
        to_row,   to_col   = move_data['to']

        target = self.board.get_piece_at(to_row, to_col)
        if target:
            self.board.capture_piece(target)
            self.captures[piece.color] += 1

        self.board.move_piece(from_row, from_col, to_row, to_col)
        piece.mark_moved()

        from_pos = (from_row, from_col)
        to_pos   = (to_row,   to_col)

        self.recent_moves.append((piece.id, from_pos, to_pos))
        if len(self.recent_moves) > 20:
            self.recent_moves.pop(0)

        if piece.id not in self.piece_last_positions:
            self.piece_last_positions[piece.id] = []
        self.piece_last_positions[piece.id].append(to_pos)
        if len(self.piece_last_positions[piece.id]) > 6:
            self.piece_last_positions[piece.id].pop(0)

        ph = self._get_position_hash()
        self.position_hashes.append(ph)
        if len(self.position_hashes) > 60:
            self.position_hashes.pop(0)

        from_sq = self.board.get_square_name(from_row, from_col)
        to_sq   = self.board.get_square_name(to_row,   to_col)
        print(f"  {piece.color} {piece.piece_type}: {from_sq} → {to_sq}")

    # ── Utilities ──────────────────────────────────────────────────────────────

    def _trigger_proximity_chats(self, active_pieces):
        for piece in active_pieces[:3]:
            nearby = [o for o in active_pieces if o != piece
                      and abs(piece.row-o.row)+abs(piece.col-o.col) <= 2]
            if nearby and self.proximity_chat:
                try:
                    msg = self.proximity_chat.trigger_proximity_chat(piece, nearby, self.board)
                    if msg:
                        self.chat_history.append(msg)
                except:
                    pass

    def _find_piece_by_type(self, pieces, pt):
        return next((p for p in pieces if p.piece_type == pt), None)

    def _calculate_board_evaluation(self):
        color = self.game_state.current_player
        enemy = 'black' if color == 'white' else 'white'
        return self.board.get_material_count(color) - self.board.get_material_count(enemy)

    def _assess_move_risk(self, move_data):
        piece = move_data['piece']
        king  = self.board.find_king(piece.color)
        if king and self.has_enhanced_ai:
            try:
                from ai_brain.enhanced_strategy import EnhancedMoveEvaluator
                if EnhancedMoveEvaluator._is_king_threatened(self.board, king):
                    return 0.8
            except:
                pass
        return 0.3

    def _add_chat_message(self, sender, content, emotion):
        self.chat_history.append({
            'sender': sender, 'content': content,
            'emotion': emotion, 'timestamp': datetime.now()
        })
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]

    def reset_game(self):
        self.game_state    = GameState()
        self.game_over     = False
        self.winner        = None
        self.game_over_reason = ''
        self.chat_history.clear()
        self.recent_moves.clear()
        self.position_hashes.clear()
        self.piece_last_positions.clear()
        self.total_moves = 0
        self.captures    = {'white': 0, 'black': 0}
        self._setup_pieces()
        self.position_hashes.append(self._get_position_hash())
        self._add_chat_message("System", "🔄 New game! White to move.", "NEUTRAL")

    def handle_mouse_click(self, pos):
        pass

    def cleanup(self):
        pass


# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    logger = setup_logger('main')
    log_info("=" * 60)
    log_info("β-bot: Enhanced Multi-Agent Chess AI Starting")
    log_info("=" * 60)

    game_window  = EnhancedGameWindow()
    clock        = pygame.time.Clock()
    game_manager = IntegratedGameManager()
    game_manager.initialize_game()

    running  = True
    paused   = False
    show_fps = True

    print("\n🎮 Controls:")
    print("   ESC      – Quit")
    print("   SPACE    – Pause / Resume")
    print("   R        – Reset / New game")
    print("   F11      – Toggle Fullscreen")
    print("   F        – Toggle FPS\n")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_SPACE:
                        if not game_manager.game_over:
                            paused = not paused
                            print("⏸️  Paused" if paused else "▶️  Resumed")

                    elif event.key == pygame.K_r:
                        game_manager.reset_game()
                        game_window.game_over_sc.hide()
                        paused = False
                        print("🔄 New game started")
                        log_info("Game reset")

                    elif event.key == pygame.K_f:
                        show_fps = not show_fps

                    elif event.key == pygame.K_F11:
                        game_window.toggle_fullscreen()

                game_window.handle_event(event)

            # update game logic
            if not paused and not game_manager.game_over:
                game_manager.update()

            # show game-over overlay when game ends
            if game_manager.game_over and not game_window.game_over_sc.visible:
                game_window.game_over_sc.show(
                    game_manager.winner,
                    game_manager.game_over_reason)

            # render
            game_window.render(game_manager)

            # FPS counter
            if show_fps:
                fps_surf = pygame.font.Font(None, 26).render(
                    f"FPS: {int(clock.get_fps())}", True, GREEN)
                game_window.screen.blit(fps_surf, (10, 10))

            # PAUSED banner
            if paused:
                font = pygame.font.Font(None, 64)
                pt   = font.render("⏸ PAUSED", True, GOLD)
                pr   = pt.get_rect(center=(game_window.screen_width // 2, 40))
                bg   = pr.inflate(40, 16)
                pygame.draw.rect(game_window.screen, BLACK_COL, bg, border_radius=10)
                game_window.screen.blit(pt, pr)

            pygame.display.flip()
            clock.tick(config.FPS)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback; traceback.print_exc()
    finally:
        print("\n👋 Shutting down β-bot...")
        try:
            game_manager.cleanup()
        except:
            pass
        pygame.quit()
        log_info("β-bot shutdown complete")
        print("✅ Goodbye!\n")


if __name__ == "__main__":
    main()