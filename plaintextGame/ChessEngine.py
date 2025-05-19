"""
Storing all the information about the current state of chess game.
Determining valid moves at current state.
It will keep move log.
"""


class GameState:
    def __init__(self):
        """
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type: 'R', 'N', 'B', 'Q', 'K', 'p' or 'D' (duck).
        "--" represents an empty space with no piece.
        Duck is represented as 'DD' (neutral color)
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        # 初始化鴨子位置 (確保不在已有棋子的位置)
        self.duck_location = (4, 4)  # 初始位置在中心
        assert self.board[self.duck_location[0]][self.duck_location[1]] == "--", "Duck initial position occupied!"
        self.board[self.duck_location[0]][self.duck_location[1]] = "DD"  # DD 表示鴨子
        self.duck_location_log = [self.duck_location]  # 鴨子位置歷史記錄

        self.moveFunctions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
            "D": self.getDuckMoves  # 使用 'D' 作為鍵對應鴨子移動
        }

        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        # 鴨子移動階段標記
        self.duck_move_phase = False  # False=棋子移動階段, True=鴨子移動階段
        self.duck_move_made = False  # 記錄當前回合是否已移動鴨子

        # 遊戲狀態標記
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []

        # En passant 相關
        self.enpassant_possible = ()  # 可進行en-passant的座標
        self.enpassant_possible_log = [self.enpassant_possible]

        # 王車易位權利
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs)]  # 修正拼寫錯誤

    def makeMove(self, move):
        """
        Takes a Move as a parameter and executes it.
        Now handles duck moves and two-phase turns.
        """
        if not move.is_duck_move:  # 普通棋子移動
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.move_log.append(move)  # log the move so we can undo it later

            # 如果是棋子移動階段，切換到鴨子移動階段，不換玩家
            if not self.duck_move_phase:
                self.duck_move_phase = True
            else:  # 如果已經是鴨子移動階段，完成後換玩家並重置階段
                self.white_to_move = not self.white_to_move
                self.duck_move_phase = False

            # update king's location if moved
            if move.piece_moved == "wK":
                self.white_king_location = (move.end_row, move.end_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.end_row, move.end_col)

            # pawn promotion
            if move.is_pawn_promotion:
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

            # enpassant move
            if move.is_enpassant_move:
                self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

            # update enpassant_possible variable
            if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
            else:
                self.enpassant_possible = ()

            # castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side castle move
                    self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
                else:  # queen-side castle move
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                    self.board[move.end_row][move.end_col - 2] = '--'

        else:  # 鴨子移動
            # 從舊位置移除鴨子
            self.board[self.duck_location[0]][self.duck_location[1]] = "--"
            # 在新位置放置鴨子
            self.board[move.end_row][move.end_col] = "DD"
            self.duck_location = (move.end_row, move.end_col)
            self.move_log.append(move)

            # 鴨子移動後換玩家並重置階段
            self.white_to_move = not self.white_to_move
            self.duck_move_phase = False

        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights - whenever it is a rook or king move
        if not move.is_duck_move:  # 鴨子移動不影響王車易位權利
            self.updateCastleRights(move)
            self.castle_rights_log.append(
                CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                             self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undoMove(self):
        """
        Undo the last move
        Now handles duck moves and two-phase turns.
        """
        if len(self.move_log) != 0:
            move = self.move_log.pop()

            if not move.is_duck_move:  # 普通棋子移動的撤銷
                self.board[move.start_row][move.start_col] = move.piece_moved
                self.board[move.end_row][move.end_col] = move.piece_captured

                # 根據移動階段調整回合狀態
                if self.duck_move_phase:  # 如果當前是鴨子階段，撤銷後應該是棋子階段
                    self.duck_move_phase = False
                else:  # 如果當前是棋子階段，撤銷後應該是上一個玩家的鴨子階段
                    self.white_to_move = not self.white_to_move
                    self.duck_move_phase = True

                # update the king's position if needed
                if move.piece_moved == "wK":
                    self.white_king_location = (move.start_row, move.start_col)
                elif move.piece_moved == "bK":
                    self.black_king_location = (move.start_row, move.start_col)

                # undo en passant move
                if move.is_enpassant_move:
                    self.board[move.end_row][move.end_col] = "--"
                    self.board[move.start_row][move.end_col] = move.piece_captured

                # undo castle rights
                self.castle_rights_log.pop()
                self.current_castling_rights = self.castle_rights_log[-1]

                # undo the castle move
                if move.is_castle_move:
                    if move.end_col - move.start_col == 2:  # king-side
                        self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                        self.board[move.end_row][move.end_col - 1] = '--'
                    else:  # queen-side
                        self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                        self.board[move.end_row][move.end_col + 1] = '--'

            else:  # 鴨子移動的撤銷
                # 將鴨子移回原來的位置
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.start_col] = "DD"
                self.duck_location = (move.start_row, move.start_col)

                # 鴨子移動撤銷後，應該是該玩家的棋子移動階段
                self.duck_move_phase = True
                # 不改變 white_to_move，因為鴨子移動是同一個回合的第二階段

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move.
        Duck moves don't affect castle rights.
        """
        # 鴨子移動不影響王車易位權利
        if move.is_duck_move:
            return

        # 如果城堡被吃掉（無論是正常吃掉還是en passant）
        if move.piece_captured == "wR":
            if move.end_col == 0:  # 左側城堡
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # 右側城堡
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # 左側城堡
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # 右側城堡
                self.current_castling_rights.bks = False

        # 如果王移動了
        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False

        # 如果城堡移動了（即使沒被吃掉，只是移動）
        elif move.piece_moved == 'wR':
            if move.start_row == 7:  # 確保是在起始行
                if move.start_col == 0:  # 左側城堡
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # 右側城堡
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:  # 確保是在起始行
                if move.start_col == 0:  # 左側城堡
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # 右側城堡
                    self.current_castling_rights.bks = False

    def getValidMoves(self):
        """
        All moves considering checks and duck blocking.
        Now handles two-phase turns (piece move and duck move).
        """
        # Save original castle rights for later restoration
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)

        moves = []

        if not self.duck_move_phase:  # Piece movement phase
            # Standard chess checks and pins
            self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

            if self.white_to_move:
                king_row, king_col = self.white_king_location
            else:
                king_row, king_col = self.black_king_location

            if self.in_check:
                if len(self.checks) == 1:  # Only 1 check, block or move king
                    moves = self.getAllPossibleMoves()
                    check = self.checks[0]
                    check_row, check_col = check[0], check[1]
                    piece_checking = self.board[check_row][check_col]
                    valid_squares = []

                    # Knight checks must be captured directly
                    if piece_checking[1] == "N":
                        valid_squares = [(check_row, check_col)]
                    else:
                        # Find squares between checking piece and king
                        for i in range(1, 8):
                            valid_square = (king_row + check[2] * i,
                                            king_col + check[3] * i)
                            valid_squares.append(valid_square)
                            if valid_square == (check_row, check_col):
                                break

                    # Filter moves that don't block check or capture checking piece
                    moves = [m for m in moves if
                             m.piece_moved[1] == "K" or
                             (m.end_row, m.end_col) in valid_squares]
                else:  # Double check, king must move
                    self.getKingMoves(king_row, king_col, moves)
            else:  # Not in check
                moves = self.getAllPossibleMoves()
                # Add castle moves if not in check
                if self.white_to_move:
                    self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
                else:
                    self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

            # Remove moves that would place/leave king in check
            moves = [m for m in moves if not self.moveMakesCheck(m)]

        else:  # Duck movement phase
            # Only allow duck moves during this phase
            moves = self.getDuckMoves()

        # Check for game end conditions
        if len(moves) == 0:
            if not self.duck_move_phase and self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
        return moves

    def moveMakesCheck(self, move):
        """檢查移動後是否會讓自己的王處於被將軍狀態"""
        # 保存當前狀態
        original_duck = self.duck_location
        original_board = [row[:] for row in self.board]
        original_white_king = self.white_king_location
        original_black_king = self.black_king_location

        # 執行臨時移動
        self.makeTempMove(move)

        # 檢查是否被將軍
        in_check = self.inCheck()

        # 恢復狀態
        self.undoTempMove(move, original_duck, original_board,
                          original_white_king, original_black_king)
        return in_check

    def inCheck(self):
        """檢查當前玩家是否被將軍，考慮鴨子阻擋"""
        king_row, king_col = self.white_king_location if self.white_to_move else self.black_king_location
        return self.squareUnderAttack(king_row, king_col)

    def squareUnderAttack(self, row, col):
        """檢查特定格子是否受到攻擊，考慮鴨子阻擋"""
        enemy_color = 'b' if self.white_to_move else 'w'

        # 檢查騎士攻擊
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece[0] == enemy_color and piece[1] == 'N':
                    return True

        # 檢查直線和斜線攻擊（車、后、象、兵、王）
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),  # 直線
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]  # 斜線

        for dr, dc in directions:
            for step in range(1, 8):
                r, c = row + dr * step, col + dc * step
                if not (0 <= r < 8 and 0 <= c < 8):
                    break

                piece = self.board[r][c]

                # 遇到鴨子就停止檢查這條線
                if piece == "DD":
                    break

                if piece != "--":
                    # 檢查攻擊類型
                    if piece[0] == enemy_color:
                        piece_type = piece[1]
                        # 直線攻擊（車或后）
                        if 0 in (dr, dc) and piece_type in ('R', 'Q'):
                            return True
                        # 斜線攻擊（象或后）
                        if dr != 0 and dc != 0 and piece_type in ('B', 'Q'):
                            return True
                        # 一步距離的國王攻擊
                        if step == 1 and piece_type == 'K':
                            return True
                        # 兵的攻擊
                        if step == 1 and piece_type == 'p':
                            pawn_dir = -1 if enemy_color == 'w' else 1
                            if dr == pawn_dir and abs(dc) == 1:
                                return True
                    break  # 遇到任何棋子就停止檢查這條線
        return False

    # 需要新增的輔助方法
    def makeTempMove(self, move):
        """執行臨時移動，不更新日誌"""
        if move.is_duck_move:
            self.board[self.duck_location[0]][self.duck_location[1]] = "--"
            self.board[move.end_row][move.end_col] = "DD"
            self.duck_location = (move.end_row, move.end_col)
        else:
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            # 更新王的位置
            if move.piece_moved == 'wK':
                self.white_king_location = (move.end_row, move.end_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.end_row, move.end_col)

    def undoTempMove(self, move, original_duck, original_board,
                     original_white_king, original_black_king):
        """撤銷臨時移動"""
        self.duck_location = original_duck
        self.board = [row[:] for row in original_board]
        self.white_king_location = original_white_king
        self.black_king_location = original_black_king

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col, considering duck blocking
        """
        original_turn = self.white_to_move
        self.white_to_move = not self.white_to_move  # switch to opponent's point of view

        # Temporarily remove duck to check attacks (since duck blocks all pieces)
        original_duck_pos = self.duck_location
        self.board[original_duck_pos[0]][original_duck_pos[1]] = "--"

        opponents_moves = self.getAllPossibleMoves()

        # Restore duck and turn
        self.board[original_duck_pos[0]][original_duck_pos[1]] = "DD"
        self.white_to_move = original_turn

        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:
                # Check if attack path is not blocked by duck
                if not self.isPathBlockedByDuck(move.start_row, move.start_col, row, col):
                    return True
        return False

    def isPathBlockedByDuck(self, start_row, start_col, end_row, end_col):
        """檢查起點和終點之間的路徑是否被鴨子阻擋"""
        # 如果起點和終點相同，直接返回False
        if start_row == end_row and start_col == end_col:
            return False

        # 計算行和列的步進方向
        dr = end_row - start_row
        dc = end_col - start_col

        # 計算步數（取行和列差值的最大值）
        steps = max(abs(dr), abs(dc))

        # 如果只有一步距離，不需要檢查路徑
        if steps <= 1:
            return False

        # 計算每一步的行列變化
        row_step = dr / steps
        col_step = dc / steps

        # 檢查路徑上的每個格子
        for step in range(1, steps):
            check_row = int(start_row + row_step * step)
            check_col = int(start_col + col_step * step)
            if (check_row, check_col) == self.duck_location:
                return True

        return False

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)

        # 過濾被鴨子阻擋的移動
        valid_moves = []
        for move in moves:
            if move.piece_moved[1] == "N":  # 騎士可以跳過鴨子
                if (move.end_row, move.end_col) != self.duck_location:
                    valid_moves.append(move)
            else:
                if not self.isPathBlockedByDuck(move.start_row, move.start_col, move.end_row, move.end_col):
                    if (move.end_row, move.end_col) != self.duck_location:
                        valid_moves.append(move)
        return valid_moves

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False

        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i

                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]

                    # Stop if we hit the duck
                    if end_piece == "DD":
                        break

                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]

                        # Check attack patterns (same as before)
                        if (0 <= j <= 3 and enemy_type == "R") or \
                                (4 <= j <= 7 and enemy_type == "B") or \
                                (i == 1 and enemy_type == "p" and (
                                        (enemy_color == "w" and 6 <= j <= 7) or
                                        (enemy_color == "b" and 4 <= j <= 5))) or \
                                (enemy_type == "Q") or \
                                (i == 1 and enemy_type == "K"):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        # Check for knight checks (must not be blocked by duck)
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2),
                        (2, -1), (2, 1), (-1, -2), (1, -2))

        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]

            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    # Check if knight's path is blocked by duck
                    if not self.isKnightPathBlocked(start_row, start_col, end_row, end_col):
                        in_check = True
                        checks.append((end_row, end_col, move[0], move[1]))

        return in_check, pins, checks

    def isKnightPathBlocked(self, start_row, start_col, end_row, end_col):
        """Check if knight's L-shape path is blocked by duck (unlikely but possible)"""
        # Knight usually can jump over pieces, but in duck chess we might want to block
        # This can be adjusted based on specific duck chess rules
        return False  # Default: knights can jump over duck

    def getPawnMoves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        Now considers duck blocking and duck's special interactions.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_location

        # 1 square forward move
        if self.board[row + move_amount][col] == "--":
            if not piece_pinned or pin_direction == (move_amount, 0):
                # Check if path is not blocked by duck
                if (row + move_amount, col) != self.duck_location:
                    moves.append(Move((row, col), (row + move_amount, col), self.board))

                    # 2 square forward move
                    if row == start_row and self.board[row + 2 * move_amount][col] == "--":
                        # Check if path is not blocked by duck
                        if (row + 2 * move_amount, col) != self.duck_location and \
                                (row + move_amount, col) != self.duck_location:
                            moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))

        # Capture moves (including en passant)
        for capture_col in [col - 1, col + 1]:
            if 0 <= capture_col <= 7:
                end_row = row + move_amount
                if not piece_pinned or pin_direction == (move_amount, capture_col - col):
                    # Normal capture
                    if self.board[end_row][capture_col][0] == enemy_color:
                        if (end_row, capture_col) != self.duck_location:  # Can't capture duck
                            moves.append(Move((row, col), (end_row, capture_col), self.board))

                    # En passant capture
                    if (end_row, capture_col) == self.enpassant_possible:
                        # Check if en passant path is not blocked by duck
                        if (row, capture_col) != self.duck_location and \
                                (end_row, capture_col) != self.duck_location:

                            attacking_piece = blocking_piece = False
                            if king_row == row:
                                if king_col < col:  # king is left of the pawn
                                    inside_range = range(king_col + 1, col - 1 if capture_col < col else col)
                                    outside_range = range(col + 1, 8) if capture_col > col else range(col - 2, -1, -1)
                                else:  # king right of the pawn
                                    inside_range = range(king_col - 1, col + 1 if capture_col > col else col, -1)
                                    outside_range = range(col - 1, -1, -1) if capture_col < col else range(col + 2, 8)

                                for i in inside_range:
                                    if self.board[row][i] != "--":
                                        blocking_piece = True
                                for i in outside_range:
                                    square = self.board[row][i]
                                    if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                        attacking_piece = True
                                    elif square != "--":
                                        blocking_piece = True

                            if not attacking_piece or blocking_piece:
                                moves.append(
                                    Move((row, col), (end_row, capture_col), self.board, is_enpassant_move=True))


    def getRookMoves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        Now considers duck blocking.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":  # don't remove pin for queen
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    # Stop if path is blocked by duck
                    if (end_row, end_col) == self.duck_location:
                        break

                    if not piece_pinned or pin_direction == direction or pin_direction == (
                    -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        Knights can jump over duck but can't land on it.
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2),
                        (2, -1), (2, 1), (-1, -2), (1, -2))
        ally_color = "w" if self.white_to_move else "b"

        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    # Can't land on duck but can jump over
                    if (end_row, end_col) != self.duck_location:
                        end_piece = self.board[end_row][end_col]
                        if end_piece[0] != ally_color:  # enemy or empty
                            moves.append(Move((row, col), (end_row, end_col), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        Now considers duck blocking.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals
        enemy_color = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    # Stop if path is blocked by duck
                    if (end_row, end_col) == self.duck_location:
                        break

                    if not piece_pinned or pin_direction == direction or pin_direction == (
                    -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        Combines rook and bishop moves, already duck-aware.
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        Now considers duck blocking and can't move to duck position.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"

        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]

            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                # Can't move to duck position
                if (end_row, end_col) == self.duck_location:
                    continue

                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece (empty or enemy)
                    # Temporarily move king to check for safety
                    original_king_pos = self.white_king_location if ally_color == "w" else self.black_king_location

                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)

                    in_check, pins, checks = self.checkForPinsAndChecks()

                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

                    # Restore king position
                    if ally_color == "w":
                        self.white_king_location = original_king_pos
                    else:
                        self.black_king_location = original_king_pos

    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        Now considers duck blocking the castle path.
        """
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check

        # Kingside castle
        if (self.white_to_move and self.current_castling_rights.wks) or \
                (not self.white_to_move and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)

        # Queenside castle
        if (self.white_to_move and self.current_castling_rights.wqs) or \
                (not self.white_to_move and self.current_castling_rights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        """ Kingside castle - duck aware """
        # Check if squares between king and rook are empty and not attacked
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            # Check if squares are not occupied by duck
            if (row, col + 1) != self.duck_location and (row, col + 2) != self.duck_location:
                # Check if squares are not under attack
                if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                    moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, row, col, moves):
        """ Queenside castle - duck aware """
        # Check if squares between king and rook are empty and not attacked
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            # Check if squares are not occupied by duck
            if (row, col - 1) != self.duck_location and (row, col - 2) != self.duck_location:
                # Check if squares are not under attack (only col-1 and col-2 matter)
                if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                    moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

    def getDuckMoves(self):
        """
        Get all possible duck moves.
        Duck can TELEPORT to any empty square on the board.
        """
        moves = []
        current_row, current_col = self.duck_location

        # Check every square on the board
        for end_row in range(8):
            for end_col in range(8):
                # Can teleport to any empty square except current position
                if self.board[end_row][end_col] == "--" and (end_row, end_col) != (current_row, current_col):
                    moves.append(Move((current_row, current_col), (end_row, end_col), self.board, is_duck_move=True))

        return moves


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False,
                 is_castle_move=False, is_duck_move=False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # 鴨子移動標記
        self.is_duck_move = is_duck_move

        # 兵升變
        self.is_pawn_promotion = ((self.piece_moved == "wp" and self.end_row == 0) or
                                  (self.piece_moved == "bp" and self.end_row == 7))

        # 吃過路兵
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # 王車易位
        self.is_castle_move = is_castle_move

        # 是否是吃子 (不能吃鴨子)
        self.is_capture = self.piece_captured != "--" and not self.is_duck_move and self.piece_captured != "DD"

        # 移動ID (用於比較移動)
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """Overriding the equals method."""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        """獲取標準棋譜表示法，增加鴨子移動支持"""
        if self.is_duck_move:
            return "D" + self.getRankFile(self.end_row, self.end_col)

        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"

        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        if self.is_enpassant_move:
            return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                self.getRankFile(self.end_row, self.end_col) + " e.p."

        if self.is_capture:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                    self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.getRankFile(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.getRankFile(self.end_row, self.end_col)

    def getRankFile(self, row, col):
        """將行列轉換為棋盤坐標 (如 (0,0) -> 'a8')"""
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __str__(self):
        """字符串表示，用於打印移動"""
        if self.is_duck_move:
            return f"Duck to {self.getRankFile(self.end_row, self.end_col)}"

        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.getRankFile(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square