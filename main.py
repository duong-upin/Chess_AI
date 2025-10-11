import pygame
import config
from ai import ChessAI
from pieces import PieceData
from move_validator import MoveValidator
from board import GameBoard
from timer_manager import TimerManager
from captured_pieces import CapturedPieces

# =========================
# UI helpers
# =========================
def draw_center_text(screen, text, y, font, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)

def button(screen, rect, text, font, bg=(90, 60, 20), fg=(255, 255, 255), hover_bg=(120, 80, 30)):
    x, y, w, h = rect
    mx, my = pygame.mouse.get_pos()
    is_hover = (x <= mx <= x + w and y <= my <= y + h)
    pygame.draw.rect(screen, hover_bg if is_hover else bg, rect, border_radius=12)
    label = font.render(text, True, fg)
    screen.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))
    return is_hover

# =========================
# ÂM THANH (đủ cho yêu cầu "setting" + "bonus ăn quân")
# =========================
class SoundManager:
    def __init__(self):
        self.volume = 0.6
        self.click = None
        self.capture_default = None
        self.capture_map = {}  # map ký tự quân -> âm ăn quân
        self.per_piece_sound = True  # bật/tắt bonus “mỗi loại quân 1 âm”
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self._load_sounds()

    def _safe_load(self, path):
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(self.volume)
            return s
        except Exception:
            return None

    def _load_sounds(self):
        # bạn có thể đổi đường dẫn file theo thư mục của bạn
        self.click = self._safe_load("assets/sounds/click.wav")
        self.capture_default = self._safe_load("assets/sounds/capture_default.wav")

        def cap(path):
            return self._safe_load(path) or self.capture_default

        # Map theo chữ Trung (đổi/giảm bớt tùy file bạn có)
        self.capture_map = {
            # Xe
            "車": cap("assets/sounds/capture_rook.wav"),
            "俥": cap("assets/sounds/capture_rook.wav"),
            # Mã
            "馬": cap("assets/sounds/capture_knight.wav"),
            "傌": cap("assets/sounds/capture_knight.wav"),
            # Tượng / Tướng sĩ / Pháo / Tốt
            "象": cap("assets/sounds/capture_bishop.wav"),
            "相": cap("assets/sounds/capture_bishop.wav"),
            "士": cap("assets/sounds/capture_guard.wav"),
            "仕": cap("assets/sounds/capture_guard.wav"),
            "將": cap("assets/sounds/capture_king.wav"),
            "帥": cap("assets/sounds/capture_king.wav"),
            "炮": cap("assets/sounds/capture_cannon.wav"),
            "砲": cap("assets/sounds/capture_cannon.wav"),
            "包": cap("assets/sounds/capture_cannon.wav"),
            "卒": cap("assets/sounds/capture_pawn.wav"),
            "兵": cap("assets/sounds/capture_pawn.wav"),
        }

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, v))
        if self.click: self.click.set_volume(self.volume)
        if self.capture_default: self.capture_default.set_volume(self.volume)
        for s in self.capture_map.values():
            if s: s.set_volume(self.volume)

    def play_click(self):
        if self.click:
            try: self.click.play()
            except Exception: pass

    def play_capture(self, captured_piece_char):
        if not self.per_piece_sound:
            s = self.capture_default
        else:
            s = self.capture_map.get(captured_piece_char, self.capture_default)
        if s:
            try: s.play()
            except Exception: pass

# =========================
# MÀN HÌNH CÀI ĐẶT (theo yêu cầu: chỉnh âm lượng, âm click, chỉnh ảnh placeholder, bonus ăn quân)
# =========================
def setting(screen, sound: SoundManager):
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 50)
    label_font = pygame.font.SysFont(None, 28)
    btn_font  = pygame.font.SysFont(None, 32)

    # slider âm lượng
    slider_rect = pygame.Rect(180, 220, max(300, config.SCREEN_WIDTH - 360), 8)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                slider_rect.width = max(300, config.SCREEN_WIDTH - 360)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if slider_rect.collidepoint(mx, my):
                    ratio = (mx - slider_rect.x) / max(1, slider_rect.width)
                    sound.set_volume(ratio)
                    sound.play_click()

        screen.fill((26, 18, 10))
        draw_center_text(screen, "SETTINGS", 90, title_font)
        draw_center_text(screen, f"Volume: {int(sound.volume * 100)}%", 160, label_font, (220, 200, 160))

        # slider
        pygame.draw.rect(screen, (70, 50, 30), slider_rect, border_radius=8)
        knob_x = int(slider_rect.x + slider_rect.width * sound.volume)
        pygame.draw.circle(screen, (200, 180, 140), (knob_x, slider_rect.y + slider_rect.height // 2), 12)

        # nút
        btn_w, btn_h = 260, 56
        bx = (config.SCREEN_WIDTH - btn_w) // 2
        rect_preview = (bx, 270, btn_w, btn_h)
        rect_skin    = (bx, 340, btn_w, btn_h)
        rect_toggle  = (bx, 410, btn_w, btn_h)
        rect_back    = (bx, 480, btn_w, btn_h)

        button(screen, rect_preview, "Preview Click", btn_font)
        button(screen, rect_skin, "Change Skin (placeholder)", btn_font)
        button(screen, rect_toggle, f"Per-piece Capture Sound: {'ON' if sound.per_piece_sound else 'OFF'}", btn_font)
        button(screen, rect_back, "Back to Main Menu", btn_font)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
            if pygame.Rect(rect_preview).collidepoint(mx, my):
                sound.play_click()
            elif pygame.Rect(rect_skin).collidepoint(mx, my):
                # chỗ này để TODO: mở popup chọn ảnh/skin
                sound.play_click()
            elif pygame.Rect(rect_toggle).collidepoint(mx, my):
                sound.per_piece_sound = not sound.per_piece_sound
                sound.play_click()
            elif pygame.Rect(rect_back).collidepoint(mx, my):
                sound.play_click()
                return "MENU"

        pygame.display.flip()
        clock.tick(60)

# =========================
# CHẾ ĐỘ CHƠI (VS AI / 2P) – phục vụ cho main và xd
# =========================
def run_match(screen, sound: SoundManager, human_is_red: bool | None, ai_depth: int | None):
    """
    Chạy 1 ván:
      - Đỏ luôn đi trước, Đen đi sau.
      - Nếu kết thúc: hiển thị Thắng/Thua + chọn 'Chơi tiếp' hoặc 'Về màn hình chính'.
      - Nếu 'Chơi tiếp': người thua = ĐỎ và đi trước ván sau.
    human_is_red: True/False khi chơi với máy; None khi 2 người chơi (cả 2 đều là human).
    ai_depth: độ sâu minimax nếu vs AI; None nếu 2 người chơi.
    Trả về: ('MENU'|'QUIT'|'AGAIN', loser_is_human_bool_or_None)
    """
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 56)
    btn_font   = pygame.font.SysFont(None, 36)
    info_font  = pygame.font.SysFont(None, 28)

    board = GameBoard(screen)
    timer = TimerManager(600)  # 10 phút mỗi bên
    captured = CapturedPieces(screen)
    black_pieces, red_pieces = PieceData.get_initial_pieces()

    ai = None
    if ai_depth is not None:
        # AI là phía còn lại của human
        ai = ChessAI(is_red=not human_is_red)

    red_turn = True       # Đỏ đi trước
    selected = None
    valid_moves = []
    turn_count = 0

    # UI kết thúc
    winner_text = ""
    loser_text  = ""
    loser_is_human = None

    # vòng chơi
    playing = True
    while playing:
        # ===== EVENT =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None
            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                board.screen = screen
                captured.screen = screen
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sound.play_click()
                x, y = pygame.mouse.get_pos()
                gx = (x - config.BOARD_X) // config.CELL_SIZE
                gy = (y - config.BOARD_Y) // config.CELL_SIZE

                # Nếu có AI: chỉ cho thao tác khi là lượt của người
                if ai is not None:
                    is_human_turn = (human_is_red and red_turn) or ((not human_is_red) and (not red_turn))
                    if not is_human_turn:
                        continue

                # Xác định tập quân theo lượt
                pieces = red_pieces if red_turn else black_pieces
                other  = black_pieces if red_turn else red_pieces

                # (Chế độ 2 người) ép lượt chẵn = đỏ, lẻ = đen (đã bảo đảm bằng red_turn/turn_count)
                if (gx, gy) in pieces:
                    selected = (gx, gy)
                    valid_moves = MoveValidator.generate_valid_moves(
                        pieces[selected], selected, pieces, other
                    )
                elif selected and (gx, gy) in valid_moves:
                    # Ăn quân
                    if (gx, gy) in other:
                        captured_piece = other.pop((gx, gy))
                        captured.add_captured_piece(captured_piece, red_turn)
                        sound.play_capture(captured_piece)
                        # Kết thúc nếu ăn vua
                        if captured_piece in ["將", "帥"]:
                            if captured_piece == "將":
                                winner_text = "Bên Đỏ thắng! Vua Đen bị ăn."
                                loser_text  = "Bên Đen thua!"
                                loser_is_human = (ai is None) or (not human_is_red)
                            else:
                                winner_text = "Bên Đen thắng! Vua Đỏ bị ăn."
                                loser_text  = "Bên Đỏ thua!"
                                loser_is_human = (ai is None) or (human_is_red)
                            pieces[(gx, gy)] = pieces.pop(selected)  # để hiển thị cuối
                            playing = False
                            break

                    # Di chuyển
                    pieces[(gx, gy)] = pieces.pop(selected)
                    selected = None
                    valid_moves = []
                    red_turn = not red_turn
                    timer.switch_turn()
                    turn_count += 1

        # ===== UPDATE =====
        screen.fill((30, 20, 12))
        timer.update_timers()
        rt, bt = timer.get_times()

        # Hết giờ
        if playing and rt <= 0:
            winner_text = "Bên Đen thắng do bên Đỏ hết thời gian!"
            loser_text  = "Bên Đỏ thua!"
            loser_is_human = (ai is None) or (human_is_red is True)
            playing = False
        elif playing and bt <= 0:
            winner_text = "Bên Đỏ thắng do bên Đen hết thời gian!"
            loser_text  = "Bên Đen thua!"
            loser_is_human = (ai is None) or (human_is_red is False)
            playing = False

        # Lượt AI
        if playing and ai is not None:
            is_ai_turn = (ai.is_red and red_turn) or ((not ai.is_red) and (not red_turn))
            if is_ai_turn:
                pygame.time.delay(400)
                depth = 3
                try:
                    # nếu bạn có sửa ChessAI để nhận depth động, thay ở đây
                    _, move = ai.minimax(red_pieces, black_pieces, depth, float('-inf'), float('inf'), ai.is_red)
                except Exception:
                    move = ai.get_best_move(red_pieces, black_pieces, depth=3)

                if move:
                    s, e = move
                    pieces = red_pieces if ai.is_red else black_pieces
                    other  = black_pieces if ai.is_red else red_pieces
                    if s in pieces:
                        # Ăn quân
                        if e in other:
                            cap = other.pop(e)
                            captured.add_captured_piece(cap, ai.is_red)
                            sound.play_capture(cap)
                            if cap in ["將", "帥"]:
                                if cap == "帥":
                                    winner_text = "Bên Đen thắng!"
                                    loser_text  = "Bên Đỏ thua!"
                                    loser_is_human = (ai is not None and human_is_red)
                                else:
                                    winner_text = "Bên Đỏ thắng!"
                                    loser_text  = "Bên Đen thua!"
                                    loser_is_human = (ai is not None and (not human_is_red))
                                pieces[e] = pieces.pop(s)
                                playing = False
                            else:
                                pieces[e] = pieces.pop(s)
                                red_turn = not red_turn
                                timer.switch_turn()
                                turn_count += 1
                        else:
                            pieces[e] = pieces.pop(s)
                            red_turn = not red_turn
                            timer.switch_turn()
                            turn_count += 1

        # Vẽ board + timer
        board.draw_board(black_pieces, red_pieces, valid_moves)
        captured.draw_captured_pieces()
        board.draw_timer(rt, bt)

        # Kết thúc → màn hình kết quả + lựa chọn
        if not playing:
            title_font = pygame.font.SysFont(None, 56)
            btn_font   = pygame.font.SysFont(None, 36)
            info_font  = pygame.font.SysFont(None, 28)
            draw_center_text(screen, "VÁN ĐẤU KẾT THÚC", config.SCREEN_HEIGHT // 2 - 120, title_font)
            draw_center_text(screen, winner_text, config.SCREEN_HEIGHT // 2 - 70, btn_font, (255, 220, 120))
            draw_center_text(screen, loser_text,  config.SCREEN_HEIGHT // 2 - 30, info_font, (220, 200, 160))
            draw_center_text(screen, "Chọn một tùy chọn:", config.SCREEN_HEIGHT // 2 + 10, info_font)

            btn_w, btn_h = 220, 56
            gap = 18
            bx = (config.SCREEN_WIDTH - btn_w) // 2
            by = (config.SCREEN_HEIGHT // 2) + 40
            rect_again = (bx, by, btn_w, btn_h)
            rect_menu  = (bx, by + btn_h + gap, btn_w, btn_h)

            button(screen, rect_again, "Chơi tiếp", btn_font)
            button(screen, rect_menu,  "Về màn hình chính", btn_font)

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if pygame.Rect(rect_again).collidepoint(mx, my):
                    # quy tắc: người thua = ĐỎ và đi trước
                    return "AGAIN", bool(loser_is_human)
                if pygame.Rect(rect_menu).collidepoint(mx, my):
                    return "MENU", None

        pygame.display.flip()
        pygame.time.delay(16)
        clock.tick(60)

# =========================
# MÀN HÌNH CHÍNH "xd" (đúng yêu cầu)
# - Có 4 chế độ: Chơi với máy, 2 người chơi, Hướng dẫn, Cài đặt
# - Sau khi thao tác thì hiển thị ra màn hình chế độ đã lựa chọn
# =========================
def xd(screen, sound: SoundManager):
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 56)
    btn_font   = pygame.font.SysFont(None, 36)
    info_font  = pygame.font.SysFont(None, 26)

    # cấu hình đơn giản cho vs AI: chọn bên và độ khó ngay trong màn hình này
    human_is_red = True
    ai_depth = 3  # mặc định

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None, None
            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        screen.fill((30, 20, 12))
        draw_center_text(screen, "CHINESE CHESS", config.SCREEN_HEIGHT // 2 - 160, title_font)
        draw_center_text(screen, "Select Mode", config.SCREEN_HEIGHT // 2 - 120, info_font, (220, 200, 160))

        btn_w, btn_h, gap = 320, 60, 18
        bx = (config.SCREEN_WIDTH - btn_w) // 2
        by = config.SCREEN_HEIGHT // 2 - 40

        rect_ai   = (bx, by, btn_w, btn_h)
        rect_2p   = (bx, by + (btn_h + gap), btn_w, btn_h)
        rect_guide= (bx, by + 2*(btn_h + gap), btn_w, btn_h)
        rect_set  = (bx, by + 3*(btn_h + gap), btn_w, btn_h)

        button(screen, rect_ai,    "Play with AI", btn_font)
        button(screen, rect_2p,    "2 players",      btn_font)
        button(screen, rect_guide, "Instructions",         btn_font)
        button(screen, rect_set,   "Settings",           btn_font)

        # Nhánh “hiển thị chế độ đã lựa chọn”:
        # - Nếu click: trả về loại chế độ để main xử lý → mở màn hình tương ứng
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if pygame.Rect(rect_ai).collidepoint(mx, my):
                sound.play_click()
                return "AI", human_is_red, ai_depth
            if pygame.Rect(rect_2p).collidepoint(mx, my):
                sound.play_click()
                return "2P", None, None
            if pygame.Rect(rect_guide).collidepoint(mx, my):
                sound.play_click()
                return "GUIDE", None, None
            if pygame.Rect(rect_set).collidepoint(mx, my):
                sound.play_click()
                return "SETTINGS", None, None

        # góc nhỏ chọn nhanh BÊN & ĐỘ KHÓ cho AI ngay ở menu (không bắt buộc)
        mini_font = pygame.font.SysFont(None, 22)
        # Toggle bên
        side_text = f"Your Side (AI): {'RED' if human_is_red else 'BLACK'}"
        st = mini_font.render(side_text, True, (220, 200, 160))
        screen.blit(st, (20, config.SCREEN_HEIGHT - 70))
        # nhấn phím S để đổi bên
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            human_is_red = not human_is_red

        # Độ khó (phím 1/2/3)
        diff_text = f"AI Difficulty (1/2/3): {ai_depth}"
        dt = mini_font.render(diff_text, True, (220, 200, 160))
        screen.blit(dt, (20, config.SCREEN_HEIGHT - 45))
        if keys[pygame.K_1]: ai_depth = 2
        if keys[pygame.K_2]: ai_depth = 3
        if keys[pygame.K_3]: ai_depth = 4

        pygame.display.flip()
        clock.tick(60)

# =========================
# HƯỚNG DẪN (ngắn gọn theo yêu cầu)
# =========================
def guide(screen):
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 50)
    body_font  = pygame.font.SysFont(None, 24)
    btn_font   = pygame.font.SysFont(None, 32)

    lines = [
        "- Tướng/Soái (將/帥): đi 1 ô trong Cung 3x3; không được đối mặt trực tiếp.",
        "- Sĩ (士/仕): đi chéo 1 ô, chỉ trong Cung.",
        "- Tượng (象/相): đi chéo 2 ô (không qua sông), không bị chặn giữa.",
        "- Xe (車/俥): đi thẳng theo hàng/cột.",
        "- Mã (馬/傌): đi chữ L (1-2), bị chặn 'chân mã'.",
        "- Pháo (炮/包/砲): đi như Xe; khi ăn phải có đúng 1 quân ngăn giữa.",
        "- Tốt/Binh (卒/兵): đi 1 ô thẳng; qua sông được đi ngang 1 ô.",
        "Chiếu hết khi đối phương không có nước đi hợp lệ và bị chiếu.",
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        screen.fill((28, 20, 12))
        draw_center_text(screen, "HƯỚNG DẪN", 90, title_font)
        y = 150
        for line in lines:
            surf = body_font.render(line, True, (230, 210, 180))
            screen.blit(surf, (60, y))
            y += 28

        rect_back = ((config.SCREEN_WIDTH - 220)//2, y + 30, 220, 56)
        button(screen, rect_back, "Về màn hình chính", btn_font)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if pygame.Rect(rect_back).collidepoint(mx, my):
                return "MENU"

        pygame.display.flip()
        clock.tick(60)

# =========================
# MAIN (đúng mô tả đề)
# - Mở xd() để chọn chế độ
# - Vào chơi (Đỏ đi trước – Đen đi sau)
# - Kết thúc: hiển thị Thắng/Thua + Chơi tiếp/Về menu
# - “Chơi tiếp”: người THUA = ĐỎ & đi trước
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Cờ Tướng")
    sound = SoundManager()

    while True:
        mode, human_is_red, ai_depth = xd(screen, sound)
        if mode == "QUIT":
            break
        elif mode == "SETTINGS":
            s = setting(screen, sound)
            if s == "QUIT":
                break
            else:
                continue
        elif mode == "GUIDE":
            g = guide(screen)
            if g == "QUIT":
                break
            else:
                continue
        elif mode == "2P":
            # 2 người chơi: không chọn bên, Đỏ đi trước
            action, loser_is_human = run_match(screen, sound, human_is_red=None, ai_depth=None)
            if action == "QUIT":
                break
            # chơi tiếp nếu chọn AGAIN
            while action == "AGAIN":
                # người thua trở thành ĐỎ và đi trước (ở 2P cả 2 đều là human → cứ coi loser_is_human=True để hợp quy tắc)
                action, loser_is_human = run_match(screen, sound, human_is_red=True, ai_depth=None)
                if action in ("QUIT", "MENU"):
                    break
            if action == "QUIT":
                break
        elif mode == "AI":
            # chơi với máy: đã có human_is_red, ai_depth từ xd()
            action, loser_is_human = run_match(screen, sound, human_is_red=human_is_red, ai_depth=ai_depth)
            if action == "QUIT":
                break
            while action == "AGAIN":
                # người thua là ĐỎ & đi trước
                again_human_is_red = bool(loser_is_human)
                action, loser_is_human = run_match(screen, sound, human_is_red=again_human_is_red, ai_depth=ai_depth)
                if action in ("QUIT", "MENU"):
                    break
            if action == "QUIT":
                break

    pygame.quit()

if __name__ == "__main__":
    main()
