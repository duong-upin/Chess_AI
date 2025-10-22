import pygame
import config
import os

class GameBoard:
    def __init__(self, screen):
        self.last_move = None  # sẽ lưu dạng: ((sx, sy), (ex, ey))
        self.screen = screen

        # Tìm ảnh bàn cờ (đường dẫn tương đối)
        candidates = [
            "assets/board.png",
            "assets/board.jpg",
            os.path.join("assets", "board.png"),
            os.path.join("assets", "board.jpg"),
        ]
        board_path = next((p for p in candidates if os.path.exists(p)), None)
        if board_path is None:
            raise FileNotFoundError("Không tìm thấy file ảnh bàn cờ trong thư mục assets")

        img = pygame.image.load(board_path)
        try:
            self.board_img = img.convert_alpha()
        except Exception:
            self.board_img = img.convert()
        self.board_img = pygame.transform.scale(
            self.board_img, (config.BOARD_WIDTH, config.BOARD_HEIGHT)
        )

        # Font mặc định cho text “lượt”
        self.font = pygame.font.SysFont("SimHei", 50)

    # ----------------- helpers -----------------
    def _get_font(self, size, bold=False):
        """Font UI nội bộ (không phụ thuộc get_vn_font ở main.py)."""
        try:
            # ưu tiên vài font hay có sẵn
            for name in ["Segoe UI", "Roboto", "Arial", "Tahoma", "Noto Sans"]:
                path = pygame.font.match_font(name, bold=bold)
                if path:
                    return pygame.font.Font(path, size)
        except Exception:
            pass
        return pygame.font.SysFont(None, size, bold=bold)

    def draw_grid(self):
        if not config.SHOW_GRID:
            return
        for x in range(config.BOARD_COLS):
            for y in range(config.BOARD_ROWS):
                px, py = self.to_pixel(x, y)
                pygame.draw.circle(self.screen, (0, 255, 0), (int(px), int(py)), 3)

    def to_pixel(self, x, y):
        board_w = self.board_img.get_width()
        board_h = self.board_img.get_height()
        cell_w = board_w / config.BOARD_COLS
        cell_h = board_h / config.BOARD_ROWS
        px = config.BOARD_X + config.GRID_OFFSET_X + x * cell_w + cell_w / 2
        py = config.BOARD_Y + config.GRID_OFFSET_Y + y * cell_h + cell_h / 2
        return px, py

    def pixel_to_coord(self, px, py):
        rel_x = px - (config.BOARD_X + config.GRID_OFFSET_X)
        rel_y = py - (config.BOARD_Y + config.GRID_OFFSET_Y)
        board_w = self.board_img.get_width()
        board_h = self.board_img.get_height()
        cell_w = board_w / config.BOARD_COLS
        cell_h = board_h / config.BOARD_ROWS
        x = int(rel_x / cell_w)
        y = int(rel_y / cell_h)
        x = max(0, min(config.BOARD_COLS - 1, x))
        y = max(0, min(config.BOARD_ROWS - 1, y))
        return x, y

    # ----------------- vẽ bàn cờ -----------------
    def draw_board(self, black_pieces, red_pieces, valid_moves, selected=None, current_turn=None):
        self.screen.fill(config.BG_COLOR)
        self.screen.blit(self.board_img, (config.BOARD_X, config.BOARD_Y))

        # ✨ Vẽ vệt nước đi trước
        self._draw_last_move_trail()

        # Vẽ các nước đi hợp lệ
        r = max(4, int(min(self.board_img.get_width() / config.BOARD_COLS,
                        self.board_img.get_height() / config.BOARD_ROWS) // 12))
        for gx, gy in valid_moves:
            mv_px, mv_py = self.to_pixel(gx, gy)
            pygame.draw.circle(self.screen, config.GREEN, (int(mv_px), int(mv_py)), r)

        # ✨ Vẽ quân, làm mờ quân đang chọn
        for (x, y), ch in black_pieces.items():
            self.draw_piece(x, y, config.BLACK, ch, config.BLACK_BG, dim=(selected == (x, y)))
        for (x, y), ch in red_pieces.items():
            self.draw_piece(x, y, config.RED, ch, config.RED_BG, dim=(selected == (x, y)))

        # Hiển thị lượt
        if current_turn:
            self.draw_turn_indicator(current_turn)

        self.draw_grid()

    def _draw_last_move_trail(self):
        if not self.last_move:
            return

        (sx, sy), (ex, ey) = self.last_move
        x1, y1 = self.to_pixel(sx, sy)
        x2, y2 = self.to_pixel(ex, ey)

        # Màu vệt
        trail_col = (220, 60, 60)

        # Vẽ các chấm nhỏ theo đoạn đường
        steps = max(1, int(((x1 - x2)**2 + (y1 - y2)**2)**0.5 // 22))
        for i in range(1, steps):
            t = i / steps
            px = int(x1 + (x2 - x1) * t)
            py = int(y1 + (y2 - y1) * t)
            pygame.draw.circle(self.screen, trail_col, (px, py), 3)

        # Vẽ vòng tròn ở đầu và cuối
        pygame.draw.circle(self.screen, trail_col, (int(x1), int(y1)), 10, 2)
        pygame.draw.circle(self.screen, trail_col, (int(x2), int(y2)), 10, 2)

    # ----------------- vẽ quân -----------------
    def draw_piece(self, x, y, color, text, bg_color, dim=False):
        px, py = self.to_pixel(x, y)
        center = (int(px), int(py))

        cell_w = self.board_img.get_width() / config.BOARD_COLS
        cell_h = self.board_img.get_height() / config.BOARD_ROWS
        radius = int(max(4, min(cell_w, cell_h) / 2 - 5))

        # vẽ lên surface có alpha để dễ mờ toàn bộ
        box = int(max(cell_w, cell_h)) + 8
        temp = pygame.Surface((box, box), pygame.SRCALPHA)
        c = (box // 2, box // 2)

        # nền + viền
        pygame.draw.circle(temp, bg_color, c, radius)
        pygame.draw.circle(temp, color,    c, max(1, radius - 3), 3)

        # chữ
        try:
            font_size = max(12, int(min(cell_w, cell_h) * 0.5))
            font = pygame.font.SysFont("SimHei", font_size)
        except Exception:
            font = self.font
        glyph = font.render(text, True, color)
        temp.blit(glyph, glyph.get_rect(center=c))

        # nếu đang chọn → mờ đi
        if dim:
            temp.set_alpha(110)  # 0..255

        self.screen.blit(temp, (center[0] - box // 2, center[1] - box // 2))

    # ----------------- lượt đi -----------------
    def draw_turn_indicator(self, current_turn):
        color = config.RED if current_turn == "red" else config.BLACK
        text = f"Lượt: {'ĐỎ' if current_turn == 'red' else 'ĐEN'}"
        turn_surface = self.font.render(text, True, color)
        self.screen.blit(
            turn_surface,
            (config.BOARD_X, config.BOARD_Y + config.BOARD_HEIGHT + 30),
        )

    # ----------------- timer dạng "button" -----------------
    def _timer_button(self, rect, title, seconds, color, active):
        bg_idle = (60, 45, 28)
        bg_act  = (78, 58, 36)
        bg = bg_act if active else bg_idle
        pygame.draw.rect(self.screen, bg, rect, border_radius=16)
        pygame.draw.rect(self.screen, color, rect, width=2, border_radius=16)

        seconds = max(0, int(seconds))
        mm, ss = divmod(seconds, 60)
        time_text = f"{mm:02d}:{ss:02d}"

        title_font = self._get_font(18, bold=True)
        time_font  = self._get_font(28, bold=True)

        title_surf = title_font.render(title, True, color)
        self.screen.blit(title_surf, title_surf.get_rect(midtop=(rect[0] + rect[2] // 2, rect[1] + 6)))

        time_surf = time_font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surf, time_surf.get_rect(midbottom=(rect[0] + rect[2] // 2, rect[1] + rect[3] - 8)))

    def draw_timer(self, red_time, black_time, red_turn):
        btn_w, btn_h = 160, 70
        left_x  = config.BOARD_X - btn_w - 16
        right_x = config.BOARD_X + config.BOARD_WIDTH + 16
        mid_y   = config.BOARD_Y + config.BOARD_HEIGHT // 2

        black_rect = pygame.Rect(right_x, mid_y - btn_h - 8, btn_w, btn_h)
        red_rect   = pygame.Rect(left_x,  mid_y + 8,        btn_w, btn_h)

        self._timer_button(black_rect, "BLACK", black_time, config.BLACK, (not red_turn))
        self._timer_button(red_rect,   "RED",   red_time,   config.RED,   red_turn)
