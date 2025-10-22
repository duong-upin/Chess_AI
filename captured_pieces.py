import pygame
import config

class CapturedPieces:
    def __init__(self, screen):
        self.screen = screen
        self.red_captured = []  # Danh sách quân bị ăn của Đỏ
        self.black_captured = []  # Danh sách quân bị ăn của Đen
        self.font = pygame.font.Font("assets/simhei.ttf",30)

    def add_captured_piece(self, piece, is_red):
        """Thêm quân cờ bị ăn vào danh sách"""
        if is_red:
            self.black_captured.append(piece)
        else:
            self.red_captured.append(piece)

    def draw_captured_pieces(self):
        """Vẽ các quân cờ bị ăn lên màn hình"""
        start_x = config.SCREEN_WIDTH - 200
        y_offset_red = 100
        y_offset_black = config.SCREEN_HEIGHT - 100

        for i, piece in enumerate(self.red_captured):
            x_pos = start_x + (i % 5) * 35  # Mỗi quân cách nhau 50 pixel
            y_pos = y_offset_red + (i // 5) * 35  # Xuống hàng sau mỗi 5 quân
            self.draw_piece(x_pos, y_pos, config.RED, piece)

        for i, piece in enumerate(self.black_captured):
            x_pos = start_x + (i % 5) * 35
            y_pos = y_offset_black - (i // 5) * 35
            self.draw_piece(x_pos, y_pos, config.BLACK, piece)

    def draw_piece(self, x, y, color, text):
        """Vẽ quân cờ đã bị ăn"""
        pygame.draw.circle(self.screen, color, (x, y), config.CELL_SIZE // 2)
        text_surface = self.font.render(text, True, config.WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)
