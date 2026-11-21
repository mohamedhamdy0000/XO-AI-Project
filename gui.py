"""
gui.py
Modern High-End UI/UX for XO (Tic-Tac-Toe) using Tkinter.
Color Palette:
- Primary: Vibrant Crimson / Scarlet Red (#dc2626 / #ef4444 / #ff4d4d)
- Secondary / Canvas: Deep Obsidian Black & Slate (#0c0c0f / #131317 / #1a1a22)
- High-Contrast Typography: Pure White (#ffffff), High-Contrast Silver (#e2e8f0), Electric Cyan (#38bdf8)
- Every single text label and control is rendered with BOLD weight for crystal-clear readability.
"""

import threading
import tkinter as tk
from tkinter import font as tkfont, messagebox
from game_logic import AI, EMPTY, HUMAN, Board
from ai import XOAI
from voice_engine import AIVoiceEngine, TTS_AVAILABLE

try:
    from camera_controller import CV_AVAILABLE, CameraGestureController
except ImportError:
    CV_AVAILABLE = False
    CameraGestureController = None


# =============================================================================
# THEME PALETTE CONSTANTS (Red & Black Cyber-Modern Aesthetic)
# =============================================================================
COLOR_BG_ROOT = "#0c0c0f"        # Deep obsidian black root background
COLOR_BG_HEADER = "#101015"      # Dark header bar
COLOR_BG_CARD = "#141419"        # Elevated card surface
COLOR_BG_CARD_INNER = "#1a1a22"  # Sub-container / wells
COLOR_BORDER = "#252530"         # Sleek subtle border
COLOR_BORDER_RED = "#7f1d1d"     # Dark crimson border highlight

COLOR_RED_PRIMARY = "#dc2626"    # Vibrant primary red
COLOR_RED_HOVER = "#ef4444"      # Hover red
COLOR_RED_ACTIVE = "#b91c1c"     # Pressed red
COLOR_RED_GLOW = "#450a0a"       # Ambient red background glow
COLOR_RED_TEXT = "#ff4d4d"       # Vivid solid red text
COLOR_RED_LIGHT = "#fca5a5"      # Bright coral text

COLOR_TEXT_WHITE = "#ffffff"     # Solid pure white
COLOR_TEXT_BRIGHT = "#f8fafc"    # Bright crisp off-white
COLOR_TEXT_SILVER = "#e2e8f0"    # Bright high-contrast silver
COLOR_TEXT_MUTED = "#a1a1aa"     # Solid readable gray (not faint)
COLOR_CYAN = "#38bdf8"           # Accent Ice Cyan for AI marks and latency

# Cell pieces
COLOR_MARK_X = "#ff3344"         # Human (X) is Flaming Neon Red
COLOR_MARK_O = "#38bdf8"         # AI (O) is Electric Ice Cyan
COLOR_CELL_BG = "#181820"        # Default empty cell background
COLOR_CELL_HOVER = "#272736"     # Hover effect on empty cell
COLOR_WIN_BG = "#7f1d1d"         # Winning cell background (Crimson victory glow)
COLOR_WIN_BORDER = "#ef4444"     # Winning cell border


class TicTacToeGUI:
    """Modern Red & Black Graphical User Interface with Crystal-Clear Bold Typography."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("XO AI // Minimax & Alpha-Beta Intelligence Engine")
        self.root.geometry("980x670")
        self.root.minsize(940, 640)
        self.root.configure(bg=COLOR_BG_ROOT)

        # Core Game State
        self.board = Board()
        self.ai = XOAI()
        self.current_turn = HUMAN
        self.game_over = False
        self.winning_line = None

        # Camera Mode State
        self.camera_controller = None
        self.camera_active = False

        # Voice Trash-Talk Engine
        self.voice_engine = AIVoiceEngine(enabled=True)
        self.voice_enabled = True

        # Cumulative Scoreboard
        self.score_human = 0
        self.score_ai = 0
        self.score_draw = 0

        # Settings Variables
        self.first_player_var = tk.StringVar(value="Human")
        self.algo_var = tk.StringVar(value="Alpha-Beta")
        self.level_var = tk.StringVar(value="Hard")

        # Telemetry Variables
        self.last_move_str = tk.StringVar(value="--")
        self.nodes_visited_str = tk.StringVar(value="0")
        self.time_taken_str = tk.StringVar(value="0.0 ms")
        self.status_text_var = tk.StringVar(value="⚔️ Your Turn (X) - Select an empty cell")
        self.speech_bubble_var = tk.StringVar(value="جاهز للمعركة يا بطل!")

        self._init_fonts()
        self._build_layout()
        self.start_new_game()

    def _init_fonts(self):
        """Initializes ultra-clear bold typography across all components."""
        self.brand_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.brand_sub_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.section_header_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.section_tag_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.bold_label_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.speech_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.mark_font = tkfont.Font(family="Segoe UI", size=38, weight="bold")
        self.index_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.status_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.stat_val_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.score_val_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.tip_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")

    # =========================================================================
    # UI CONSTRUCTION
    # =========================================================================
    def _build_layout(self):
        # 1. Top Sleek Header Bar
        self._build_header()

        # 2. Main 3-Column Content Layout
        content = tk.Frame(self.root, bg=COLOR_BG_ROOT)
        content.pack(fill="both", expand=True, padx=16, pady=(10, 14))
        content.columnconfigure(0, weight=1)  # Left Settings
        content.columnconfigure(1, weight=2)  # Center Board
        content.columnconfigure(2, weight=1)  # Right Telemetry
        content.rowconfigure(0, weight=1)

        # Build Columns
        self._build_left_panel(content)
        self._build_center_panel(content)
        self._build_right_panel(content)

    def _build_header(self):
        """Builds a luxury dark header with red accent bottom line."""
        header_container = tk.Frame(self.root, bg=COLOR_BG_HEADER)
        header_container.pack(fill="x", side="top")

        header_content = tk.Frame(header_container, bg=COLOR_BG_HEADER, height=54)
        header_content.pack(fill="x", padx=18, pady=8)

        # Brand / Title
        left_brand = tk.Frame(header_content, bg=COLOR_BG_HEADER)
        left_brand.pack(side="left")

        # Red Icon Badge
        badge = tk.Label(
            left_brand,
            text=" ⬡ ",
            font=self.brand_font,
            fg=COLOR_RED_PRIMARY,
            bg=COLOR_BG_HEADER
        )
        badge.pack(side="left")

        title_frame = tk.Frame(left_brand, bg=COLOR_BG_HEADER)
        title_frame.pack(side="left", padx=4)

        title_lbl = tk.Label(
            title_frame,
            text="XO AI // INTELLIGENCE ENGINE",
            font=self.brand_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_HEADER
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            title_frame,
            text="MINIMAX & ALPHA-BETA PRUNING  •  ACADEMIC EDITION",
            font=self.brand_sub_font,
            fg=COLOR_RED_TEXT,
            bg=COLOR_BG_HEADER
        )
        sub_lbl.pack(anchor="w")

        # Action Buttons on Right (Voice & Camera)
        right_btns = tk.Frame(header_content, bg=COLOR_BG_HEADER)
        right_btns.pack(side="right")

        # Voice Toggle
        self.voice_btn = tk.Button(
            right_btns,
            text="🔊 AI Voice: ON",
            font=self.bold_label_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_CARD_INNER,
            activebackground=COLOR_RED_GLOW,
            activeforeground=COLOR_TEXT_WHITE,
            relief="flat",
            bd=0,
            highlightbackground=COLOR_BORDER_RED,
            highlightthickness=1,
            cursor="hand2",
            padx=14,
            pady=6,
            command=self._toggle_voice_mode
        )
        self.voice_btn.pack(side="right", padx=(10, 0))

        # Camera Mode Toggle
        self.cam_btn = tk.Button(
            right_btns,
            text="📷 Air-Touch Camera",
            font=self.bold_label_font,
            fg=COLOR_CYAN,
            bg=COLOR_BG_CARD_INNER,
            activebackground=COLOR_BG_CARD,
            activeforeground=COLOR_TEXT_WHITE,
            relief="flat",
            bd=0,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            cursor="hand2",
            padx=14,
            pady=6,
            command=self._toggle_camera_mode
        )
        self.cam_btn.pack(side="right")

        # Bottom 2px Radiant Red Accent Stripe
        accent_stripe = tk.Frame(header_container, bg=COLOR_RED_PRIMARY, height=2)
        accent_stripe.pack(fill="x", side="bottom")

    # ----------------- COLUMN 1: LEFT CONFIGURATION PANEL -----------------
    def _build_left_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=COLOR_BG_CARD,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        # Card Title
        self._create_panel_header(card, "MATCH CONTROLS")

        # 1. Who plays first
        self._create_section_label(card, "FIRST PLAYER")
        f1 = tk.Frame(card, bg=COLOR_BG_CARD_INNER, highlightbackground=COLOR_BORDER, highlightthickness=1)
        f1.pack(fill="x", padx=14, pady=(2, 10))

        rb_h = self._create_radio(f1, "Human Player (X)", self.first_player_var, "Human")
        rb_h.pack(anchor="w", padx=10, pady=(6, 3))
        rb_c = self._create_radio(f1, "Computer AI (O)", self.first_player_var, "Computer")
        rb_c.pack(anchor="w", padx=10, pady=(3, 6))

        # 2. Algorithm
        self._create_section_label(card, "SEARCH ALGORITHM")
        f2 = tk.Frame(card, bg=COLOR_BG_CARD_INNER, highlightbackground=COLOR_BORDER, highlightthickness=1)
        f2.pack(fill="x", padx=14, pady=(2, 10))

        rb_ab = self._create_radio(f2, "Alpha-Beta Pruning (Fast)", self.algo_var, "Alpha-Beta")
        rb_ab.pack(anchor="w", padx=10, pady=(6, 3))
        rb_mini = self._create_radio(f2, "Standard Minimax", self.algo_var, "Minimax")
        rb_mini.pack(anchor="w", padx=10, pady=(3, 6))

        # 3. Difficulty Level
        self._create_section_label(card, "DIFFICULTY LEVEL")
        f3 = tk.Frame(card, bg=COLOR_BG_CARD_INNER, highlightbackground=COLOR_BORDER, highlightthickness=1)
        f3.pack(fill="x", padx=14, pady=(2, 12))

        rb_hard = self._create_radio(f3, "Hard (Unbeatable - Full)", self.level_var, "Hard")
        rb_hard.pack(anchor="w", padx=10, pady=(6, 2))
        rb_med = self._create_radio(f3, "Medium (Heuristic - Depth 2)", self.level_var, "Medium")
        rb_med.pack(anchor="w", padx=10, pady=2)
        rb_easy = self._create_radio(f3, "Easy (Random Moves)", self.level_var, "Easy")
        rb_easy.pack(anchor="w", padx=10, pady=(2, 6))

        # Spacer to push New Game to bottom
        tk.Frame(card, bg=COLOR_BG_CARD).pack(expand=True, fill="both")

        # Action: New Game Button (Radiant Red CTA)
        btn_box = tk.Frame(card, bg=COLOR_BG_CARD)
        btn_box.pack(fill="x", padx=14, pady=(6, 14))

        self.new_game_btn = tk.Button(
            btn_box,
            text="⚡ START NEW GAME",
            font=self.section_header_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_RED_PRIMARY,
            activebackground=COLOR_RED_HOVER,
            activeforeground=COLOR_TEXT_WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=11,
            command=self.start_new_game
        )
        self.new_game_btn.pack(fill="x")
        self._attach_button_hover(self.new_game_btn, COLOR_RED_PRIMARY, COLOR_RED_HOVER)

    # ----------------- COLUMN 2: CENTER BOARD PANEL -----------------
    def _build_center_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=COLOR_BG_CARD,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        card.grid(row=0, column=1, sticky="nsew", padx=8, pady=0)

        # AI Cognitive Speech Box (Futuristic Console)
        speech_outer = tk.Frame(
            card,
            bg=COLOR_BG_CARD_INNER,
            highlightbackground=COLOR_BORDER_RED,
            highlightthickness=1
        )
        speech_outer.pack(fill="x", padx=16, pady=(14, 8))

        speech_hdr = tk.Label(
            speech_outer,
            text="🤖 AI COGNITIVE CONSOLE",
            font=self.section_tag_font,
            fg=COLOR_RED_TEXT,
            bg=COLOR_BG_CARD_INNER
        )
        speech_hdr.pack(anchor="w", padx=12, pady=(7, 2))

        self.speech_bubble_lbl = tk.Label(
            speech_outer,
            textvariable=self.speech_bubble_var,
            font=self.speech_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_CARD_INNER,
            pady=5,
            wraplength=380,
            justify="center"
        )
        self.speech_bubble_lbl.pack(padx=12, pady=(0, 9))

        # 3x3 Board Chassis
        board_container = tk.Frame(card, bg=COLOR_BG_CARD)
        board_container.pack(expand=True, pady=4)

        self.grid_chassis = tk.Frame(
            board_container,
            bg=COLOR_BORDER,
            bd=0,
            padx=2,
            pady=2
        )
        self.grid_chassis.pack()

        self.cell_frames = []
        self.cell_buttons = []
        self.cell_indices = []

        for i in range(9):
            r, c = divmod(i, 3)
            cell_box = tk.Frame(
                self.grid_chassis,
                bg=COLOR_CELL_BG,
                width=100,
                height=100
            )
            cell_box.grid(row=r, column=c, padx=2, pady=2)
            cell_box.pack_propagate(False)

            # Coordinate Index (clearly visible bold number in corner)
            idx_bar = tk.Frame(cell_box, bg=COLOR_CELL_BG)
            idx_bar.pack(fill="x", side="top", padx=6, pady=(3, 0))
            idx_lbl = tk.Label(
                idx_bar,
                text=str(i),
                font=self.index_font,
                fg=COLOR_TEXT_MUTED,
                bg=COLOR_CELL_BG
            )
            idx_lbl.pack(side="right")

            btn = tk.Button(
                cell_box,
                text="",
                font=self.mark_font,
                fg=COLOR_TEXT_WHITE,
                bg=COLOR_CELL_BG,
                activebackground=COLOR_CELL_HOVER,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda idx=i: self._on_cell_clicked(idx)
            )
            btn.pack(fill="both", expand=True)

            # Bind interactive hover highlight
            self._attach_cell_hover(btn, cell_box, idx_bar, idx_lbl, i)

            self.cell_frames.append(cell_box)
            self.cell_buttons.append(btn)
            self.cell_indices.append((idx_bar, idx_lbl))

        # Status Banner Below Board
        self.status_container = tk.Frame(
            card,
            bg=COLOR_BG_CARD_INNER,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.status_container.pack(fill="x", padx=16, pady=(6, 4))

        self.status_lbl = tk.Label(
            self.status_container,
            textvariable=self.status_text_var,
            font=self.status_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_CARD_INNER,
            pady=8
        )
        self.status_lbl.pack()

        sub_hint = tk.Label(
            card,
            text="Tap empty cell to move  •  or toggle Air-Touch Camera",
            font=self.brand_sub_font,
            fg=COLOR_TEXT_SILVER,
            bg=COLOR_BG_CARD
        )
        sub_hint.pack(pady=(0, 10))

    # ----------------- COLUMN 3: RIGHT TELEMETRY PANEL -----------------
    def _build_right_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=COLOR_BG_CARD,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        card.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=0)

        # Card Title
        self._create_panel_header(card, "LIVE AI TELEMETRY")

        # Telemetry Stat Box
        telem_box = tk.Frame(
            card,
            bg=COLOR_BG_CARD_INNER,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        telem_box.pack(fill="x", padx=14, pady=(2, 10))

        # 1. Target Cell (Bold white)
        self._build_metric_row(telem_box, "Target Move:", self.last_move_str, COLOR_TEXT_WHITE)
        # 2. Nodes Explored (Bold Red)
        self._build_metric_row(telem_box, "Nodes Explored:", self.nodes_visited_str, COLOR_RED_TEXT)
        # 3. Latency (Bold Cyan)
        self._build_metric_row(telem_box, "Search Latency:", self.time_taken_str, COLOR_CYAN, is_last=True)

        # Match Scoreboard (Esports Style)
        self._create_section_label(card, "MATCH SCOREBOARD")
        score_container = tk.Frame(
            card,
            bg=COLOR_BG_CARD_INNER,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        score_container.pack(fill="x", padx=14, pady=(2, 10))

        score_grid = tk.Frame(score_container, bg=COLOR_BG_CARD_INNER)
        score_grid.pack(fill="x", padx=8, pady=10)
        score_grid.columnconfigure(0, weight=1)
        score_grid.columnconfigure(1, weight=1)
        score_grid.columnconfigure(2, weight=1)

        # Human Score
        h_box = tk.Frame(score_grid, bg=COLOR_BG_CARD_INNER)
        h_box.grid(row=0, column=0)
        tk.Label(h_box, text="HUMAN (X)", font=self.brand_sub_font, fg=COLOR_RED_TEXT, bg=COLOR_BG_CARD_INNER).pack()
        self.score_h_lbl = tk.Label(h_box, text="0", font=self.score_val_font, fg=COLOR_RED_TEXT, bg=COLOR_BG_CARD_INNER)
        self.score_h_lbl.pack()

        # AI Score
        a_box = tk.Frame(score_grid, bg=COLOR_BG_CARD_INNER)
        a_box.grid(row=0, column=1)
        tk.Label(a_box, text="AI (O)", font=self.brand_sub_font, fg=COLOR_CYAN, bg=COLOR_BG_CARD_INNER).pack()
        self.score_a_lbl = tk.Label(a_box, text="0", font=self.score_val_font, fg=COLOR_CYAN, bg=COLOR_BG_CARD_INNER)
        self.score_a_lbl.pack()

        # Draws Score
        d_box = tk.Frame(score_grid, bg=COLOR_BG_CARD_INNER)
        d_box.grid(row=0, column=2)
        tk.Label(d_box, text="DRAWS", font=self.brand_sub_font, fg=COLOR_TEXT_SILVER, bg=COLOR_BG_CARD_INNER).pack()
        self.score_d_lbl = tk.Label(d_box, text="0", font=self.score_val_font, fg=COLOR_TEXT_WHITE, bg=COLOR_BG_CARD_INNER)
        self.score_d_lbl.pack()

        # Algorithm Analysis Insight Note
        self._create_section_label(card, "PERFORMANCE INSIGHT")
        tip_box = tk.Frame(
            card,
            bg=COLOR_BG_CARD_INNER,
            highlightbackground=COLOR_BORDER_RED,
            highlightthickness=1
        )
        tip_box.pack(fill="x", padx=14, pady=(2, 10))

        tk.Label(
            tip_box,
            text="⚡ Pruning Efficiency",
            font=self.bold_label_font,
            fg=COLOR_RED_LIGHT,
            bg=COLOR_BG_CARD_INNER
        ).pack(anchor="w", padx=10, pady=(8, 3))

        tip_msg = (
            "Alpha-Beta pruning cuts unpromising branches, "
            "evaluating up to 96.2% fewer nodes than standard "
            "Minimax while guaranteeing the mathematically identical "
            "optimal move."
        )
        tk.Label(
            tip_box,
            text=tip_msg,
            font=self.tip_font,
            fg=COLOR_TEXT_BRIGHT,
            bg=COLOR_BG_CARD_INNER,
            justify="left",
            wraplength=210
        ).pack(anchor="w", padx=10, pady=(0, 8))

    # =========================================================================
    # UI HELPER BUILDERS & STYLING
    # =========================================================================
    def _create_panel_header(self, parent, title_text: str):
        """Creates a standardized panel header with red pill accent."""
        hdr_frame = tk.Frame(parent, bg=COLOR_BG_CARD)
        hdr_frame.pack(fill="x", padx=14, pady=(12, 8))

        pill = tk.Frame(hdr_frame, bg=COLOR_RED_PRIMARY, width=3, height=14)
        pill.pack(side="left", fill="y", padx=(0, 6))

        tk.Label(
            hdr_frame,
            text=title_text,
            font=self.section_header_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_CARD
        ).pack(side="left")

    def _create_section_label(self, parent, text: str):
        lbl = tk.Label(
            parent,
            text=text,
            font=self.section_tag_font,
            fg=COLOR_RED_LIGHT,
            bg=COLOR_BG_CARD
        )
        lbl.pack(anchor="w", padx=14, pady=(2, 2))

    def _create_radio(self, parent, text: str, variable: tk.StringVar, value: str) -> tk.Radiobutton:
        return tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            font=self.label_font,
            fg=COLOR_TEXT_WHITE,
            bg=COLOR_BG_CARD_INNER,
            activebackground=COLOR_BG_CARD_INNER,
            activeforeground=COLOR_RED_TEXT,
            selectcolor="#3b080c",
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

    def _build_metric_row(self, parent, label: str, textvariable: tk.StringVar, color: str, is_last: bool = False):
        row = tk.Frame(parent, bg=COLOR_BG_CARD_INNER)
        pad_bottom = 8 if is_last else 3
        pad_top = 8 if not is_last and label == "Target Move:" else 3
        row.pack(fill="x", padx=10, pady=(pad_top, pad_bottom))

        tk.Label(row, text=label, font=self.label_font, fg=COLOR_TEXT_SILVER, bg=COLOR_BG_CARD_INNER).pack(side="left")
        tk.Label(row, textvariable=textvariable, font=self.stat_val_font, fg=color, bg=COLOR_BG_CARD_INNER).pack(side="right")

    def _attach_button_hover(self, btn: tk.Button, normal_bg: str, hover_bg: str):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

    def _attach_cell_hover(self, btn, cell_box, idx_bar, idx_lbl, index: int):
        def _on_enter(e):
            if not self.game_over and self.board.is_empty(index) and self.current_turn == HUMAN:
                cell_box.config(bg=COLOR_CELL_HOVER)
                btn.config(bg=COLOR_CELL_HOVER)
                idx_bar.config(bg=COLOR_CELL_HOVER)
                idx_lbl.config(bg=COLOR_CELL_HOVER, fg=COLOR_TEXT_WHITE)

        def _on_leave(e):
            if not self.game_over and self.board.is_empty(index):
                cell_box.config(bg=COLOR_CELL_BG)
                btn.config(bg=COLOR_CELL_BG)
                idx_bar.config(bg=COLOR_CELL_BG)
                idx_lbl.config(bg=COLOR_CELL_BG, fg=COLOR_TEXT_MUTED)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)

    # =========================================================================
    # CORE GAME FLOW & ACTIONS
    # =========================================================================
    def start_new_game(self):
        """Reset the board and initiate game flow based on settings."""
        self.board.reset()
        self.game_over = False
        self.winning_line = None

        # Reset cell styles and text
        for i in range(9):
            self.cell_buttons[i].config(
                text="",
                state="normal",
                bg=COLOR_CELL_BG,
                activebackground=COLOR_CELL_HOVER
            )
            self.cell_frames[i].config(bg=COLOR_CELL_BG)
            idx_bar, idx_lbl = self.cell_indices[i]
            idx_bar.config(bg=COLOR_CELL_BG)
            idx_lbl.config(bg=COLOR_CELL_BG, fg=COLOR_TEXT_MUTED)

        # Reset Telemetry
        self.last_move_str.set("--")
        self.nodes_visited_str.set("0")
        self.time_taken_str.set("0.0 ms")

        first_player = self.first_player_var.get()
        ai_starts = (first_player == "Computer")

        # Voice Introduction
        self.voice_engine.comment_game_start(ai_starts=ai_starts, on_text_spoken=self._update_speech_bubble)

        if first_player == "Human":
            self.current_turn = HUMAN
            self.status_text_var.set("⚔️ Your Turn (X) - Select an empty cell")
            self._set_status_theme("human")
        else:
            self.current_turn = AI
            self.status_text_var.set("⏳ Computer is calculating optimal move...")
            self._set_status_theme("ai_thinking")
            self.root.after(400, self._perform_ai_move)

    def _on_cell_clicked(self, index: int):
        if self.game_over or self.current_turn != HUMAN:
            return

        if not self.board.is_empty(index):
            return

        # Human places X
        self.board.make_move(index, HUMAN)
        self._update_cell_ui(index, HUMAN)

        if self._check_game_end():
            return

        # Pass turn to AI
        self.current_turn = AI
        self.status_text_var.set("⏳ Computer is calculating optimal move...")
        self._set_status_theme("ai_thinking")
        self._set_board_interactive(False)

        self.root.after(250, self._perform_ai_move)

    def _perform_ai_move(self):
        if self.game_over:
            return

        algo = self.algo_var.get()
        level = self.level_var.get()

        best_move, nodes, time_ms = self.ai.get_best_move(self.board, algorithm=algo, level=level)

        if best_move is not None:
            self.board.make_move(best_move, AI)
            self._update_cell_ui(best_move, AI)

            self.last_move_str.set(f"Cell {best_move}")
            self.nodes_visited_str.set(f"{nodes:,}")
            self.time_taken_str.set(f"{time_ms:.1f} ms" if time_ms > 0 else "< 0.1 ms")

            # Voice commentary
            is_threat = self._ai_has_threat()
            self.voice_engine.comment_ai_move(
                cell_idx=best_move, nodes=nodes, is_threat=is_threat,
                on_text_spoken=self._update_speech_bubble
            )

        if self._check_game_end():
            return

        # Pass turn back to Human
        self.current_turn = HUMAN
        self.status_text_var.set("⚔️ Your Turn (X) - Select an empty cell")
        self._set_status_theme("human")
        self._set_board_interactive(True)

    def _update_cell_ui(self, index: int, player: str):
        color = COLOR_MARK_X if player == HUMAN else COLOR_MARK_O
        self.cell_buttons[index].config(
            text=player,
            fg=color,
            disabledforeground=color,
            state="disabled",
            bg=COLOR_CELL_BG
        )

    def _set_board_interactive(self, enabled: bool):
        if self.game_over:
            return
        for i in range(9):
            if self.board.is_empty(i):
                self.cell_buttons[i].config(state="normal" if enabled else "disabled")

    def _check_game_end(self) -> bool:
        winner, winning_trio = self.board.check_winner()

        if winner is not None:
            self.game_over = True
            self.winning_line = winning_trio
            self._highlight_winner(winning_trio)

            if winner == HUMAN:
                self.status_text_var.set("🏆 VICTORY! You defeated the AI!")
                self._set_status_theme("win_human")
                self.score_human += 1
                self.voice_engine.comment_game_over("Human", on_text_spoken=self._update_speech_bubble)
            else:
                self.status_text_var.set("💀 DEFEAT! Minimax AI wins!")
                self._set_status_theme("win_ai")
                self.score_ai += 1
                self.voice_engine.comment_game_over("AI", on_text_spoken=self._update_speech_bubble)

            self._update_scoreboard()
            self._disable_all_cells()
            return True

        if self.board.is_draw():
            self.game_over = True
            self.status_text_var.set("🤝 STALEMATE! Game is a Draw!")
            self._set_status_theme("draw")
            self.score_draw += 1
            self.voice_engine.comment_game_over("Draw", on_text_spoken=self._update_speech_bubble)
            self._update_scoreboard()
            self._disable_all_cells()
            return True

        return False

    def _highlight_winner(self, trio: tuple):
        for idx in trio:
            self.cell_frames[idx].config(bg=COLOR_WIN_BG)
            self.cell_buttons[idx].config(
                bg=COLOR_WIN_BG,
                activebackground=COLOR_WIN_BG,
                fg=COLOR_TEXT_WHITE,
                disabledforeground=COLOR_TEXT_WHITE
            )
            idx_bar, idx_lbl = self.cell_indices[idx]
            idx_bar.config(bg=COLOR_WIN_BG)
            idx_lbl.config(bg=COLOR_WIN_BG, fg=COLOR_TEXT_WHITE)

    def _disable_all_cells(self):
        for btn in self.cell_buttons:
            btn.config(state="disabled")

    def _update_scoreboard(self):
        self.score_h_lbl.config(text=str(self.score_human))
        self.score_a_lbl.config(text=str(self.score_ai))
        self.score_d_lbl.config(text=str(self.score_draw))

    def _set_status_theme(self, mode: str):
        """Styles the dynamic status banner based on game state."""
        if mode == "human":
            self.status_container.config(highlightbackground=COLOR_BORDER, bg=COLOR_BG_CARD_INNER)
            self.status_lbl.config(fg=COLOR_TEXT_WHITE, bg=COLOR_BG_CARD_INNER)
        elif mode == "ai_thinking":
            self.status_container.config(highlightbackground="#b45309", bg="#2a1705")
            self.status_lbl.config(fg="#f59e0b", bg="#2a1705")
        elif mode == "win_human":
            self.status_container.config(highlightbackground="#15803d", bg="#052e16")
            self.status_lbl.config(fg="#4ade80", bg="#052e16")
        elif mode == "win_ai":
            self.status_container.config(highlightbackground=COLOR_RED_PRIMARY, bg=COLOR_RED_GLOW)
            self.status_lbl.config(fg=COLOR_RED_HOVER, bg=COLOR_RED_GLOW)
        elif mode == "draw":
            self.status_container.config(highlightbackground=COLOR_BORDER, bg=COLOR_BG_CARD_INNER)
            self.status_lbl.config(fg=COLOR_TEXT_WHITE, bg=COLOR_BG_CARD_INNER)

    def _ai_has_threat(self) -> bool:
        from game_logic import WINNING_COMBINATIONS
        for a, b, c in WINNING_COMBINATIONS:
            line = [self.board.cells[a], self.board.cells[b], self.board.cells[c]]
            if line.count(AI) == 2 and line.count(EMPTY) == 1:
                return True
        return False

    # =========================================================================
    # VOICE & CAMERA CONTROLLERS
    # =========================================================================
    def _toggle_voice_mode(self):
        self.voice_enabled = not self.voice_enabled
        self.voice_engine.enabled = self.voice_enabled
        if self.voice_enabled:
            self.voice_btn.config(text="🔊 AI Voice: ON", fg=COLOR_TEXT_WHITE, bg=COLOR_BG_CARD_INNER)
        else:
            self.voice_btn.config(text="🔇 AI Voice: OFF", fg=COLOR_TEXT_MUTED, bg=COLOR_BG_CARD_INNER)

    def _update_speech_bubble(self, spoken_text: str):
        self.root.after(0, lambda: self.speech_bubble_var.set(spoken_text))

    def _toggle_camera_mode(self):
        if not CV_AVAILABLE or CameraGestureController is None:
            messagebox.showinfo(
                "Camera Mode Info",
                "OpenCV & MediaPipe are required for Camera Mode."
            )
            return

        if self.camera_active:
            if self.camera_controller:
                self.camera_controller.is_running = False
            self.camera_active = False
            self.cam_btn.config(text="📷 Air-Touch Camera", fg=COLOR_CYAN, bg=COLOR_BG_CARD_INNER)
        else:
            try:
                self.camera_active = True
                self.cam_btn.config(text="🛑 Stop Camera", fg=COLOR_TEXT_WHITE, bg=COLOR_RED_PRIMARY)
                self.camera_controller = CameraGestureController(
                    board=self.board,
                    on_move_callback=self._on_camera_move_selected
                )
                threading.Thread(
                    target=self.camera_controller.start_camera_loop,
                    args=(self._on_camera_closed,),
                    daemon=True
                ).start()
            except Exception as e:
                self.camera_active = False
                self.cam_btn.config(text="📷 Air-Touch Camera", fg=COLOR_CYAN, bg=COLOR_BG_CARD_INNER)
                messagebox.showerror("Camera Error", f"Could not start camera:\n{e}")

    def _on_camera_move_selected(self, cell_idx: int):
        self.root.after(0, lambda: self._on_cell_clicked(cell_idx))

    def _on_camera_closed(self):
        self.camera_active = False
        self.root.after(0, lambda: self.cam_btn.config(text="📷 Air-Touch Camera", fg=COLOR_CYAN, bg=COLOR_BG_CARD_INNER))
