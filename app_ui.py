"""
app_ui.py — β-bot Chess AI · UI Module
========================================
Board:  Black × Sea-Blue (matches your original Pygame theme)
UI:     Premium Purple × Blue gradient aesthetic (inspired by your CSS)
Pieces: Loads your PNG files from assets/pieces/ — identical to the
        original piece_renderer.py / enhanced_ui.py logic.
        Falls back to crisp Unicode glyphs if PNGs are missing.
"""

from __future__ import annotations
import io, os
from datetime import datetime
from typing import Optional, List, Tuple, Dict

from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# PIECE IMAGE PATHS  — mirrors config.PIECE_IMAGES from the original project
# All common naming conventions are tried in order.
# ══════════════════════════════════════════════════════════════════════════════

def _build_piece_paths(root: str = ".") -> Dict[str, Dict[str, List[str]]]:
    """
    Return a dict of candidate PNG paths for every piece.
    Tries every naming convention used in chess asset packs.
    """
    def candidates(color: str, pt: str) -> List[str]:
        c1 = color[0]           # w / b
        C1 = color[0].upper()   # W / B
        PT = pt.capitalize()    # King / Queen …
        abbr  = pt[0].upper()   # K Q R B N P
        # knight special case
        abbr_n = 'N' if pt == 'knight' else abbr

        bases = [
            f"assets/pieces/{color}_{pt}.png",
            f"assets/pieces/{color}/{pt}.png",
            f"assets/pieces/{c1}{abbr_n}.png",
            f"assets/pieces/{C1}{abbr_n}.png",
            f"assets/pieces/{color}_{pt.capitalize()}.png",
            f"assets/pieces/{pt}_{color}.png",
            f"assets/{color}_{pt}.png",
            f"assets/{c1}{abbr_n}.png",
            f"pieces/{color}_{pt}.png",
            f"pieces/{c1}{abbr_n}.png",
            f"images/{color}_{pt}.png",
            f"images/{c1}{abbr_n}.png",
        ]
        # prepend project root
        return [os.path.join(root, b) for b in bases] + bases

    paths: Dict[str, Dict[str, List[str]]] = {}
    for color in ("white", "black"):
        paths[color] = {}
        for pt in ("king", "queen", "rook", "bishop", "knight", "pawn"):
            paths[color][pt] = candidates(color, pt)
    return paths


# Unicode fallback glyphs
PIECE_SYMS: Dict[Tuple[str, str], str] = {
    ("white","king"):"♔", ("white","queen"):"♕", ("white","rook"):"♖",
    ("white","bishop"):"♗", ("white","knight"):"♘", ("white","pawn"):"♙",
    ("black","king"):"♚", ("black","queen"):"♛", ("black","rook"):"♜",
    ("black","bishop"):"♝", ("black","knight"):"♞", ("black","pawn"):"♟",
}

EMOTION_EMOJI: Dict[str, str] = {
    "HAPPY":"😊","SAD":"😢","SCARED":"😰","CONFIDENT":"😤",
    "ANGRY":"😠","NEUTRAL":"😐","ANXIOUS":"😟","PROUD":"😎",
    "RESIGNED":"😔","EXCITED":"🤩","DETERMINED":"💪","DESPERATE":"😭",
}

EMOTION_DOT: Dict[str, Tuple[int,int,int]] = {
    "HAPPY":(80,240,80),"SAD":(80,120,255),"SCARED":(255,150,30),
    "CONFIDENT":(0,220,130),"ANGRY":(255,50,50),"NEUTRAL":(140,150,200),
    "ANXIOUS":(255,200,50),"PROUD":(200,60,255),"RESIGNED":(110,120,140),
    "EXCITED":(255,230,0),"DETERMINED":(0,200,220),"DESPERATE":(220,30,30),
}

# Board palette — black × sea-blue
LIGHT_SQ   = (22,  55, 110)    # sea blue
DARK_SQ    = (7,   18,  44)    # deep navy
HL_FROM    = (0,   90, 180)
HL_TO      = (0,  150, 255)
BG_CANVAS  = (3,    6,  18)

WHITE_FILL = (230, 242, 255)
BLACK_FILL = (55,  120, 255)
WHITE_SH   = (0,   15,  60, 100)
BLACK_SH   = (0,    0,  15, 120)

_FONTS     = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
              "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
_FONTS_BD  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for p in (_FONTS_BD if bold else _FONTS):
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: continue
    return ImageFont.load_default()


# ══════════════════════════════════════════════════════════════════════════════
# PNG PIECE CACHE  (loaded once, scaled on demand)
# ══════════════════════════════════════════════════════════════════════════════

_PNG_CACHE: Dict[str, Optional[Image.Image]] = {}   # "color_pt_sq" → PIL Image


def _load_piece_png(color: str, pt: str, sq: int, root: str = ".") -> Optional[Image.Image]:
    key = f"{color}_{pt}_{sq}"
    if key in _PNG_CACHE:
        return _PNG_CACHE[key]

    paths = _build_piece_paths(root)
    for candidate in paths[color][pt]:
        if os.path.exists(candidate):
            try:
                img = Image.open(candidate).convert("RGBA")
                img = img.resize((sq, sq), Image.LANCZOS)
                _PNG_CACHE[key] = img
                return img
            except Exception:
                continue

    _PNG_CACHE[key] = None
    return None


# ══════════════════════════════════════════════════════════════════════════════
# BOARD RENDERER
# ══════════════════════════════════════════════════════════════════════════════

def render_board_image(
    board_obj,
    sq: int = 90,
    last_move: Optional[Tuple] = None,
    project_root: str = ".",
) -> Image.Image:
    """
    Render chess board as PIL RGB image.
    Uses PNG piece images when available, Unicode glyphs otherwise.
    """
    MARGIN = 34
    W = sq * 8 + MARGIN
    H = sq * 8 + MARGIN + 12

    canvas = Image.new("RGBA", (W, H), (*BG_CANVAS, 255))
    draw   = ImageDraw.Draw(canvas, "RGBA")
    pfont  = _font(int(sq * 0.72))
    cfont  = _font(14, bold=True)

    # ── Squares ───────────────────────────────────────────────────────────────
    for row in range(8):
        for col in range(8):
            x = MARGIN + col * sq; y = row * sq
            base = LIGHT_SQ if (row + col) % 2 == 0 else DARK_SQ
            if last_move:
                (fr, fc), (tr, tc) = last_move
                if (row, col) == (fr, fc):   base = HL_FROM
                elif (row, col) == (tr, tc): base = HL_TO
            draw.rectangle([x, y, x+sq-1, y+sq-1], fill=(*base, 255))
            draw.rectangle([x, y, x+sq-1, y+sq-1], outline=(0,30,80,80), width=1)

    # ── Coordinates ───────────────────────────────────────────────────────────
    for i in range(8):
        ch = "abcdefgh"[i]
        bb = draw.textbbox((0,0), ch, font=cfont)
        cx = MARGIN + i*sq + (sq - (bb[2]-bb[0]))//2 - bb[0]
        draw.text((cx, sq*8+8), ch, fill=(60,130,230,200), font=cfont)
        ch2 = "87654321"[i]
        bb2 = draw.textbbox((0,0), ch2, font=cfont)
        ry = i*sq + (sq - (bb2[3]-bb2[1]))//2 - bb2[1]
        draw.text((5, ry), ch2, fill=(60,130,230,200), font=cfont)

    # ── Pieces ────────────────────────────────────────────────────────────────
    pieces: List = []
    if board_obj is not None:
        try:
            pieces = [p for p in board_obj.get_all_pieces() if not p.is_captured]
        except Exception:
            pass

    for piece in pieces:
        px = MARGIN + piece.col * sq
        py = piece.row * sq

        # Try PNG first
        png = _load_piece_png(piece.color, piece.piece_type, sq, project_root)
        if png is not None:
            # Paste PNG with transparency
            canvas.alpha_composite(png, dest=(px, py))
        else:
            # Unicode fallback — perfectly centred
            sym = PIECE_SYMS.get((piece.color, piece.piece_type), "?")
            bb = draw.textbbox((0,0), sym, font=pfont)
            tw = bb[2]-bb[0]; th = bb[3]-bb[1]
            tx = px + (sq-tw)//2 - bb[0]
            ty = py + (sq-th)//2 - bb[1] - 2
            sc = WHITE_SH if piece.color=="white" else BLACK_SH
            draw.text((tx+2, ty+3), sym, fill=sc, font=pfont)
            fc = (*WHITE_FILL,255) if piece.color=="white" else (*BLACK_FILL,255)
            draw.text((tx, ty), sym, fill=fc, font=pfont)

        # Emotion dot — top-right corner
        emo     = getattr(piece, "current_emotion", "NEUTRAL")
        dot_rgb = EMOTION_DOT.get(emo, (140,150,200))
        dr      = max(5, sq//13)
        dx      = px + sq - dr*2 - 5; dy = py + 5
        draw.ellipse([dx-2,dy-2,dx+dr*2+2,dy+dr*2+2], fill=(*dot_rgb,45))
        draw.ellipse([dx,dy,dx+dr*2,dy+dr*2], fill=(*dot_rgb,225))

    # ── Border glow ───────────────────────────────────────────────────────────
    for i in range(5, 0, -1):
        a = int(55/i)
        draw.rectangle([MARGIN-i,-i,MARGIN+sq*8+i,sq*8+i], outline=(0,100,255,a), width=1)
    draw.rectangle([MARGIN,0,MARGIN+sq*8-1,sq*8-1], outline=(0,130,255,220), width=2)

    return canvas.convert("RGB")


def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()


def st_image(img_bytes: bytes) -> None:
    try: st.image(img_bytes, use_container_width=True)
    except TypeError: st.image(img_bytes)


# ══════════════════════════════════════════════════════════════════════════════
# CSS — Purple × Blue premium aesthetic (inspired by your provided CSS)
# ══════════════════════════════════════════════════════════════════════════════

def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Keyframes ── */
@keyframes gradShift {
  0%,100%{background-position:0% 50%;}
  50%{background-position:100% 50%;}
}
@keyframes orbFloat {
  0%,100%{transform:translateY(0) scale(1);opacity:.25;}
  33%{transform:translateY(-30px) scale(1.08);opacity:.45;}
  66%{transform:translateY(-55px) scale(.93);opacity:.6;}
}
@keyframes badgeGlow {
  0%,100%{box-shadow:0 0 10px rgba(138,43,226,.3);}
  50%{box-shadow:0 0 22px rgba(138,43,226,.65);}
}
@keyframes titleShine {
  0%,100%{background-position:0% 50%;}
  50%{background-position:200% 50%;}
}
@keyframes cardHover {
  0%,100%{box-shadow:0 0 4px rgba(138,43,226,.18);}
  50%{box-shadow:0 0 18px rgba(138,43,226,.45);}
}
@keyframes scanline {
  0%{transform:translateY(-100%);opacity:.5;}
  100%{transform:translateY(110vh);opacity:0;}
}
@keyframes fadeUp {
  from{opacity:0;transform:translateY(16px);}
  to{opacity:1;transform:translateY(0);}
}
@keyframes msgSlide {
  from{opacity:0;transform:translateX(-12px);}
  to{opacity:1;transform:translateX(0);}
}
@keyframes spin{to{transform:rotate(360deg);}}
@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.35);}}
@keyframes winFlash{0%,100%{opacity:1;}50%{opacity:.5;}}
@keyframes barFill{from{width:0;}to{width:100%;}}
@keyframes borderBreath{0%,100%{border-color:rgba(138,43,226,.25);}50%{border-color:rgba(138,43,226,.6);}}

/* ── Base ── */
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{
  font-family:'Inter',sans-serif;
  background:#080810 !important;
  color:#e8e4f0;
  line-height:1.6;
}
.stApp{background:#080810 !important;}
.block-container{padding:.8rem 1.6rem 2rem !important;max-width:100% !important;}
header[data-testid="stHeader"]{background:#080810 !important;border-bottom:1px solid rgba(138,43,226,.15);}
.stDeployButton,footer{display:none !important;}

/* ── Animated background orbs ── */
body::before{
  content:'';
  position:fixed;top:0;left:0;width:100%;height:100%;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(138,43,226,.09) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 80%, rgba(65,105,225,.09) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 50%, rgba(138,43,226,.04) 0%, transparent 70%);
  pointer-events:none;z-index:0;animation:orbFloat 18s ease-in-out infinite;
}

/* Scanline */
body::after{
  content:'';position:fixed;top:0;left:0;right:0;height:2px;
  background:linear-gradient(transparent,rgba(138,43,226,.2),transparent);
  animation:scanline 9s linear infinite;pointer-events:none;z-index:9999;
}

/* ── Header ── */
.app-header{
  text-align:center;padding:.6rem 0 .5rem;
  border-bottom:1px solid rgba(138,43,226,.12);margin-bottom:1.1rem;
  animation:fadeUp .5s ease both;
}
.app-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(1.6rem,3.8vw,2.8rem);font-weight:800;
  background:linear-gradient(90deg,#8a2be2,#4169e1,#00d4ff,#8a2be2);
  background-size:300% 100%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation:titleShine 4s ease-in-out infinite;margin:0;letter-spacing:-.01em;
}
.app-sub{
  font-family:'JetBrains Mono',monospace;font-size:.68rem;
  color:rgba(138,43,226,.5);letter-spacing:.3em;text-transform:uppercase;margin-top:5px;
}

/* ── HUD strip ── */
.hud-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:10px;
  margin-bottom:12px;animation:fadeUp .4s ease .1s both;
}
.hud-card{
  background:rgba(255,255,255,.03);
  border:1px solid rgba(138,43,226,.2);border-radius:10px;
  padding:12px 16px;position:relative;overflow:hidden;
  animation:borderBreath 5s ease-in-out infinite;transition:border-color .3s;
}
.hud-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(138,43,226,.4),rgba(65,105,225,.4),transparent);
}
.hc-label{
  font-family:'JetBrains Mono',monospace;font-size:.58rem;
  letter-spacing:.26em;text-transform:uppercase;
  color:rgba(138,43,226,.45);margin-bottom:5px;
}
.hc-val{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#8a60e8;}
.hc-white{color:#e8e4ff;} .hc-black{color:#7870ff;}

/* ── Badges ── */
.badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:3px 12px;border-radius:20px;
  font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.06em;
}
.b-ready{background:rgba(65,105,225,.08);border:1px solid rgba(65,105,225,.3);color:#6888e8;}
.b-think{background:rgba(80,200,80,.07);border:1px solid rgba(80,200,80,.3);
         color:#60d060;animation:borderBreath 1s infinite;}
.b-over {background:rgba(220,50,50,.07);border:1px solid rgba(220,50,50,.3);
         color:#e04848;animation:winFlash 1.4s infinite;}
.spin{display:inline-block;width:8px;height:8px;border:2px solid rgba(80,200,80,.3);
      border-top-color:#60d060;border-radius:50%;animation:spin .7s linear infinite;}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;
     background:#6888e8;animation:pulse 1.8s ease infinite;}

/* ── Board wrapper ── */
.board-wrap{
  background:rgba(138,43,226,.03);
  border:1px solid rgba(138,43,226,.2);border-radius:12px;
  padding:14px 14px 10px;position:relative;overflow:hidden;
  animation:fadeUp .6s cubic-bezier(.2,.8,.2,1) both;
}
.board-wrap::before{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(138,43,226,.07),transparent 55%);
  pointer-events:none;
}

/* ── Last move bar ── */
.lm-bar{
  display:flex;align-items:center;justify-content:center;gap:8px;
  padding:5px 14px;margin-top:8px;
  background:rgba(255,255,255,.02);border:1px solid rgba(65,105,225,.15);
  border-radius:6px;font-family:'JetBrains Mono',monospace;
  font-size:.7rem;color:rgba(65,105,225,.4);letter-spacing:.12em;
}
.lm-sq{color:#5878e8;font-weight:600;}

/* ── Chat panel ── */
.chat-wrap{
  background:rgba(255,255,255,.02);border:1px solid rgba(138,43,226,.18);
  border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
  animation:fadeUp .5s ease .2s both;
}
.chat-header{
  background:linear-gradient(90deg,rgba(138,43,226,.1),rgba(65,105,225,.08));
  border-bottom:1px solid rgba(138,43,226,.18);
  padding:11px 16px;display:flex;align-items:center;
  justify-content:space-between;flex-shrink:0;
}
.chat-title{
  font-family:'Space Grotesk',sans-serif;font-size:.68rem;
  font-weight:600;letter-spacing:.18em;color:#8a2be2;text-transform:uppercase;
}
.chat-badge{
  font-family:'JetBrains Mono',monospace;font-size:.58rem;
  color:rgba(138,43,226,.35);background:rgba(138,43,226,.06);
  border:1px solid rgba(138,43,226,.15);border-radius:12px;padding:2px 9px;
}
.chat-body{
  overflow-y:auto;padding:10px 12px;max-height:490px;
  scroll-behavior:smooth;flex:1;
}
.chat-body::-webkit-scrollbar{width:3px;}
.chat-body::-webkit-scrollbar-track{background:transparent;}
.chat-body::-webkit-scrollbar-thumb{background:rgba(138,43,226,.25);border-radius:2px;}

.chat-msg{
  padding:7px 10px;margin-bottom:5px;border-radius:6px;
  background:rgba(255,255,255,.015);border-left:2px solid rgba(138,43,226,.15);
  line-height:1.45;font-size:.84rem;animation:msgSlide .2s ease both;
  transition:background .2s;
}
.chat-msg:hover{background:rgba(138,43,226,.06);}
.m-system{border-left-color:#d49820;}
.m-queen {border-left-color:#38aadd;}
.m-king  {border-left-color:#9060d8;}
.m-knight{border-left-color:#28c878;}
.m-bishop{border-left-color:#e07028;}
.m-rook  {border-left-color:#3868d8;}
.m-pawn  {border-left-color:#556677;}
.s-system{color:#d4a020;font-family:'JetBrains Mono',monospace;font-size:.78rem;}
.s-queen {color:#38aadd;font-weight:700;}
.s-king  {color:#9060d8;font-weight:700;}
.s-knight{color:#28c878;font-weight:600;}
.s-bishop{color:#e07028;font-weight:600;}
.s-rook  {color:#4888e0;font-weight:600;}
.s-pawn  {color:#788898;}
.m-body  {color:#8898b0;}
.m-ts    {float:right;font-family:'JetBrains Mono',monospace;font-size:.6rem;
          color:rgba(138,43,226,.2);margin-left:8px;}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:rgba(8,8,16,.96) !important;
  border-right:1px solid rgba(138,43,226,.1) !important;
}
[data-testid="stSidebar"] label{color:rgba(138,43,226,.55) !important;font-size:.82rem;}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3{
  font-family:'Space Grotesk',sans-serif;color:rgba(138,43,226,.7);
  font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;
}
[data-testid="stSidebar"] hr{border-color:rgba(138,43,226,.1) !important;}
[data-testid="stMetricValue"]{
  font-family:'Space Grotesk',sans-serif !important;
  color:#8a2be2 !important;font-size:1.1rem !important;
}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,rgba(138,43,226,.12),rgba(65,105,225,.12)) !important;
  border:1px solid rgba(138,43,226,.3) !important;
  color:#9060e8 !important;
  font-family:'Space Grotesk',sans-serif !important;
  font-weight:600 !important;font-size:.75rem !important;
  letter-spacing:.08em !important;text-transform:uppercase !important;
  border-radius:50px !important;padding:8px 22px !important;
  transition:all .25s ease !important;position:relative !important;overflow:hidden !important;
}
.stButton>button:hover{
  background:linear-gradient(135deg,rgba(138,43,226,.25),rgba(65,105,225,.25)) !important;
  border-color:rgba(138,43,226,.6) !important;
  color:#c090ff !important;
  box-shadow:0 8px 28px rgba(138,43,226,.28) !important;
  transform:translateY(-2px) !important;
}

/* ── Material bars ── */
.mat-row{
  display:flex;align-items:center;gap:8px;padding:7px 10px;margin-bottom:5px;
  background:rgba(255,255,255,.025);border:1px solid rgba(138,43,226,.12);
  border-radius:7px;
}
.mat-icon{font-size:.95rem;width:20px;text-align:center;}
.mat-name{font-family:'JetBrains Mono',monospace;font-size:.68rem;
          color:rgba(138,43,226,.4);width:40px;}
.mat-track{flex:1;height:5px;background:rgba(255,255,255,.05);border-radius:3px;overflow:hidden;}
.mat-fw{height:100%;background:linear-gradient(90deg,#8a2be2,#4169e1);
        border-radius:3px;animation:barFill .9s ease both;}
.mat-fb{height:100%;background:linear-gradient(90deg,#4169e1,#00d4ff);
        border-radius:3px;animation:barFill .9s ease both;}
.mat-num{font-family:'Space Grotesk',monospace;font-size:.8rem;color:#8a60e8;min-width:22px;text-align:right;}
.mat-adv{text-align:center;font-family:'JetBrains Mono',monospace;font-size:.66rem;margin-top:2px;}

/* ── Captured ── */
.cap-label{font-family:'JetBrains Mono',monospace;font-size:.58rem;
           color:rgba(138,43,226,.3);letter-spacing:.2em;text-transform:uppercase;margin-bottom:2px;}
.cap-pieces{font-size:1.1rem;letter-spacing:.04em;color:rgba(138,43,226,.6);min-height:24px;}
.cap-empty{color:rgba(138,43,226,.2);font-style:italic;font-size:.7rem;font-family:'JetBrains Mono',monospace;}

/* ── IQ table ── */
.iq-tbl{width:100%;border-collapse:collapse;}
.iq-tbl td{padding:5px 8px;font-family:'JetBrains Mono',monospace;font-size:.68rem;
           border-bottom:1px solid rgba(138,43,226,.08);color:rgba(138,43,226,.35);}
.iq-tbl tr:hover td{background:rgba(138,43,226,.05);}
.iq-p{font-size:.95rem;width:22px;}

/* ── Emotion grid ── */
.emo-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;padding:6px;}
.emo-cell{
  background:rgba(138,43,226,.04);border:1px solid rgba(138,43,226,.12);
  border-radius:6px;padding:5px 4px;text-align:center;font-size:.66rem;
  color:rgba(138,43,226,.35);font-family:'JetBrains Mono',monospace;
  transition:all .2s;
}
.emo-cell:hover{border-color:rgba(138,43,226,.45);color:#9060e8;}

/* ── Game over ── */
.game-over{
  background:linear-gradient(135deg,rgba(138,43,226,.06),rgba(65,105,225,.06));
  border:1px solid rgba(138,43,226,.35);border-radius:12px;
  padding:22px 28px;text-align:center;margin-bottom:14px;
  animation:borderBreath 1.5s infinite;position:relative;overflow:hidden;
}
.game-over::before{
  content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;
  background:radial-gradient(ellipse,rgba(138,43,226,.06) 0%,transparent 60%);
  pointer-events:none;
}
.go-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(1.3rem,3vw,1.9rem);font-weight:800;
  letter-spacing:.12em;animation:winFlash 1.8s ease infinite;margin-bottom:6px;
}
.go-reason{font-size:.95rem;color:rgba(138,43,226,.4);letter-spacing:.06em;}

/* ── Expander ── */
[data-testid="stExpander"]{
  background:rgba(138,43,226,.03) !important;
  border:1px solid rgba(138,43,226,.12) !important;border-radius:8px !important;
}
[data-testid="stExpander"] summary{
  font-family:'Space Grotesk',sans-serif !important;
  font-size:.7rem !important;color:rgba(138,43,226,.5) !important;
  letter-spacing:.1em !important;
}

/* ── Divider ── */
.neo-hr{border:none;height:1px;
        background:linear-gradient(90deg,transparent,rgba(138,43,226,.2),transparent);
        margin:10px 0;}

/* ── Slider / Toggle ── */
[data-baseweb="slider"] [role="slider"]{background:#8a2be2 !important;}
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# HTML BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _scls(sender: str) -> str:
    s = sender.lower()
    for k in ("queen","king","knight","bishop","rook","pawn","system"):
        if k in s: return k
    return "system"


def html_header() -> str:
    return """
<div class="app-header">
  <div class="app-title">β-bot Chess AI</div>
  <div class="app-sub">Multi-Agent · Hierarchical Decision System · Neural Chess</div>
</div>
"""


def html_hud(player: str, move_count: int, ai_thinking: bool, game_over: bool) -> str:
    sym = "♔" if player=="white" else "♚"
    cls = "hc-white" if player=="white" else "hc-black"
    turn = f'<span class="{cls}">{sym} {player.upper()}</span>'
    if ai_thinking:
        status = '<span class="badge b-think"><span class="spin"></span>COMPUTING</span>'
    elif game_over:
        status = '<span class="badge b-over">■ GAME OVER</span>'
    else:
        status = '<span class="badge b-ready"><span class="dot"></span>STANDBY</span>'
    return f"""
<div class="hud-grid">
  <div class="hud-card">
    <div class="hc-label">Active Player</div>
    <div class="hc-val">{turn}</div>
  </div>
  <div class="hud-card">
    <div class="hc-label">Move Counter</div>
    <div class="hc-val" style="color:#5878e8">#{move_count:04d}</div>
  </div>
  <div class="hud-card">
    <div class="hc-label">Engine Status</div>
    <div class="hc-val">{status}</div>
  </div>
</div>
"""


def html_material(w_mat: int, b_mat: int) -> str:
    total = max(w_mat+b_mat, 1)
    wp = max(5, int(w_mat/total*100)); bp = max(5, int(b_mat/total*100))
    diff = w_mat-b_mat
    ac, at = ("#8a2be2",f"+{diff} WHITE") if diff>0 else (("#4169e1",f"{diff} BLACK") if diff<0 else ("#556677","EQUAL"))
    return f"""
<div style="padding:4px 0">
  <div class="mat-row">
    <span class="mat-icon" style="color:#c8c0ff">♔</span>
    <span class="mat-name">WHITE</span>
    <div class="mat-track"><div class="mat-fw" style="width:{wp}%"></div></div>
    <span class="mat-num">{w_mat}</span>
  </div>
  <div class="mat-row">
    <span class="mat-icon" style="color:#7870ff">♚</span>
    <span class="mat-name">BLACK</span>
    <div class="mat-track"><div class="mat-fb" style="width:{bp}%"></div></div>
    <span class="mat-num">{b_mat}</span>
  </div>
  <div class="mat-adv" style="color:{ac}">ADVANTAGE {at}</div>
</div>
"""


def html_captured(w_caps: List, b_caps: List) -> str:
    D = {"king":"♚","queen":"♛","rook":"♜","bishop":"♝","knight":"♞","pawn":"♟"}
    def row(caps, label):
        if caps:
            g = " ".join(D.get(p.piece_type,"?") for p in caps)
            inner = f'<div class="cap-pieces">{g}</div>'
        else:
            inner = '<div class="cap-empty">none captured</div>'
        return f'<div style="margin-bottom:6px"><div class="cap-label">{label}</div>{inner}</div>'
    return f'<div style="padding:4px 0 8px">{row(w_caps,"Captured by White")}{row(b_caps,"Captured by Black")}</div>'


def html_chat(chat_history: List[Dict]) -> str:
    count = len(chat_history)
    rows = []
    for msg in chat_history[-60:]:
        sender  = msg.get("sender","?")
        content = msg.get("content","").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        emotion = msg.get("emotion","NEUTRAL")
        emoji   = EMOTION_EMOJI.get(emotion,"😐")
        cls     = _scls(sender)
        ts      = msg.get("timestamp")
        ts_s    = ts.strftime("%H:%M:%S") if ts else ""
        rows.append(
            f'<div class="chat-msg m-{cls}">'
            f'<span class="m-ts">{ts_s}</span>'
            f'<span class="s-{cls}">{sender}</span> '
            f'{emoji} <span class="m-body">{content}</span>'
            f'</div>'
        )
    inner = "\n".join(rows) if rows else (
        '<div style="color:rgba(138,43,226,.2);font-family:\'JetBrains Mono\',monospace;'
        'font-size:.7rem;padding:28px;text-align:center;letter-spacing:.15em;">'
        '— AWAITING TRANSMISSIONS —</div>'
    )
    return f"""
<div class="chat-wrap">
  <div class="chat-header">
    <span class="chat-title">◈ Piece Communications</span>
    <span class="chat-badge">LOG {count:05d}</span>
  </div>
  <div class="chat-body" id="chatbox">{inner}</div>
</div>
<script>(function(){{var c=document.getElementById('chatbox');if(c)c.scrollTop=c.scrollHeight;}})();</script>
"""


def html_last_move(lm) -> str:
    if not lm:
        return '<div class="lm-bar">NO MOVES YET</div>'
    (fr,fc),(tr,tc) = lm
    fsq = "abcdefgh"[fc]+"87654321"[fr]
    tsq = "abcdefgh"[tc]+"87654321"[tr]
    return (f'<div class="lm-bar">LAST MOVE &nbsp;'
            f'<span class="lm-sq">{fsq}</span>&nbsp;→&nbsp;<span class="lm-sq">{tsq}</span></div>')


def html_game_over(winner: str, reason: str) -> str:
    if winner=="draw":   title,col="◈  DRAW  ◈","#9060e8"
    elif winner=="white": title,col="♔  WHITE WINS  ♔","#e0d4ff"
    else:                 title,col="♚  BLACK WINS  ♚","#7060ff"
    return f"""
<div class="game-over">
  <div class="go-title" style="color:{col}">{title}</div>
  <div class="go-reason">{reason}</div>
</div>
"""


def html_iq_table() -> str:
    rows_data = [
        ("♛","QUEEN","9.0–9.99","Strategic Synthesiser","#38aadd"),
        ("♚","KING", "8.0–8.99","Executive Validator",  "#9060d8"),
        ("♞","KNIGHT","7.0–7.99","Tactical Specialist",  "#28c878"),
        ("♝","BISHOP","6.0–6.99","Positional Analyst",   "#e07028"),
        ("♜","ROOK",  "5.0–5.99","Structural Coord.",    "#4888e0"),
        ("♟","PAWN",  "1.0–4.99","Frontline Scout",      "#778899"),
    ]
    trs="".join(
        f'<tr><td class="iq-p" style="color:{col}">{sym}</td>'
        f'<td style="color:{col};font-weight:700">{name}</td>'
        f'<td style="color:rgba(138,43,226,.3)">{iq}</td>'
        f'<td style="color:rgba(138,43,226,.2);font-size:.62rem">{role}</td></tr>'
        for sym,name,iq,role,col in rows_data
    )
    return f'<table class="iq-tbl">{trs}</table>'


def html_emotion_grid() -> str:
    cells="".join(
        f'<div class="emo-cell">{emoji}<br>{emo.title()}</div>'
        for emo,emoji in EMOTION_EMOJI.items()
    )
    return f'<div class="emo-grid">{cells}</div>'