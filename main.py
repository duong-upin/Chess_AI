import pygame
import config
from ai import ChessAI
from pieces import PieceData
from move_validator import MoveValidator
from board import GameBoard
from timer_manager import TimerManager
from captured_pieces import CapturedPieces

# =========================
# MÀN HÌNH KẾT THÚC (UI đẹp)
# =========================
def draw_game_over_ui(screen, winner_text, loser_text):
    import pygame
    import config

    # ===== FONT =====
    title_font = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 64)   # In đậm, to
    sub_font   = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 32)
    btn_font   = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 28)

    # ===== MÀU =====
    bg_color     = (30, 20, 12)
    title_color  = (255, 215, 100)     # vàng sáng
    sub_color    = (220, 200, 160)     # xám vàng nhẹ
    btn_bg       = (90, 60, 20)
    btn_hover_bg = (130, 85, 35)
    btn_text     = (255, 255, 255)

    # ===== LAYOUT =====
    screen.fill(bg_color)
    center_x = config.SCREEN_WIDTH // 2
    center_y = config.SCREEN_HEIGHT // 2

    # "GAME OVER"
    game_over_surf = title_font.render("GAME OVER", True, (255, 255, 255))
    game_over_rect = game_over_surf.get_rect(center=(center_x, center_y - 150))
    screen.blit(game_over_surf, game_over_rect)

    # Winner / Loser text
    win_surf = title_font.render(winner_text.upper(), True, title_color)
    win_rect = win_surf.get_rect(center=(center_x, center_y - 70))
    screen.blit(win_surf, win_rect)

    lose_surf = sub_font.render(loser_text.upper(), True, sub_color)
    lose_rect = lose_surf.get_rect(center=(center_x, center_y - 25))
    screen.blit(lose_surf, lose_rect)

    # ===== BUTTONS =====
    def draw_button(text, rect):
        mx, my = pygame.mouse.get_pos()
        is_hover = pygame.Rect(rect).collidepoint(mx, my)
        bg = btn_hover_bg if is_hover else btn_bg
        pygame.draw.rect(screen, bg, rect, border_radius=12)
        label = btn_font.render(text, True, btn_text)
        screen.blit(label, label.get_rect(center=pygame.Rect(rect).center))
        return is_hover

    btn_w, btn_h = 240, 56
    gap = 18
    rect_again = (center_x - btn_w // 2, center_y + 40, btn_w, btn_h)
    rect_menu  = (center_x - btn_w // 2, center_y + 40 + btn_h + gap, btn_w, btn_h)

    hover_again = draw_button("New Game", rect_again)
    hover_menu  = draw_button("Back to Main Menu", rect_menu)

    pygame.display.flip()

    # ===== XỬ LÝ EVENT =====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if pygame.Rect(rect_again).collidepoint(mx, my):
                return "AGAIN"
            elif pygame.Rect(rect_menu).collidepoint(mx, my):
                return "MENU"
    return None


# =========================
# UI helpers
# =========================
def get_vn_font(size, bold=False):
    # Ưu tiên system fonts có hỗ trợ tiếng Việt
    candidates = ["Segoe UI", "Arial", "Tahoma", "Roboto", "Noto Sans", "DejaVu Sans", "Verdana", "Times New Roman"]
    for name in candidates:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    # Fallback: nếu bạn có kèm font trong assets (khuyến nghị thêm 1 file)
    try:
        return pygame.font.Font("assets/fonts/DejaVuSans.ttf", size)
    except Exception:
        pass
    # Cuối cùng mới dùng SysFont (ít chắc chắn về glyph)
    return pygame.font.SysFont(None, size, bold=bold)

def draw_center_text(screen, text, y, font, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)

def button(screen, rect, text, font, bg=(90, 60, 20), fg=(255, 255, 255),
           hover_bg=(120, 80, 30), hit_pad=10):
    x, y, w, h = rect
    mx, my = pygame.mouse.get_pos()

    # vùng click mở rộng thêm hit_pad px mỗi cạnh
    hit_rect = pygame.Rect(x - hit_pad, y - hit_pad, w + hit_pad*2, h + hit_pad*2)
    is_hover = hit_rect.collidepoint(mx, my)

    pygame.draw.rect(screen, hover_bg if is_hover else bg, rect, border_radius=12)
    label = font.render(text, True, fg)
    screen.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))

    return hit_rect   # trả về rect mở rộng để xử lý click


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

    slider_rect = pygame.Rect(180, 220, max(300, config.SCREEN_WIDTH - 360), 8)

    while True:
        # TÍNH LẠI RECT CỦA NÚT MỖI FRAME (để hỗ trợ resize)
        btn_w, btn_h = 260, 56
        bx = (config.SCREEN_WIDTH - btn_w) // 2
        rect_preview = (bx, 270, btn_w, btn_h)
        rect_skin    = (bx, 340, btn_w, btn_h)
        rect_toggle  = (bx, 410, btn_w, btn_h)
        rect_back    = (bx, 480, btn_w, btn_h)

        # ========== VÒNG SỰ KIỆN ==========
        for event in pygame.event.get():
            HIT_PAD = 12  # nới vùng click nút ~12px mỗi cạnh
            if event.type == pygame.QUIT:
                return "QUIT"

            

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Slider: nới hitbox theo chiều dọc để dễ bấm
                slider_hit = slider_rect.inflate(0, 24)
                if slider_hit.collidepoint(mx, my):
                    ratio = (mx - slider_rect.x) / max(1, slider_rect.width)
                    ratio = max(0.0, min(1.0, ratio))  # clamp 0..1
                    sound.set_volume(ratio)
                    sound.play_click()

                # Preview
                elif pygame.Rect(rect_preview).inflate(HIT_PAD*2, HIT_PAD*2).collidepoint(mx, my):
                    sound.play_click()

                # Skin placeholder
                elif pygame.Rect(rect_skin).inflate(HIT_PAD*2, HIT_PAD*2).collidepoint(mx, my):
                    sound.play_click()

                # Toggle per-piece sound
                elif pygame.Rect(rect_toggle).inflate(HIT_PAD*2, HIT_PAD*2).collidepoint(mx, my):
                    sound.per_piece_sound = not sound.per_piece_sound
                    sound.play_click()

                # Back to menu
                elif pygame.Rect(rect_back).inflate(HIT_PAD*2, HIT_PAD*2).collidepoint(mx, my):
                    sound.play_click()
                    return "MENU"

        # ========== VẼ UI ==========
        screen.fill((26, 18, 10))
        draw_center_text(screen, "SETTINGS", 90, title_font)
        draw_center_text(screen, f"Volume: {int(sound.volume * 100)}%", 160, label_font, (220, 200, 160))

        pygame.draw.rect(screen, (70, 50, 30), slider_rect, border_radius=8)
        knob_x = int(slider_rect.x + slider_rect.width * sound.volume)
        pygame.draw.circle(screen, (200, 180, 140), (knob_x, slider_rect.y + slider_rect.height // 2), 12)

        # Vẽ nút + lấy hitbox mở rộng (vd: 12px)
        hit_preview = button(screen, rect_preview, "Preview Click", btn_font, hit_pad=12)
        hit_skin    = button(screen, rect_skin, "Change Skin", btn_font, hit_pad=12)
        hit_toggle  = button(screen, rect_toggle, f"Capture Sound: {'ON' if sound.per_piece_sound else 'OFF'}", btn_font, hit_pad=12)
        hit_back    = button(screen, rect_back, "Back to Main Menu", btn_font, hit_pad=12)

        pygame.display.flip()
        clock.tick(60)

# =========================
# CHẾ ĐỘ CHƠI (VS AI / 2P) – phục vụ cho main và xd
# =========================
        # Kết thúc → màn hình kết quả + lựa chọn
def run_match(screen, sound: SoundManager, human_is_red: bool | None, ai_depth: int | None):
    """
    Chạy 1 ván:
      - Đỏ luôn đi trước, Đen đi sau.
      - Nếu kết thúc: hiển thị Thắng/Thua + chọn 'New game' hoặc 'Back to Main Menu'.
      - Nếu 'New game': người thua = ĐỎ và đi trước ván sau.
    human_is_red: True/False khi chơi với máy; None khi 2 người chơi (cả 2 đều là human).
    ai_depth: độ sâu minimax nếu vs AI; None nếu 2 người chơi.
    Trả về: ('MENU'|'QUIT'|'AGAIN', loser_is_human_bool_or_None)
    """
    clock = pygame.time.Clock()

    # UI fonts cho phần in-game (không phải Game Over)
    title_font = pygame.font.SysFont(None, 56)
    btn_font   = pygame.font.SysFont(None, 36)
    info_font  = pygame.font.SysFont(None, 28)

    board    = GameBoard(screen)
    timer    = TimerManager(600)  # 10 phút mỗi bên
    captured = CapturedPieces(screen)
    black_pieces, red_pieces = PieceData.get_initial_pieces()

    # Thiết lập AI (nếu có)
    ai = None
    if ai_depth is not None:
        # AI sẽ là phía còn lại của human
        ai = ChessAI(is_red=not human_is_red)
    depth_default = ai_depth if ai_depth is not None else 3

    red_turn      = True       # Đỏ đi trước
    selected      = None
    valid_moves   = []
    turn_count    = 0

    # Thông tin kết thúc ván
    winner_text      = ""
    loser_text       = ""
    loser_is_human   = None
    playing          = True

    while True:
        # ===== EVENT =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None

            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                board.screen = screen
                captured.screen = screen

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and playing:
                sound.play_click()
                x, y = pygame.mouse.get_pos()

                # Tăng độ "dễ click": làm tròn về ô gần nhất
                gx = round((x - config.BOARD_X) / config.CELL_SIZE)
                gy = round((y - config.BOARD_Y) / config.CELL_SIZE)

                # Ngoài bàn cờ thì bỏ
                if gx < 0 or gx >= 9 or gy < 0 or gy >= 10:
                    continue

                # Nếu có AI: chỉ thao tác khi là lượt của người
                if ai is not None:
                    is_human_turn = (human_is_red and red_turn) or ((not human_is_red) and (not red_turn))
                    if not is_human_turn:
                        continue

                # Tập quân theo lượt
                pieces = red_pieces if red_turn else black_pieces
                other  = black_pieces if red_turn else red_pieces

                # Chọn quân hoặc đi quân
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

                        # Ăn vua -> kết thúc
                        if captured_piece in ["將", "帥"]:
                            if captured_piece == "將":  # ăn Vua đen
                                winner_text = "YOU WIN"
                                loser_text  = "YOU LOSE"
                                loser_is_human = (ai is None) or (not human_is_red)
                            else:                        # ăn Soái đỏ
                                winner_text = "YOU WIN" if not red_turn else "YOU WIN"
                                # ở đây vẫn hiển thị YOU WIN / YOU LOSE
                                loser_text  = "YOU LOSE"
                                loser_is_human = (ai is None) or (human_is_red)
                            pieces[(gx, gy)] = pieces.pop(selected)
                            playing = False
                        else:
                            # Di chuyển bình thường sau khi ăn
                            pieces[(gx, gy)] = pieces.pop(selected)
                            selected = None
                            valid_moves = []
                            red_turn = not red_turn
                            timer.switch_turn()
                            turn_count += 1
                            continue  # quay lại loop

                    if playing:
                        # Di chuyển thường
                        pieces[(gx, gy)] = pieces.pop(selected)
                        selected = None
                        valid_moves = []
                        red_turn = not red_turn
                        timer.switch_turn()
                        turn_count += 1

        # ===== UPDATE TIMER =====
        if playing:
            timer.update_timers()
            rt, bt = timer.get_times()

            # Hết giờ -> kết thúc
            if rt <= 0:
                winner_text = "YOU WIN"      # Đen thắng vì Đỏ hết giờ
                loser_text  = "YOU LOSE"
                loser_is_human = (ai is None) or (human_is_red is True)
                playing = False
            elif bt <= 0:
                winner_text = "YOU WIN"      # Đỏ thắng vì Đen hết giờ
                loser_text  = "YOU LOSE"
                loser_is_human = (ai is None) or (human_is_red is False)
                playing = False

        # ===== LƯỢT AI =====
        if playing and ai is not None:
            is_ai_turn = (ai.is_red and red_turn) or ((not ai.is_red) and (not red_turn))
            if is_ai_turn:
                pygame.time.delay(350)  # nhẹ nhàng
                try:
                    _, move = ai.minimax(red_pieces, black_pieces, depth_default, float('-inf'), float('inf'), ai.is_red)
                except Exception:
                    move = ai.get_best_move(red_pieces, black_pieces, depth=depth_default)

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
                                winner_text = "YOU WIN"    # phía AI thắng; UI vẫn hiển thị YOU WIN / YOU LOSE
                                loser_text  = "YOU LOSE"
                                loser_is_human = (ai is not None and ((human_is_red and not ai.is_red) or ((not human_is_red) and ai.is_red)))
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

        # ===== VẼ BÀN + TIMER =====
        board.draw_board(black_pieces, red_pieces, valid_moves)
        captured.draw_captured_pieces()
        rt, bt = timer.get_times()
        board.draw_timer(rt, bt, red_turn)


        # ===== MÀN HÌNH KẾT THÚC (UI ĐẸP + NÚT) =====
        if not playing:
            # fonts dùng helper có dấu; fallback SysFont nếu thiếu
            title_font = get_vn_font(56, bold=True) if 'get_vn_font' in globals() else pygame.font.SysFont(None, 56)
            btn_font   = get_vn_font(36)            if 'get_vn_font' in globals() else pygame.font.SysFont(None, 36)
            info_font  = get_vn_font(28)            if 'get_vn_font' in globals() else pygame.font.SysFont(None, 28)

            # toạ độ buttons
            btn_w, btn_h = 240, 56
            gap = 18
            bx = (config.SCREEN_WIDTH - btn_w) // 2
            by = (config.SCREEN_HEIGHT // 2) + 40
            rect_again = (bx, by, btn_w, btn_h)
            rect_menu  = (bx, by + btn_h + gap, btn_w, btn_h)

            HIT_PAD     = 12          # mở rộng vùng click
            cooldown_ms = 500         # tránh ăn nhầm click trước đó
            start_ts    = pygame.time.get_ticks()
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)

            # vòng lặp màn hình kết thúc
            while True:
                screen.fill((30, 20, 12))
                # Title
                draw_center_text(screen, "GAME OVER", config.SCREEN_HEIGHT // 2 - 120, title_font)
                # YOU WIN (vàng nổi) / YOU LOSE (xám vàng)
                draw_center_text(screen, winner_text, config.SCREEN_HEIGHT // 2 - 30, btn_font, (255, 215, 100))

                # Buttons (đẹp hơn + hover)
                # nhỏ hơn nhưng đậm hơn
                small_bold_font = get_vn_font(20, bold=True) if 'get_vn_font' in globals() else pygame.font.SysFont(None, 28, bold=True)

                hit_again = button(screen, rect_again, "New game", small_bold_font, hit_pad=HIT_PAD)
                hit_menu  = button(screen, rect_menu,  "Back to Main Menu", small_bold_font, hit_pad=HIT_PAD)


                now = pygame.time.get_ticks()
                accepting_clicks = (now - start_ts) >= cooldown_ms

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "QUIT", None

                    elif event.type == pygame.KEYDOWN and accepting_clicks:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            return "AGAIN", bool(loser_is_human)
                        if event.key in (pygame.K_ESCAPE, pygame.K_m):
                            return "MENU", None

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and accepting_clicks:
                        mx, my = event.pos
                        if hit_again.collidepoint(mx, my):
                            return "AGAIN", bool(loser_is_human)
                        elif hit_menu.collidepoint(mx, my):
                            return "MENU", None

                clock.tick(60)
        pygame.display.flip()
        clock.tick(60)

    # Fallback an toàn nếu lỡ thoát vòng mà chưa return
    return "MENU", None

                    


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
    mini_font  = pygame.font.SysFont(None, 22)

    human_is_red = True
    ai_depth = 3
    HIT_PAD = 14

    while True:
        screen.fill((30, 20, 12))
        draw_center_text(screen, "CHINESE CHESS", config.SCREEN_HEIGHT // 2 - 160, title_font)
        draw_center_text(screen, "Select Mode",  config.SCREEN_HEIGHT // 2 - 120, info_font, (220, 200, 160))

        btn_w, btn_h, gap = 320, 60, 18
        bx = (config.SCREEN_WIDTH - btn_w) // 2
        by = config.SCREEN_HEIGHT // 2 - 40

        rect_ai    = (bx, by, btn_w, btn_h)
        rect_2p    = (bx, by + (btn_h + gap), btn_w, btn_h)
        rect_guide = (bx, by + 2*(btn_h + gap), btn_w, btn_h)
        rect_set   = (bx, by + 3*(btn_h + gap), btn_w, btn_h)

        # Vẽ nút và NHẬN hitbox mở rộng trước khi xử lý event
        hit_ai    = button(screen, rect_ai,    "Play with AI",  btn_font, hit_pad=HIT_PAD)
        hit_2p    = button(screen, rect_2p,    "2 players",     btn_font, hit_pad=HIT_PAD)
        hit_guide = button(screen, rect_guide, "Instructions",  btn_font, hit_pad=HIT_PAD)
        hit_set   = button(screen, rect_set,   "Settings",      btn_font, hit_pad=HIT_PAD)

        # Chọn bên khi đấu AI
        side_w, side_h = 140, 50
        side_gap = 20
        side_y = rect_set[1] + btn_h + 50
        side_bx = (config.SCREEN_WIDTH - (side_w*2 + side_gap)) // 2
        rect_side_red   = (side_bx, side_y, side_w, side_h)
        rect_side_black = (side_bx + side_w + side_gap, side_y, side_w, side_h)

        hit_side_red   = button(screen, rect_side_red,   "RED SIDE",   mini_font,
                                bg=(150, 50, 50) if human_is_red else (80, 40, 40), hit_pad=10)
        hit_side_black = button(screen, rect_side_black, "BLACK SIDE", mini_font,
                                bg=(50, 50, 150) if not human_is_red else (40, 40, 80), hit_pad=10)

        # Góc nhỏ: hiển thị độ khó
        diff_text = f"AI Difficulty (1/2/3): {ai_depth}"
        dt = mini_font.render(diff_text, True, (220, 200, 160))
        screen.blit(dt, (20, config.SCREEN_HEIGHT - 45))

        # ==== EVENT LOOP (sau khi đã có hit_*) ====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None, None

            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if hit_ai.collidepoint(mx, my):
                    sound.play_click()
                    return "AI", human_is_red, ai_depth
                elif hit_2p.collidepoint(mx, my):
                    sound.play_click()
                    return "2P", None, None
                elif hit_guide.collidepoint(mx, my):
                    sound.play_click()
                    return "GUIDE", None, None
                elif hit_set.collidepoint(mx, my):
                    sound.play_click()
                    return "SETTINGS", None, None
                elif hit_side_red.collidepoint(mx, my):
                    sound.play_click()
                    human_is_red = True
                elif hit_side_black.collidepoint(mx, my):
                    sound.play_click()
                    human_is_red = False

        # phím tắt đổi độ khó
        keys = pygame.key.get_pressed()
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
        "- General: move 1 square in the 3x3 Palace; cannot face directly.",
        "- Mandarin: moves one square diagonally, only in the Palace.",
        "- Elephant: moves 2 squares diagonally (not across the river), without being blocked in the middle.",
        "- Chariot: Moves straight along rows or columns any number of squares, as long as the path is clear.",
        "- Horse: Moves in an “L” shape (one square horizontally or vertically, then two squares perpendicularly); can be blocked at the “horse leg.”",
        "- Cannon: Moves like a chariot, but to capture a piece there must be exactly one piece between it and the target.",
        "- Soldier: Moves one step forward; after crossing the river, it can also move one step sideways.",
        "Checkmate: Occurs when the opponent has no legal move and their general is in check.",

    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        screen.fill((28, 20, 12))
        draw_center_text(screen, "Instructions", 90, title_font)
        y = 150
        for line in lines:
            surf = body_font.render(line, True, (230, 210, 180))
            screen.blit(surf, (60, y))
            y += 28

        rect_back = ((config.SCREEN_WIDTH - 220)//2, y + 30, 220, 56)
        button(screen, rect_back, "Back to Main Menu", btn_font)

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
