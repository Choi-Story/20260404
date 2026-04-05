import pygame
import sys
import math
import time

pygame.init()

# ─────────────────────────── 설정 ───────────────────────────
WIDTH, HEIGHT = 520, 680
FPS = 60

# 색상
BG          = (10,  10,  10)
PANEL       = (18,  18,  18)
GRID_COLOR  = (40,  40,  40)
CELL_HOVER  = (30,  30,  30)
X_COLOR     = (255, 59,  92)    # 빨강
O_COLOR     = (0,   198, 255)   # 하늘색
TIE_COLOR   = (120, 120, 120)
BTN_NORMAL  = (28,  28,  28)
BTN_HOVER   = (42,  42,  42)
BTN_ACTIVE  = (55,  55,  55)
TEXT_PRI    = (255, 255, 255)
TEXT_SEC    = (90,  90,  90)
WIN_FLASH_X = (60,  15,  20)
WIN_FLASH_O = (10,  40,  60)

# 폰트
pygame.font.init()
try:
    FONT_TITLE  = pygame.font.SysFont("Courier New", 28, bold=True)
    FONT_SUB    = pygame.font.SysFont("Courier New", 10, bold=False)
    FONT_STATUS = pygame.font.SysFont("Courier New", 15, bold=True)
    FONT_BTN    = pygame.font.SysFont("Courier New", 12, bold=True)
    FONT_SCORE  = pygame.font.SysFont("Courier New", 20, bold=True)
    FONT_SLABEL = pygame.font.SysFont("Courier New",  9, bold=False)
except:
    FONT_TITLE  = pygame.font.SysFont(None, 32)
    FONT_SUB    = pygame.font.SysFont(None, 14)
    FONT_STATUS = pygame.font.SysFont(None, 18)
    FONT_BTN    = pygame.font.SysFont(None, 16)
    FONT_SCORE  = pygame.font.SysFont(None, 24)
    FONT_SLABEL = pygame.font.SysFont(None, 13)

# ─────────────────────────── Minimax AI ───────────────────────────
LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_winner(board):
    for a,b,c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def get_winning_line(board, sym):
    for line in LINES:
        if all(board[i] == sym for i in line):
            return line
    return None

def minimax(board, depth, is_max, alpha, beta):
    w = check_winner(board)
    if w == "O": return 10 - depth
    if w == "X": return depth - 10
    if "" not in board: return 0
    if is_max:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                best = max(best, minimax(board, depth+1, False, alpha, beta))
                board[i] = ""
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                best = min(best, minimax(board, depth+1, True, alpha, beta))
                board[i] = ""
                beta = min(beta, best)
                if beta <= alpha: break
        return best

def best_move(board):
    bv, bi = -math.inf, -1
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            v = minimax(board, 0, False, -math.inf, math.inf)
            board[i] = ""
            if v > bv:
                bv, bi = v, i
    return bi

# ─────────────────────────── 게임 클래스 ───────────────────────────
class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TIC · TAC · TOE")
        self.clock  = pygame.time.Clock()

        # 상태
        self.mode         = "2P"    # "2P" | "AI"
        self.board        = [""] * 9
        self.current      = "X"
        self.game_active  = False
        self.scores       = {"X": 0, "O": 0, "TIE": 0}
        self.status_msg   = ""
        self.status_color = TEXT_PRI
        self.winner       = None
        self.win_line_idx = None
        self.hover_cell   = -1
        self.ai_pending   = False
        self.ai_time      = 0
        self.flash_alpha  = 0
        self.flash_dir    = 1
        self.result_time  = 0

        # 레이아웃
        self.margin      = 28
        self.board_top   = 200
        self.cell_size   = (WIDTH - self.margin*2) // 3   # ~154
        self.board_left  = self.margin
        self.board_size  = self.cell_size * 3

        # 버튼 rect
        btn_y = self.board_top + self.board_size + 30
        bw, bh = 175, 38
        self.btn_new   = pygame.Rect(self.margin, btn_y, bw, bh)
        self.btn_reset = pygame.Rect(WIDTH - self.margin - bw, btn_y, bw, bh)

        # 모드 버튼
        mw, mh = 170, 36
        mx = WIDTH//2
        self.btn_2p = pygame.Rect(mx - mw - 6, 120, mw, mh)
        self.btn_ai = pygame.Rect(mx + 6,       120, mw, mh)

        self._start_game()

    # ── 셀 rect ──
    def cell_rect(self, idx):
        r, c = divmod(idx, 3)
        x = self.board_left + c * self.cell_size
        y = self.board_top  + r * self.cell_size
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    # ── 셀 인덱스 from 좌표 ──
    def pos_to_cell(self, mx, my):
        for i in range(9):
            if self.cell_rect(i).collidepoint(mx, my):
                return i
        return -1

    # ── 게임 시작 ──
    def _start_game(self):
        self.board        = [""] * 9
        self.current      = "X"
        self.game_active  = True
        self.winner       = None
        self.win_line_idx = None
        self.ai_pending   = False
        self.flash_alpha  = 0
        self._set_status()

    def _set_status(self, msg=None, color=None):
        if msg:
            self.status_msg   = msg
            self.status_color = color or TEXT_PRI
        else:
            is_ai = self.mode == "AI"
            if self.current == "X":
                self.status_msg   = "▶  PLAYER X  턴"
                self.status_color = X_COLOR
            else:
                label = "AI" if is_ai else "PLAYER O"
                self.status_msg   = f"▶  {label}  턴"
                self.status_color = O_COLOR

    # ── 돌 놓기 ──
    def _place(self, idx):
        if not self.game_active or self.board[idx]: return
        self.board[idx] = self.current

        w = check_winner(self.board)
        if w:
            self.winner       = w
            self.win_line_idx = get_winning_line(self.board, w)
            self.game_active  = False
            self.scores[w]   += 1
            label = ("AI" if self.mode == "AI" else "PLAYER O") if w == "O" else "PLAYER X"
            self._set_status(f"🎉  {label}  승리!", X_COLOR if w == "X" else O_COLOR)
            self.result_time  = time.time()
        elif "" not in self.board:
            self.game_active = False
            self.scores["TIE"] += 1
            self._set_status("🤝  무승부!", TIE_COLOR)
            self.result_time = time.time()
        else:
            self.current = "O" if self.current == "X" else "X"
            self._set_status()
            if self.mode == "AI" and self.current == "O":
                self.ai_pending = True
                self.ai_time    = time.time() + 0.4

    # ── 그리기 ──
    def draw(self):
        self.screen.fill(BG)
        self._draw_title()
        self._draw_mode_buttons()
        self._draw_status()
        self._draw_board()
        self._draw_scores()
        self._draw_buttons()
        pygame.display.flip()

    def _draw_title(self):
        t  = FONT_TITLE.render("TIC · TAC · TOE", True, TEXT_PRI)
        s  = FONT_SUB.render("STRATEGY  BOARD  GAME", True, TEXT_SEC)
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 22))
        self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 58))

    def _draw_mode_buttons(self):
        for btn, label, val in [
            (self.btn_2p, "  2 PLAYER", "2P"),
            (self.btn_ai, "  vs AI",    "AI"),
        ]:
            active = self.mode == val
            color  = BTN_ACTIVE if active else BTN_HOVER if btn.collidepoint(pygame.mouse.get_pos()) else BTN_NORMAL
            pygame.draw.rect(self.screen, color, btn, border_radius=6)
            if active:
                pygame.draw.rect(self.screen, X_COLOR if val=="2P" else O_COLOR, btn, 2, border_radius=6)
            icon = "👥" if val == "2P" else "🤖"
            surf = FONT_BTN.render(label, True, TEXT_PRI if active else TEXT_SEC)
            self.screen.blit(surf, (btn.x + btn.w//2 - surf.get_width()//2,
                                    btn.y + btn.h//2 - surf.get_height()//2))

    def _draw_status(self):
        surf = FONT_STATUS.render(self.status_msg, True, self.status_color)
        self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 172))

    def _draw_board(self):
        cs  = self.cell_size
        bl  = self.board_left
        bt  = self.board_top
        bs  = self.board_size

        # 외곽선
        pygame.draw.rect(self.screen, GRID_COLOR,
                         pygame.Rect(bl-2, bt-2, bs+4, bs+4), 2, border_radius=4)

        for i in range(9):
            rect = self.cell_rect(i)
            # 셀 배경
            if self.win_line_idx and i in self.win_line_idx:
                bg = WIN_FLASH_X if self.winner == "X" else WIN_FLASH_O
            elif i == self.hover_cell and self.game_active and not self.board[i]:
                bg = CELL_HOVER
            else:
                bg = (14,14,14)
            pygame.draw.rect(self.screen, bg, rect)

            # 그리드 선
            pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

            # 심볼
            if self.board[i]:
                self._draw_symbol(rect, self.board[i])

    def _draw_symbol(self, rect, sym):
        cx = rect.centerx
        cy = rect.centery
        pad = 22
        lw  = 7

        if sym == "X":
            x1, y1 = rect.left + pad, rect.top + pad
            x2, y2 = rect.right - pad, rect.bottom - pad
            pygame.draw.line(self.screen, X_COLOR, (x1,y1), (x2,y2), lw)
            pygame.draw.line(self.screen, X_COLOR, (x2,y1), (x1,y2), lw)
        else:
            r = rect.width // 2 - pad
            pygame.draw.circle(self.screen, O_COLOR, (cx, cy), r, lw)

    def _draw_scores(self):
        sy = self.board_top + self.board_size + 80
        panel = pygame.Rect(self.margin, sy, WIDTH - self.margin*2, 60)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)

        labels = [("PLAYER X", "X", X_COLOR),
                  ("DRAW",     "TIE", TIE_COLOR),
                  ("AI" if self.mode=="AI" else "PLAYER O", "O", O_COLOR)]
        w3 = panel.width // 3
        for i, (lbl, key, color) in enumerate(labels):
            cx = panel.x + w3*i + w3//2
            ls = FONT_SLABEL.render(lbl, True, TEXT_SEC)
            vs = FONT_SCORE.render(str(self.scores[key]), True, color)
            self.screen.blit(ls, (cx - ls.get_width()//2, sy + 10))
            self.screen.blit(vs, (cx - vs.get_width()//2, sy + 28))

    def _draw_buttons(self):
        mp = pygame.mouse.get_pos()
        for btn, label in [(self.btn_new, "🔄  NEW GAME"),
                           (self.btn_reset, "🗑  RESET ALL")]:
            hov = btn.collidepoint(mp)
            pygame.draw.rect(self.screen, BTN_HOVER if hov else BTN_NORMAL,
                             btn, border_radius=6)
            pygame.draw.rect(self.screen, GRID_COLOR, btn, 1, border_radius=6)
            surf = FONT_BTN.render(label, True, TEXT_PRI)
            self.screen.blit(surf, (btn.centerx - surf.get_width()//2,
                                    btn.centery - surf.get_height()//2))

    # ── 이벤트 & 루프 ──
    def run(self):
        while True:
            self.clock.tick(FPS)
            now = time.time()

            # AI 대기
            if self.ai_pending and now >= self.ai_time:
                self.ai_pending = False
                mv = best_move(self.board)
                if mv != -1:
                    self._place(mv)

            # 결과 후 자동 새 게임
            if not self.game_active and self.result_time and \
               now - self.result_time > 1.8:
                self.result_time = 0
                self._start_game()

            # 호버 셀
            mx, my = pygame.mouse.get_pos()
            self.hover_cell = self.pos_to_cell(mx, my)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # 모드 버튼
                    if self.btn_2p.collidepoint(mx, my):
                        self.mode = "2P"; self._start_game()
                    elif self.btn_ai.collidepoint(mx, my):
                        self.mode = "AI"; self._start_game()

                    # 액션 버튼
                    elif self.btn_new.collidepoint(mx, my):
                        self._start_game()
                    elif self.btn_reset.collidepoint(mx, my):
                        self.scores = {"X":0,"O":0,"TIE":0}
                        self._start_game()

                    # 셀 클릭
                    else:
                        ci = self.pos_to_cell(mx, my)
                        if ci != -1 and self.game_active and not self.board[ci]:
                            if self.mode == "2P":
                                self._place(ci)
                            elif self.current == "X":
                                self._place(ci)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._start_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

            self.draw()

# ──────────────────────────── 실행 ────────────────────────────
if __name__ == "__main__":
    game = TicTacToe()
    game.run()
