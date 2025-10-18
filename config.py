import pygame


# ==============================
# ⚙️ Cấu hình cơ bản


# ==============================
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 850


# ==============================
# 🎨 Màu sắc
# ==============================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
BG_COLOR = (230, 210, 170)


# ==============================
# ♟️ Bàn cờ (9 cột × 10 hàng)
# ==============================
BOARD_COLS = 9
BOARD_ROWS = 10
CELL_SIZE = 65   # Khoảng cách giữa hai giao điểm (điều chỉnh cho khớp ảnh)


# Kích thước bàn cờ tính theo giao điểm (không phải số ô)
BOARD_WIDTH = (BOARD_COLS - 1) * CELL_SIZE
BOARD_HEIGHT = (BOARD_ROWS - 1) * CELL_SIZE


# Vị trí bàn cờ (tọa độ góc trên bên trái trên màn hình)
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2 - 20
# Offset để dịch hệ toạ độ ảo cho khớp với lưới thật
GRID_OFFSET_X = 0  
GRID_OFFSET_Y = 3


# ==============================
# 🎯 Tùy chọn hiển thị lưới ảo (để căn chỉnh)
# ==============================
SHOW_GRID = False   # ⚙️ Đặt False khi đã căn chuẩn


# ==============================
# 🧩 Điều chỉnh vị trí quân (nếu cần căn mịn)
# ==============================
PIECE_OFFSET_X = 0  # chỉ dùng khi quân cờ hơi lệch (± vài pixel)
PIECE_OFFSET_Y = 0


# ==============================
# 🎭 Màu nền quân cờ
# ==============================
RED_BG = (255, 220, 220)
BLACK_BG = (230, 230, 230)
