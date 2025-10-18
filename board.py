import pygame
import config
import os




class GameBoard:
    def __init__(self, screen):
        self.screen = screen


        # Các đường dẫn khả dĩ để tìm ảnh bàn cờ
        candidates = [
            "E:/duong/co so AI/Chess_AI/assets/board.png",
            "E:/duong/co so AI/Chess_AI/assets/board.jpg",
            os.path.join("assets", "board.png"),
            os.path.join("assets", "board.jpg"),
        ]
        board_path = next((p for p in candidates if os.path.exists(p)), None)
        if board_path is None:
            raise FileNotFoundError("Không tìm thấy file ảnh bàn cờ trong thư mục assets hoặc đường dẫn mặc định")


        # Load ảnh một lần và scale theo cấu hình
        img = pygame.image.load(board_path)
        try:
            self.board_img = img.convert_alpha()
        except Exception:
            self.board_img = img.convert()
        self.board_img = pygame.transform.scale(self.board_img, (config.BOARD_WIDTH, config.BOARD_HEIGHT))


        # Font mặc định
        self.font = pygame.font.SysFont("SimHei", 50)
    def draw_grid(self):
        if not config.SHOW_GRID:
            return
        for x in range(config.BOARD_COLS):
            for y in range(config.BOARD_ROWS):
                px, py = self.to_pixel(x, y)
                # Vẽ dấu chấm nhỏ tại giao điểm
                pygame.draw.circle(self.screen, (0, 255, 0), (int(px), int(py)), 3)


    def to_pixel(self, x, y):
        """Chuyển tọa độ logic sang tọa độ pixel thật.
        Tính kích thước ô dựa trên kích thước ảnh bàn cờ để tránh lệch."""
        board_w = self.board_img.get_width()
        board_h = self.board_img.get_height()


        cell_w = board_w / config.BOARD_COLS
        cell_h = board_h / config.BOARD_ROWS


        # lấy tâm ô để vẽ quân/điểm chính xác
        px = config.BOARD_X + config.GRID_OFFSET_X + x * cell_w + cell_w / 2
        py = config.BOARD_Y + config.GRID_OFFSET_Y + y * cell_h + cell_h / 2


        return px, py
    def pixel_to_coord(self, px, py):
        """Chuyển từ pixel (ví dụ vị trí chuột) về tọa độ lưới (x, y).
        Trả về (x, y) đã clamp trong khoảng [0, COLS-1], [0, ROWS-1]."""
        rel_x = px - (config.BOARD_X + config.GRID_OFFSET_X)
        rel_y = py - (config.BOARD_Y + config.GRID_OFFSET_Y)


        board_w = self.board_img.get_width()
        board_h = self.board_img.get_height()


        cell_w = board_w / config.BOARD_COLS
        cell_h = board_h / config.BOARD_ROWS


        x = int(rel_x / cell_w)
        y = int(rel_y / cell_h)


        # clamp về phạm vi hợp lệ
        x = max(0, min(config.BOARD_COLS - 1, x))
        y = max(0, min(config.BOARD_ROWS - 1, y))
        return x, y
    # ===========================================================
    #                        VẼ BÀN CỜ
    # ===========================================================
    def draw_board(self, black_pieces, red_pieces, valid_moves, current_turn=None):
        self.screen.fill(config.BG_COLOR)
        self.screen.blit(self.board_img, (config.BOARD_X, config.BOARD_Y))


        # Vẽ các nước đi hợp lệ
        for move in valid_moves:
            mv_px, mv_py = self.to_pixel(move[0], move[1])
            pygame.draw.circle(
                self.screen,
                config.GREEN,
                (int(mv_px), int(mv_py)),
                max(4, int(min(self.board_img.get_width()/config.BOARD_COLS, self.board_img.get_height()/config.BOARD_ROWS) // 12)),
            )


        # Vẽ quân đen
        for pos, text in black_pieces.items():
            self.draw_piece(pos[0], pos[1], config.BLACK, text, config.BLACK_BG)


        # Vẽ quân đỏ
        for pos, text in red_pieces.items():
            self.draw_piece(pos[0], pos[1], config.RED, text, config.RED_BG)


        # Hiển thị lượt đi
        if current_turn:
            self.draw_turn_indicator(current_turn)
        self.draw_grid()
        pygame.display.flip()


    # ===========================================================
    #                        VẼ QUÂN CỜ
    # ===========================================================
    def draw_piece(self, x, y, color, text, bg_color):
        # Dùng hệ tọa độ ảo (to_pixel trả về tâm ô)
        px, py = self.to_pixel(x, y)
        center = (int(px), int(py))


        # Tính bán kính dựa trên kích thước ô thực
        cell_w = self.board_img.get_width() / config.BOARD_COLS
        cell_h = self.board_img.get_height() / config.BOARD_ROWS
        radius = int(max(4, min(cell_w, cell_h) / 2 - 5))


        # Nền quân
        pygame.draw.circle(self.screen, bg_color, center, radius)
        pygame.draw.circle(self.screen, color, center, max(1, radius - 3), 3)


        # Ký hiệu quân (phóng to/thu nhỏ tùy ô)
        # điều chỉnh size font nếu cần (nếu font quá lớn/nhỏ)
        try:
            font_size = max(12, int(min(cell_w, cell_h) * 0.5))
            font = pygame.font.SysFont("SimHei", font_size)
        except Exception:
            font = self.font


        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        self.screen.blit(text_surface, text_rect)
    # ===========================================================
    #                        LƯỢT ĐI
    # ===========================================================
    def draw_turn_indicator(self, current_turn):
        color = config.RED if current_turn == "red" else config.BLACK
        text = f"Lượt: {'ĐỎ' if current_turn == 'red' else 'ĐEN'}"
        turn_surface = self.font.render(text, True, color)
        self.screen.blit(
            turn_surface,
            (config.BOARD_X, config.BOARD_Y + config.BOARD_HEIGHT + 30),
        )

    def draw_timer(self, red_time, black_time):
        font = pygame.font.Font(None, 24)
        red_time_text = font.render(f"Red: {int(red_time)}s", True, config.RED)
        black_time_text = font.render(f"Black: {int(black_time)}s", True, config.BLACK)
        self.screen.blit(red_time_text, (10, 500))
        self.screen.blit(black_time_text, (10, 100))
