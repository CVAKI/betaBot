"""
streamlit_app.py — β-bot Chess AI · Main Entry Point
======================================================
• Board: black × sea-blue (your original Pygame colours)
• UI:    premium purple × blue gradient (your provided CSS aesthetic)
• Pieces: loads your PNG files from assets/pieces/ automatically
          (mirrors config.PIECE_IMAGES logic from piece_renderer.py)
          falls back to crisp Unicode glyphs if PNGs are missing

Run:
    streamlit run streamlit_app.py
"""

import streamlit as st
import time, random, sys, os
from datetime import datetime

# ── Path ──────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="β-bot Chess AI",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import UI ─────────────────────────────────────────────────────────────────
try:
    from app_ui import (
        inject_styles, render_board_image, pil_to_bytes, st_image,
        html_header, html_hud, html_chat, html_material,
        html_captured, html_last_move, html_game_over,
        html_iq_table, html_emotion_grid, EMOTION_EMOJI,
    )
except ImportError as e:
    st.error(f"Cannot import app_ui.py — place it in the same folder.\n\n{e}")
    st.stop()

inject_styles()


# ══════════════════════════════════════════════════════════════════════════════
# STUB ENGINE  (used when the real β-bot project files are not present)
# Mirrors the structure of the real IntegratedGameManager so the UI
# renders identically whether running standalone or with the full engine.
# ══════════════════════════════════════════════════════════════════════════════

class _P:
    """Stub chess piece."""
    _n = 0
    def __init__(self, color, pt, row, col):
        self.color, self.piece_type = color, pt
        self.row,   self.col        = row, col
        self.is_captured  = False
        self.has_moved    = False
        self.current_emotion = "NEUTRAL"
        _P._n += 1
        self.id = f"{color}_{pt}_{_P._n}"
    def get_value(self):
        return {"pawn":1,"knight":3,"bishop":3,"rook":5,"queen":9,"king":0}.get(self.piece_type,1)
    def mark_moved(self): self.has_moved = True


class _Board:
    """Stub board."""
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]
        self._mc  = 0
    @property
    def move_count(self): return self._mc
    def get_all_pieces(self, color=None):
        return [p for row in self.grid for p in row
                if p and not p.is_captured and (color is None or p.color==color)]
    def get_piece_at(self, r, c):
        return self.grid[r][c] if 0<=r<8 and 0<=c<8 else None
    def set_piece_at(self, r, c, p):
        if 0<=r<8 and 0<=c<8: self.grid[r][c]=p
    def capture_piece(self, p):
        p.is_captured=True
        if 0<=p.row<8 and 0<=p.col<8: self.grid[p.row][p.col]=None
    def move_piece(self, fr, fc, tr, tc):
        p=self.grid[fr][fc]
        if p:
            self.grid[fr][fc]=None; p.row,p.col=tr,tc; self.grid[tr][tc]=p
        self._mc+=1
    def get_material_count(self, color):
        return sum(p.get_value() for p in self.get_all_pieces(color))
    def get_square_name(self, r, c):
        return "abcdefgh"[c]+str(8-r)
    def clear_board(self):
        self.grid=[[None]*8 for _ in range(8)]


class _State:
    def __init__(self):
        self.current_player="white"; self.move_count=0
    def switch_turn(self):
        self.current_player="black" if self.current_player=="white" else "white"
        self.move_count+=1


_BACK = ["rook","knight","bishop","queen","king","bishop","knight","rook"]
_EMOS = list(EMOTION_EMOJI.keys())


class StubGameManager:
    """Fully-functional stub that plays random-ish chess autonomously."""

    def __init__(self):
        self.board       = _Board()
        self.game_state  = _State()
        self.pieces: list = []
        self.chat_history: list = []
        self.game_over   = False
        self.winner      = None
        self.game_over_reason = ""
        self.ai_thinking = False
        self.last_move   = None
        self._last_t     = 0.0
        self.move_delay  = 1.0
        self.total_moves = 0

    def initialize_game(self):
        self._setup()
        self._log("System","♟ Game initialised — White to move.","NEUTRAL")

    def _setup(self):
        self.pieces.clear(); self.board.clear_board()
        for col in range(8):
            for color,row in [("white",6),("black",1)]:
                p=_P(color,"pawn",row,col); self.pieces.append(p); self.board.set_piece_at(row,col,p)
        for col,pt in enumerate(_BACK):
            for color,row in [("white",7),("black",0)]:
                p=_P(color,pt,row,col); self.pieces.append(p); self.board.set_piece_at(row,col,p)

    def update(self) -> bool:
        if self.game_over or self.ai_thinking: return False
        if time.time()-self._last_t < self.move_delay: return False
        self._do_move(); return True

    def _do_move(self):
        color = self.game_state.current_player
        en    = "black" if color=="white" else "white"
        active = [p for p in self.pieces if p.color==color and not p.is_captured]
        cands = []
        for piece in active:
            for mv in self._moves(piece):
                t=self.board.get_piece_at(*mv)
                cands.append((t.get_value()*12 if t else 0)+random.random(), piece, mv)
        if not cands: return
        cands.sort(reverse=True)
        _,piece,mv = cands[0]
        target=self.board.get_piece_at(*mv)
        if target:
            if target.piece_type=="king":
                self.board.capture_piece(target)
                self.game_over=True; self.winner=color
                loser="Black" if color=="white" else "White"
                self.game_over_reason=f"{loser} king captured — Checkmate!"
                self._log("System",f"🏁 {self.game_over_reason}","PROUD"); return
            self.board.capture_piece(target)
        fr,fc=piece.row,piece.col
        self.board.move_piece(fr,fc,*mv); piece.mark_moved()
        piece.current_emotion=random.choice(_EMOS)
        self.last_move=((fr,fc),mv)
        self._dialogue(piece,target,mv)
        self.game_state.switch_turn(); self.total_moves+=1; self._last_t=time.time()
        if self.total_moves>=300:
            self.game_over=True; self.winner="draw"; self.game_over_reason="Draw — 300 move limit"

    def _moves(self, piece):
        moves=[]; r,c=piece.row,piece.col
        en="black" if piece.color=="white" else "white"
        def add(tr,tc):
            if 0<=tr<8 and 0<=tc<8:
                t=self.board.get_piece_at(tr,tc)
                if t is None or t.color==en: moves.append((tr,tc))
        def slide(dr,dc):
            nr,nc=r+dr,c+dc
            while 0<=nr<8 and 0<=nc<8:
                t=self.board.get_piece_at(nr,nc)
                if t is None: moves.append((nr,nc)); nr+=dr; nc+=dc
                elif t.color==en: moves.append((nr,nc)); break
                else: break
        pt=piece.piece_type
        if pt=="pawn":
            d=-1 if piece.color=="white" else 1
            if 0<=r+d<8 and not self.board.get_piece_at(r+d,c):
                moves.append((r+d,c))
                if not piece.has_moved and not self.board.get_piece_at(r+2*d,c):
                    moves.append((r+2*d,c))
            for dc in [-1,1]:
                t=self.board.get_piece_at(r+d,c+dc) if 0<=c+dc<8 and 0<=r+d<8 else None
                if t and t.color==en: moves.append((r+d,c+dc))
        elif pt=="knight":
            for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]: add(r+dr,c+dc)
        elif pt=="bishop":
            for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]: slide(dr,dc)
        elif pt=="rook":
            for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]: slide(dr,dc)
        elif pt=="queen":
            for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]: slide(dr,dc)
        elif pt=="king":
            for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]: add(r+dr,c+dc)
        return moves

    def _dialogue(self, piece, captured, mv):
        pid=f"{piece.color.capitalize()} {piece.piece_type.capitalize()}"
        if captured:
            msgs=[
                f"Captured the enemy {captured.piece_type}! Material gained.",
                f"Took their {captured.piece_type} at {self.board.get_square_name(*mv)}.",
                f"The {captured.piece_type} falls. Position improved.",
            ]
        else:
            sq=self.board.get_square_name(*mv)
            msgs=[
                f"Advancing to {sq}. Observing.",
                f"Moving to {sq} — strategic repositioning.",
                f"Covering {sq}. Executing the plan.",
                f"Position at {sq} looks promising.",
            ]
        self._log(pid,random.choice(msgs),piece.current_emotion)

    def _log(self, sender, content, emotion):
        self.chat_history.append({
            "sender":sender,"content":content,
            "emotion":emotion,"timestamp":datetime.now(),
        })
        if len(self.chat_history)>160:
            self.chat_history=self.chat_history[-160:]

    def reset_game(self): self.__init__(); self.initialize_game()


# ══════════════════════════════════════════════════════════════════════════════
# REAL ENGINE LOADER
# ══════════════════════════════════════════════════════════════════════════════

def _load_gm():
    try:
        from main import IntegratedGameManager  # type: ignore
        return IntegratedGameManager, False
    except Exception as e:
        return None, str(e)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def _init():
    if "gm" not in st.session_state:
        RealGM, err = _load_gm()
        if RealGM:
            gm=RealGM(); st.session_state["stub"]=False
        else:
            gm=StubGameManager()
            st.session_state.update({"stub":True,"stub_err":err})
        gm.initialize_game()
        st.session_state.update({"gm":gm,"auto":True,"sq":88,"speed":1.0})
    return st.session_state["gm"]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    gm = _init()

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ◈ Control Panel")
        st.markdown("---")

        auto  = st.toggle("▶  Auto-Play", value=st.session_state.get("auto",True))
        st.session_state["auto"] = auto

        speed = st.slider("Move Delay (s)", 0.3, 4.0,
                          st.session_state.get("speed",1.0), step=0.1)
        st.session_state["speed"] = speed
        if hasattr(gm,"move_delay"): gm.move_delay=speed

        sq = st.slider("Board Square Size", 60, 108,
                       st.session_state.get("sq",88), step=4)
        st.session_state["sq"] = sq

        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            if st.button("↺  Reset", use_container_width=True):
                gm.reset_game(); st.rerun()
        with c2:
            if not gm.game_over:
                if st.button("⏭  Step", use_container_width=True):
                    gm.update(); st.rerun()

        st.markdown("---")
        st.markdown("### ◈ Material")
        w_mat = gm.board.get_material_count("white")
        b_mat = gm.board.get_material_count("black")
        st.markdown(html_material(w_mat,b_mat), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ◈ Captured")
        w_caps=[p for p in gm.pieces if p.color=="black" and p.is_captured]
        b_caps=[p for p in gm.pieces if p.color=="white" and p.is_captured]
        st.markdown(html_captured(w_caps,b_caps), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ◈ Stats")
        s1,s2 = st.columns(2)
        s1.metric("Moves",  gm.game_state.move_count)
        s2.metric("Total",  gm.total_moves)

        if st.session_state.get("stub"):
            st.markdown("---")
            st.warning("**Demo Mode** — real engine not found.", icon="⚠️")
            with st.expander("Import error"):
                st.code(st.session_state.get("stub_err",""))

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(html_header(), unsafe_allow_html=True)

    # ── GAME OVER BANNER ──────────────────────────────────────────────────────
    if gm.game_over:
        st.markdown(html_game_over(gm.winner or "draw", gm.game_over_reason),
                    unsafe_allow_html=True)
        _,btn,_ = st.columns([2,1,2])
        with btn:
            if st.button("↺  New Game", use_container_width=True):
                gm.reset_game(); st.rerun()

    # ── MAIN COLUMNS ──────────────────────────────────────────────────────────
    col_board, col_chat = st.columns([3,2], gap="medium")

    # ── Board ─────────────────────────────────────────────────────────────────
    with col_board:
        lm = getattr(gm,"last_move",None)

        st.markdown(
            html_hud(gm.game_state.current_player, gm.game_state.move_count,
                     gm.ai_thinking, gm.game_over),
            unsafe_allow_html=True,
        )

        board_img = render_board_image(
            gm.board,
            sq=st.session_state["sq"],
            last_move=lm,
            project_root=ROOT,
        )

        st.markdown('<div class="board-wrap">', unsafe_allow_html=True)
        st_image(pil_to_bytes(board_img))
        st.markdown(html_last_move(lm), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("🎭 Emotion Legend"):
            st.markdown(html_emotion_grid(), unsafe_allow_html=True)

    # ── Chat + IQ ─────────────────────────────────────────────────────────────
    with col_chat:
        st.markdown(html_chat(gm.chat_history), unsafe_allow_html=True)
        st.markdown('<div class="neo-hr"></div>', unsafe_allow_html=True)
        with st.expander("🧠 IQ Hierarchy"):
            st.markdown(html_iq_table(), unsafe_allow_html=True)

    # ── AUTO-PLAY ─────────────────────────────────────────────────────────────
    if st.session_state.get("auto") and not gm.game_over:
        gm.update()
        time.sleep(0.04)
        st.rerun()


if __name__ == "__main__":
    main()