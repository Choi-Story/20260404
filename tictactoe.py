import tkinter as tk
from tkinter import messagebox
import random
import math

# ────────────────────────────── 색상 팔레트 ──────────────────────────────
BG        = "#0D0D0D"
PANEL     = "#141414"
GRID_BG   = "#1A1A1A"
CELL_BG   = "#1E1E1E"
CELL_HOV  = "#252525"
X_COLOR   = "#FF3B5C"   # 빨강
O_COLOR   = "#00C6FF"   # 하늘색
TIE_COLOR = "#888888"
BTN_ACT   = "#222222"
BTN_HOV   = "#2A2A2A"
TEXT_PRI  = "#FFFFFF"
TEXT_SEC  = "#666666"
ACCENT    = "#FF3B5C"

FONT_TITLE  = ("Courier New", 26, "bold")
FONT_STATUS = ("Courier New", 13, "bold")
FONT_BTN    = ("Courier New", 11, "bold")
FONT_CELL   = ("Courier New", 42, "bold")
FONT_SCORE  = ("Courier New", 10)
FONT_SCORE2 = ("Courier New", 14, "bold")


# ──────────────────────────────── Minimax AI ─────────────────────────────
def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner_board(board)
    if winner == "O":   return 10 - depth
    if winner == "X":   return depth - 10
    if "" not in board: return 0

    if is_maximizing:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                best = max(best, minimax(board, depth + 1, False, alpha, beta))
                board[i] = ""
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                best = min(best, minimax(board, depth + 1, True, alpha, beta))
                board[i] = ""
                beta = min(beta, best)
                if beta <= alpha: break
        return best


def best_ai_move(board):
    best_val, best_idx = -math.inf, -1
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            val = minimax(board, 0, False, -math.inf, math.inf)
            board[i] = ""
            if val > best_val:
                best_val, best_idx = val, i
    return best_idx


def check_winner_board(board):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


# ──────────────────────────────── 메인 앱 ────────────────────────────────
class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("TIC · TAC · TOE")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.mode        = tk.StringVar(value="2P")   # "2P" | "AI"
        self.board       = [""] * 9
        self.current     = "X"
        self.game_active = False
        self.scores      = {"X": 0, "O": 0, "TIE": 0}
        self.buttons     = []
        self.win_line    = []

        self._build_ui()
        self._start_game()

    # ─────────────────── UI 구성 ───────────────────
    def _build_ui(self):
        root = self.root

        # ── 타이틀 ──
        tk.Label(root, text="TIC · TAC · TOE", font=FONT_TITLE,
                 fg=TEXT_PRI, bg=BG).pack(pady=(22, 4))
        tk.Label(root, text="STRATEGY BOARD GAME", font=("Courier New", 9),
                 fg=TEXT_SEC, bg=BG).pack(pady=(0, 14))

        # ── 모드 선택 ──
        mode_frame = tk.Frame(root, bg=BG)
        mode_frame.pack(pady=(0, 14))

        for label, val in [("👥  2 PLAYER", "2P"), ("🤖  vs AI", "AI")]:
            rb = tk.Radiobutton(
                mode_frame, text=label, variable=self.mode, value=val,
                font=FONT_BTN, fg=TEXT_PRI, bg=BTN_ACT,
                selectcolor="#333333", activebackground=BTN_HOV,
                activeforeground=TEXT_PRI, relief="flat", padx=16, pady=8,
                command=self._mode_changed, indicatoron=False,
                bd=0, cursor="hand2"
            )
            rb.pack(side="left", padx=6)

        # ── 상태 표시 ──
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(root, textvariable=self.status_var,
                                   font=FONT_STATUS, fg=X_COLOR, bg=BG)
        self.status_lbl.pack(pady=(0, 12))

        # ── 게임 보드 ──
        board_outer = tk.Frame(root, bg="#333333", padx=2, pady=2)
        board_outer.pack(padx=28)

        board_frame = tk.Frame(board_outer, bg=GRID_BG)
        board_frame.pack()

        self.buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            cell = tk.Canvas(board_frame, width=110, height=110,
                             bg=CELL_BG, highlightthickness=0, cursor="hand2")
            cell.grid(row=row, column=col, padx=2, pady=2)
            cell.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
            cell.bind("<Enter>",    lambda e, c=cell: self._cell_hover(c, True))
            cell.bind("<Leave>",    lambda e, c=cell: self._cell_hover(c, False))
            self.buttons.append(cell)

        # ── 점수판 ──
        score_frame = tk.Frame(root, bg=PANEL, pady=12)
        score_frame.pack(fill="x", padx=28, pady=(14, 0))

        self.score_labels = {}
        for sym, label, color in [("X", "PLAYER X", X_COLOR),
                                    ("TIE", "DRAW", TEXT_SEC),
                                    ("O", "PLAYER O", O_COLOR)]:
            col_f = tk.Frame(score_frame, bg=PANEL)
            col_f.pack(side="left", expand=True)
            tk.Label(col_f, text=label, font=FONT_SCORE,
                     fg=TEXT_SEC, bg=PANEL).pack()
            lbl = tk.Label(col_f, text="0", font=FONT_SCORE2,
                           fg=color, bg=PANEL)
            lbl.pack()
            self.score_labels[sym] = lbl

        # ── 버튼 ──
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(pady=16)

        def make_btn(parent, text, cmd):
            b = tk.Button(parent, text=text, font=FONT_BTN,
                          fg=TEXT_PRI, bg=BTN_ACT, activebackground=BTN_HOV,
                          activeforeground=TEXT_PRI, relief="flat",
                          padx=20, pady=8, cursor="hand2", bd=0,
                          command=cmd)
            b.pack(side="left", padx=6)
            return b

        make_btn(btn_frame, "🔄  NEW GAME", self._start_game)
        make_btn(btn_frame, "🗑  RESET ALL", self._reset_all)

        root.update_idletasks()
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()
        root.geometry(f"{w}x{h}+{(root.winfo_screenwidth()-w)//2}+"
                      f"{(root.winfo_screenheight()-h)//2}")

    # ─────────────────── 셀 호버 ───────────────────
    def _cell_hover(self, cell, enter):
        if not self.game_active: return
        idx = self.buttons.index(cell)
        if self.board[idx]: return
        cell.configure(bg=CELL_HOV if enter else CELL_BG)

    # ─────────────────── 모드 변경 ───────────────────
    def _mode_changed(self):
        self._update_score_labels()
        self._start_game()

    def _update_score_labels(self):
        is_ai = self.mode.get() == "AI"
        self.score_labels["X"].master.children["!label"].config(
            text="PLAYER" if is_ai else "PLAYER X")
        self.score_labels["O"].master.children["!label"].config(
            text="AI" if is_ai else "PLAYER O")

    # ─────────────────── 게임 시작 ───────────────────
    def _start_game(self):
        self.board       = [""] * 9
        self.current     = "X"
        self.game_active = True
        self.win_line    = []

        for cell in self.buttons:
            cell.delete("all")
            cell.configure(bg=CELL_BG)

        self._set_status()

    def _reset_all(self):
        self.scores = {"X": 0, "O": 0, "TIE": 0}
        for k, lbl in self.score_labels.items():
            lbl.config(text="0")
        self._start_game()

    # ─────────────────── 상태 메시지 ───────────────────
    def _set_status(self, msg=None, color=None):
        if msg:
            self.status_var.set(msg)
            self.status_lbl.config(fg=color or TEXT_PRI)
        else:
            is_ai = self.mode.get() == "AI"
            if self.current == "X":
                self.status_var.set("▶  PLAYER X  턴")
                self.status_lbl.config(fg=X_COLOR)
            else:
                label = "AI" if is_ai else "PLAYER O"
                self.status_var.set(f"▶  {label}  턴")
                self.status_lbl.config(fg=O_COLOR)

    # ─────────────────── 클릭 처리 ───────────────────
    def _on_click(self, idx):
        if not self.game_active or self.board[idx]:
            return
        if self.mode.get() == "AI" and self.current == "O":
            return   # AI 차례에는 클릭 무시

        self._place(idx)

        if self.game_active and self.mode.get() == "AI" and self.current == "O":
            self.root.after(350, self._ai_move)

    def _ai_move(self):
        if not self.game_active: return
        move = best_ai_move(self.board)
        if move != -1:
            self._place(move)

    # ─────────────────── 돌 놓기 ───────────────────
    def _place(self, idx):
        self.board[idx] = self.current
        self._draw_symbol(idx, self.current)

        winner = check_winner_board(self.board)
        if winner:
            self._end_game(winner)
        elif "" not in self.board:
            self._end_game(None)
        else:
            self.current = "O" if self.current == "X" else "X"
            self._set_status()

    # ─────────────────── 심볼 그리기 ───────────────────
    def _draw_symbol(self, idx, sym):
        cell = self.buttons[idx]
        cell.delete("all")
        pad = 22
        w, h = 110, 110

        if sym == "X":
            cell.create_line(pad, pad, w-pad, h-pad,
                             fill=X_COLOR, width=7, capstyle="round")
            cell.create_line(w-pad, pad, pad, h-pad,
                             fill=X_COLOR, width=7, capstyle="round")
        else:
            cell.create_oval(pad, pad, w-pad, h-pad,
                             outline=O_COLOR, width=7)

    # ─────────────────── 게임 종료 ───────────────────
    def _end_game(self, winner):
        self.game_active = False
        is_ai = self.mode.get() == "AI"

        if winner:
            self.scores[winner] += 1
            self.score_labels[winner].config(text=str(self.scores[winner]))
            self._highlight_winner(winner)
            if winner == "X":
                msg, color = "🎉  PLAYER X  승리!", X_COLOR
            else:
                label = "AI" if is_ai else "PLAYER O"
                msg, color = f"🎉  {label}  승리!", O_COLOR
        else:
            self.scores["TIE"] += 1
            self.score_labels["TIE"].config(text=str(self.scores["TIE"]))
            msg, color = "🤝  무승부!", TIE_COLOR

        self._set_status(msg, color)
        self.root.after(1800, self._start_game)

    def _highlight_winner(self, winner):
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        color = X_COLOR if winner == "X" else O_COLOR
        for line in lines:
            if all(self.board[i] == winner for i in line):
                for idx in line:
                    self.buttons[idx].configure(bg="#2A1A1A" if winner == "X" else "#0A1A2A")
                break


# ──────────────────────────────── 실행 ──────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()
