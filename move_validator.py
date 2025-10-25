class MoveValidator:
    @staticmethod
    def is_king_in_check(king_pos, pieces, other_pieces):
        """Kiểm tra xem tướng có bị chiếu không."""
        for pos, piece in other_pieces.items():
            if MoveValidator.is_valid_move(piece, pos, king_pos, other_pieces, pieces):
                return True  # Có ít nhất một quân đang chiếu tướng
        if MoveValidator.are_kings_facing(pieces, other_pieces):
            return True
        return False

    @staticmethod
    def is_valid_move(piece, current_pos, new_pos, pieces, other_pieces):
        x, y = current_pos
        new_x, new_y = new_pos

        # Thêm điều kiện: Không di chuyển vào ô có quân cùng màu
        if new_pos in pieces:
            return False

        if piece in ["卒", "兵"]:  # Tốt/Binh
            direction = 1 if piece == "卒" else -1  # Tốt (卒) đi xuống, Binh (兵) đi lên
            if new_x == x and new_y == y + direction:
                return True  # Đi thẳng bình thường
            if (piece == "卒" and y >= 5) or (piece == "兵" and y <= 4):
                # Nếu đã qua sông, cho phép đi ngang
                if abs(new_x - x) == 1 and new_y == y:
                    return True
            return False

        elif piece in ["將", "帥"]:  # Tướng/Soái
            dx = abs(new_x - x)
            dy = abs(new_y - y)
            if piece == "將":
                if not (3 <= new_x <= 5 and 0 <= new_y <= 2):
                    return False
            if piece == "帥":
                if not (3 <= new_x <= 5 and 7 <= new_y <= 9):
                    return False
            return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

        elif piece == "車":  # Xe
            if new_x == x:  # Đi dọc
                step = 1 if new_y > y else -1
                for i in range(y + step, new_y, step):
                    if (x, i) in pieces or (x, i) in other_pieces:
                        return False
            elif new_y == y:  # Đi ngang
                step = 1 if new_x > x else -1
                for i in range(x + step, new_x, step):
                    if (i, y) in pieces or (i, y) in other_pieces:
                        return False
            else:
                return False
            return True

        elif piece == "馬":  # Mã
            dx = abs(new_x - x)
            dy = abs(new_y - y)
            if dx == 2 and dy == 1:  # Nhảy ngang trước, dọc sau
                if (x + (new_x - x) // 2, y) in pieces or (x + (new_x - x) // 2, y) in other_pieces:
                    return False
            elif dx == 1 and dy == 2:  # Nhảy dọc trước, ngang sau
                if (x, y + (new_y - y) // 2) in pieces or (x, y + (new_y - y) // 2) in other_pieces:
                    return False

            return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)

        elif piece in ["象", "相"]:  # Tượng/Tướng
            dx = abs(new_x - x)
            dy = abs(new_y - y)
            if piece == "象":
                if not (0 <= new_x <= 8 and 0 <= new_y <= 4):
                    return False
            if piece == "相":
                if not (0 <= new_x <= 8 and 5 <= new_y <= 9):
                    return False
            return dx == 2 and dy == 2

        elif piece in ["士", "仕"]:  # Sĩ
            dx = abs(new_x - x)
            dy = abs(new_y - y)
            if piece == "士":
                if not (3 <= new_x <= 5 and 0 <= new_y <= 2):
                    return False
            if piece == "仕":
                if not (3 <= new_x <= 5 and 7 <= new_y <= 9):
                    return False
            return dx == 1 and dy == 1

        elif piece in ["包", "炮"]:  # Pháo
            count = 0
            if new_x == x:  # Đi dọc
                step = 1 if new_y > y else -1
                for i in range(y + step, new_y, step):
                    if (x, i) in pieces or (x, i) in other_pieces:
                        count += 1
            elif new_y == y:  # Đi ngang
                step = 1 if new_x > x else -1
                for i in range(x + step, new_x, step):
                    if (i, y) in pieces or (i, y) in other_pieces:
                        count += 1
            else:
                return False
            if new_pos in other_pieces:  # Ăn quân
                return count == 1  # Phải có đúng 1 quân cản
            return count == 0  # Đi thường thì không được có quân cản
        
        final_valid_moves = []
        king_pos = next((pos for pos, p in pieces.items() if p in ["帥", "將"]), None)

        if king_pos is None: # Không tìm thấy Tướng, có thể là lỗi
            return valid_moves

        for move in valid_moves:
            # Tạo bản sao để mô phỏng nước đi
            temp_pieces = pieces.copy()
            temp_other_pieces = other_pieces.copy()

            # Di chuyển quân
            moved_piece = temp_pieces.pop(current_pos)
            temp_pieces[move] = moved_piece

            # Xóa quân đối phương nếu bị ăn
            if move in temp_other_pieces:
                temp_other_pieces.pop(move)

            # Cập nhật vị trí Tướng nếu Tướng di chuyển
            current_king_pos = move if current_pos == king_pos else king_pos

            # Nếu nước đi không làm Tướng bị chiếu, thì mới thêm vào danh sách cuối cùng
            if not MoveValidator.is_king_in_check(current_king_pos, temp_pieces, temp_other_pieces):
                final_valid_moves.append(move)

        return final_valid_moves
    @staticmethod
    def are_kings_facing(pieces, other_pieces):
        #Kiểm tra xem hai tướng có đối mặt nhau không
        #Tìm vị trí hai tướng
        try:
            king_pos = next(pos for pos, p in pieces.items() if p in ["帥", "將"])
            other_king_pos = next(pos for pos, p in other_pieces.items() if p in ["帥", "將"])
        except StopIteration:
            return False #Nếu không tìm thấy tướng thì bỏ qua
        
        #Nếu không cùng cột, chắc chắn không lộ mặt
        if king_pos[0] != other_king_pos[0]:
            return False
        
        #Kiểm tra xem có quân nào cản không
        start_y = min(king_pos[1], other_king_pos[1])
        end_y = max(king_pos[1], other_king_pos[1])

        for y in range(start_y + 1, end_y):
            if (king_pos[0], y) in pieces or (king_pos[0], y) in other_pieces:
                return False #Có quân cản -> Không lộ mặt
            
        return True

    @staticmethod
    def generate_valid_moves(piece, current_pos, pieces, other_pieces):
        """Trả về danh sách nước đi hợp lệ."""
        x, y = current_pos
        valid_moves = []

        # Thêm điều kiện lọc: Loại bỏ các ô có quân cùng màu
        def is_valid(new_x, new_y):
            return (new_x, new_y) not in pieces

        if piece == "馬":
            moves_to_check = [(x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
                              (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2)]
            for new_x, new_y in moves_to_check:
                if 0 <= new_x < 9 and 0 <= new_y < 10:
                    # Kiểm tra cản trở của Mã
                    if not ((abs(new_x - x) == 2 and abs(new_y - y) == 1 and
                             (x + (new_x - x) // 2, y) in pieces or (x + (new_x - x) // 2, y) in other_pieces) or
                            (abs(new_x - x) == 1 and abs(new_y - y) == 2 and
                             (x, y + (new_y - y) // 2) in pieces or (x, y + (new_y - y) // 2) in other_pieces)):

                        if MoveValidator.is_valid_move(piece, current_pos, (new_x, new_y), pieces, other_pieces):
                            valid_moves.append((new_x, new_y))

        elif piece == "車":
            for i in range(-8, 9):  # Kiểm tra theo chiều ngang
                if i != 0:
                    new_x = x + i
                    if 0 <= new_x < 9:
                        # Kiểm tra cản trở của Xe
                        blocked = False
                        step = 1 if i > 0 else -1
                        for j in range(x + step, new_x, step):
                            if (j, y) in pieces or (j, y) in other_pieces:
                                blocked = True
                                break
                        if not blocked and MoveValidator.is_valid_move(piece, current_pos, (new_x, y), pieces,
                                                                       other_pieces):
                            valid_moves.append((new_x, y))

            for i in range(-9, 10):  # Kiểm tra theo chiều dọc
                if i != 0:
                    new_y = y + i
                    if 0 <= new_y < 10:
                        # Kiểm tra cản trở của Xe
                        blocked = False
                        step = 1 if i > 0 else -1
                        for j in range(y + step, new_y, step):
                            if (x, j) in pieces or (x, j) in other_pieces:
                                blocked = True
                                break
                        if not blocked and MoveValidator.is_valid_move(piece, current_pos, (x, new_y), pieces,
                                                                       other_pieces):
                            valid_moves.append((x, new_y))

        elif piece in ["帥", "將"]:
            potential_moves = [(x + dx, y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

            for new_pos in potential_moves:
                new_x, new_y = new_pos

                # Kiểm tra xem Tướng có trong cung không
                if not (0 <= new_x < 9 and 0 <= new_y < 10):
                    continue
                if not MoveValidator.is_valid_move(piece, current_pos, new_pos, pieces, other_pieces):
                    continue

                # Tạo trạng thái bàn cờ giả định sau khi tướng di chuyển
                temp_pieces = pieces.copy()
                temp_pieces[new_pos] = temp_pieces.pop(current_pos)

                # Kiểm tra xem ở vị trí mới, Tướng có bị chiếu không
                if not MoveValidator.is_king_in_check(new_pos, temp_pieces, other_pieces):
                    valid_moves.append(new_pos)

        elif piece in ["士", "仕"]:
            moves_to_check = [(x + i, y + j) for i in [-1, 1] for j in [-1, 1]]
            for new_x, new_y in moves_to_check:
                if 0 <= new_x < 9 and 0 <= new_y < 10:
                    if MoveValidator.is_valid_move(piece, current_pos, (new_x, new_y), pieces, other_pieces):
                        valid_moves.append((new_x, new_y))

        elif piece in ["象", "相"]:
            moves_to_check = [(x + i * 2, y + j * 2) for i in [-1, 1] for j in [-1, 1]]
            for new_x, new_y in moves_to_check:
                if 0 <= new_x < 9 and 0 <= new_y < 10:
                    # Kiểm tra cản trở của Tượng/Tướng
                    if not ((x + (new_x - x) // 2, y + (new_y - y) // 2) in pieces or
                            (x + (new_x - x) // 2,
                             y + (new_y - y) // 2) in other_pieces) and MoveValidator.is_valid_move(piece, current_pos,
                                                                                                    (new_x, new_y),
                                                                                                    pieces,
                                                                                                    other_pieces):
                        valid_moves.append((new_x, new_y))

        elif piece in ["卒", "兵"]:
            direction = 1 if piece == "卒" else -1
            moves_to_check = [(x, y + direction)]
            if (piece == "卒" and y >= 5) or (piece == "兵" and y <= 4):
                moves_to_check.extend([(x + 1, y), (x - 1, y)])  # Thêm nước đi ngang khi qua sông
            for new_x, new_y in moves_to_check:
                if 0 <= new_x < 9 and 0 <= new_y < 10:
                    if MoveValidator.is_valid_move(piece, current_pos, (new_x, new_y), pieces, other_pieces):
                        valid_moves.append((new_x, new_y))

        elif piece in ["包", "炮"]:
            for i in range(-8, 9):  # Kiểm tra theo chiều ngang
                if i != 0:
                    new_x = x + i
                    if 0 <= new_x < 9:
                        valid_moves.append((new_x, y))  # Thêm vào danh sách để kiểm tra sau

            for i in range(-9, 10):  # Kiểm tra theo chiều dọc
                if i != 0:
                    new_y = y + i
                    if 0 <= new_y < 10:
                        valid_moves.append((x, new_y))  # Thêm vào danh sách để kiểm tra sau

            # Lọc các nước đi của Pháo dựa trên điều kiện cản
            valid_moves_filtered = []
            for new_x, new_y in valid_moves:
                count = 0
                if new_x == x:  # Đi dọc
                    step = 1 if new_y > y else -1
                    for i in range(y + step, new_y, step):
                        if (x, i) in pieces or (x, i) in other_pieces:
                            count += 1
                elif new_y == y:  # Đi ngang
                    step = 1 if new_x > x else -1
                    for i in range(x + step, new_x, step):
                        if (i, y) in pieces or (i, y) in other_pieces:
                            count += 1
                if (new_x, new_y) in other_pieces:  # Ăn quân
                    if count == 1 and MoveValidator.is_valid_move(piece, current_pos, (new_x, new_y), pieces,
                                                                  other_pieces):
                        valid_moves_filtered.append((new_x, new_y))
                elif count == 0 and MoveValidator.is_valid_move(piece, current_pos, (new_x, new_y), pieces,
                                                                other_pieces):  # Đi thường
                    valid_moves_filtered.append((new_x, new_y))
            return valid_moves_filtered

        return valid_moves