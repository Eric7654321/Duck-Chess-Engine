"""
Storing all the information about the current state of duck chess game.
Determining valid moves at current state.
It will keep move log.
Special rules:
1. No check/checkmate - capturing the opponent's king wins immediately
2. Duck blocks all pieces (except knights) and must be moved after each piece move
3. Two-phase turns: piece move -> duck move
"""


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        # Initialize king locations
        self.white_king_location = (7, 4)  # e1
        self.black_king_location = (0, 4)  # e8

        # 鴨子初始化
        self.duck_location = (2, 7)  # 中心位置
        assert (
                self.board[self.duck_location[0]][self.duck_location[1]] == "--"
        ), "鴨子初始位置已被佔用！"
        self.board[self.duck_location[0]][self.duck_location[1]] = "DD"
        self.duck_location_log = [self.duck_location]

        self.moveFunctions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
            "D": self.getDuckMoves,
        }

        self.white_to_move = True
        self.move_log = []
        self.game_over = False  # True when king is captured
        self.winner = None  # "w" or "b" when game ends

        # Duck movement phase flags
        self.duck_move_phase = False  # False=piece move, True=duck move
        self.duck_move_made = False

        # En passant tracking
        self.enpassant_possible = ()  # coordinates for en passant capture
        self.enpassant_possible_log = [self.enpassant_possible]

        # Castling rights
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs,
            )
        ]

        # Half-move counter for 50-move rule
        self.no_progress_count = 0

    def makeMove(self, move):
        """Execute a move (piece or duck) and check for king capture"""
        if self.game_over:
            return

        move.prev_no_progress_count = self.no_progress_count

        if not move.is_duck_move:  # Piece movement
            captured_piece = self.board[move.end_row][move.end_col]
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.move_log.append(move)

            # Update king location if moved
            if move.piece_moved == "wK":
                self.white_king_location = (move.end_row, move.end_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.end_row, move.end_col)

            # Check if king was captured
            if captured_piece in ["wK", "bK"]:
                self.game_over = True
                self.winner = "w" if captured_piece == "bK" else "b"
                return

            # Handle pawn-specific rules
            if move.piece_moved[1] == "p":
                # Pawn promotion
                if move.is_pawn_promotion:
                    self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

                # En passant capture
                if move.is_enpassant_move:
                    captured_pawn_row = move.start_row
                    captured_pawn_col = move.end_col
                    self.board[captured_pawn_row][captured_pawn_col] = "--"

                # Set en passant opportunity
                if abs(move.start_row - move.end_row) == 2:
                    self.enpassant_possible = (
                        (move.start_row + move.end_row) // 2,
                        move.start_col,
                    )
                else:
                    self.enpassant_possible = ()
            else:
                self.enpassant_possible = ()

            # Handle castling
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # Kingside
                    rook_start_col = move.end_col + 1
                    rook_end_col = move.end_col - 1
                    rook = self.board[move.end_row][rook_start_col]
                    self.board[move.end_row][rook_end_col] = rook
                    self.board[move.end_row][rook_start_col] = "--"
                else:  # Queenside
                    rook_start_col = move.end_col - 2
                    rook_end_col = move.end_col + 1
                    rook = self.board[move.end_row][rook_start_col]
                    self.board[move.end_row][rook_end_col] = rook
                    self.board[move.end_row][rook_start_col] = "--"

            # Update turn phase
            if not self.duck_move_phase:
                self.duck_move_phase = True
            else:
                self.white_to_move = not self.white_to_move
                self.duck_move_phase = False

            # 50 steps
            if move.is_capture or move.piece_moved[1] == 'p':
                self.no_progress_count = 0
            else:
                self.no_progress_count += 1

            if self.no_progress_count >= 50:
                self.game_over = True

        else:  # Duck movement
            # Move duck to new position
            self.board[self.duck_location[0]][self.duck_location[1]] = "--"
            self.board[move.end_row][move.end_col] = "DD"
            self.duck_location = (move.end_row, move.end_col)
            self.duck_location_log.append(self.duck_location)
            self.move_log.append(move)

            # After duck move, change player and reset phase
            self.white_to_move = not self.white_to_move
            self.duck_move_phase = False

        # Update move counters and logs
        self.enpassant_possible_log.append(self.enpassant_possible)

        # Update castling rights if needed
        if not move.is_duck_move:
            self.updateCastleRights(move)
            self.castle_rights_log.append(
                CastleRights(
                    self.current_castling_rights.wks,
                    self.current_castling_rights.bks,
                    self.current_castling_rights.wqs,
                    self.current_castling_rights.bqs,
                )
            )

    def undoMove(self):
        """Undo the last move"""
        if len(self.move_log) == 0:
            return

        move = self.move_log.pop()

        self.no_progress_count = move.prev_no_progress_count

        if not move.is_duck_move:  # Undo piece move
            # Restore board state
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured

            # Restore king position if moved
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

            # Restore en passant state
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured

            # Restore castling rights
            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]

            # Restore castle state
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # Kingside
                    rook_current_col = move.end_col - 1
                    rook_original_col = move.end_col + 1
                    rook = self.board[move.end_row][rook_current_col]
                    self.board[move.end_row][rook_original_col] = rook
                    self.board[move.end_row][rook_current_col] = "--"
                else:  # Queenside
                    rook_current_col = move.end_col + 1
                    rook_original_col = move.end_col - 2
                    rook = self.board[move.end_row][rook_current_col]
                    self.board[move.end_row][rook_original_col] = rook
                    self.board[move.end_row][rook_current_col] = "--"

            # Restore turn state
            if self.duck_move_phase:
                self.duck_move_phase = False
            else:
                self.white_to_move = not self.white_to_move
                self.duck_move_phase = True

            # Clear game over state
            self.game_over = False
            self.winner = None

        else:  # Undo duck move
            # Restore duck position
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.start_row][move.start_col] = "DD"
            self.duck_location = (move.start_row, move.start_col)
            self.duck_location_log.pop()

            # Restore turn state
            self.duck_move_phase = True
            # Player doesn't change because duck move is part of the same turn

            # Clear game over state
            self.game_over = False
            self.winner = None

        # Restore en passant state
        self.enpassant_possible_log.pop()
        self.enpassant_possible = self.enpassant_possible_log[-1]

        # Restore 50-move counter
        self.prev_no_progress_count = 0

    def updateCastleRights(self, move):
        """Update castling rights based on move"""
        if move.is_duck_move:
            return

        # King moved
        if move.piece_moved == "wK":
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False

        # Rook captured
        if move.piece_captured == "wR":
            if move.end_col == 0:  # Queenside rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # Kingside rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # Queenside rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # Kingside rook
                self.current_castling_rights.bks = False

        # Rook moved from starting position
        if move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:  # Queenside rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # Kingside rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:  # Queenside rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # Kingside rook
                    self.current_castling_rights.bks = False

    def getValidMoves(self):
        """Get all valid moves for current game state"""
        if self.game_over:
            return []

        # Piece movement phase
        if not self.duck_move_phase:
            moves = self.getAllPossibleMoves()

            # 添加城堡移动 - 修复入堡功能
            if self.white_to_move:
                self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

            return moves

        # Duck movement phase
        else:
            return self.getDuckMoves()

    def getAllPossibleMoves(self):
        """Get all possible moves without considering check (since no check in duck chess)"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece_color = self.board[row][col][0]
                piece_type = self.board[row][col][1]

                # Skip empty squares, duck, and opponent pieces
                if piece_color == "-" or piece_type == "D" or \
                        (piece_color == "w" and not self.white_to_move) or \
                        (piece_color == "b" and self.white_to_move):
                    continue

                # Generate moves for this piece (skip duck)
                if piece_type in self.moveFunctions and piece_type != "D":
                    self.moveFunctions[piece_type](row, col, moves)

        return moves

    def getPawnMoves(self, row, col, moves):
        """Get all pawn moves considering duck blocking and en passant"""
        if self.white_to_move:  # White pawn moves
            direction = -1
            start_row = 6
            enemy_color = "b"
        else:  # Black pawn moves
            direction = 1
            start_row = 1
            enemy_color = "w"

        # Move forward one square
        if self.board[row + direction][col] == "--":
            if (row + direction, col) != self.duck_location:
                # Check promotion
                if (row + direction == 0 and self.white_to_move) or (row + direction == 7 and not self.white_to_move):
                    moves.append(Move((row, col), (row + direction, col), self.board, is_pawn_promotion=True))
                else:
                    moves.append(Move((row, col), (row + direction, col), self.board))

                # Move forward two squares
                if row == start_row and self.board[row + 2*direction][col] == "--":
                    if (row + 2*direction, col) != self.duck_location and (row + direction, col) != self.duck_location:
                        moves.append(Move((row, col), (row + 2*direction, col), self.board))

        # Capture diagonally
        for d_col in [-1, 1]:
            if 0 <= col + d_col < 8:
                end_row = row + direction
                end_col = col + d_col

                # Can't capture duck
                if (end_row, end_col) == self.duck_location:
                    continue

                # Normal capture
                if self.board[end_row][end_col][0] == enemy_color:
                    # Check promotion
                    if (end_row == 0 and self.white_to_move) or (end_row == 7 and not self.white_to_move):
                        moves.append(Move((row, col), (end_row, end_col), self.board, is_pawn_promotion=True))
                    else:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

                # En passant capture
                if (end_row, end_col) == self.enpassant_possible:
                    # Make sure path isn't blocked by duck
                    if (row, end_col) != self.duck_location and (end_row, end_col) != self.duck_location:
                        moves.append(Move((row, col), (end_row, end_col), self.board, is_enpassant_move=True))

    def getRookMoves(self, row, col, moves):
        """Get all rook moves considering duck blocking"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
        ally_color = "w" if self.white_to_move else "b"

        for dr, dc in directions:
            for step in range(1, 8):
                end_row = row + dr * step
                end_col = col + dc * step

                # Stop at board edge
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break

                # Stop if duck is blocking
                if (end_row, end_col) == self.duck_location:
                    break

                end_piece = self.board[end_row][end_col]

                # Empty square is valid
                if end_piece == "--":
                    moves.append(Move((row, col), (end_row, end_col), self.board))
                # Capture enemy piece
                elif end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))
                    break  # Can't jump over enemy pieces
                # Ally piece blocks
                else:
                    break

    def getKnightMoves(self, row, col, moves):
        """Get all knight moves (can jump over duck)"""
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        ally_color = "w" if self.white_to_move else "b"

        for dr, dc in knight_moves:
            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                # Can't land on duck
                if (end_row, end_col) == self.duck_location:
                    continue

                end_piece = self.board[end_row][end_col]
                # Valid if empty or enemy piece
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def getBishopMoves(self, row, col, moves):
        """Get all bishop moves considering duck blocking"""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals
        ally_color = "w" if self.white_to_move else "b"

        for dr, dc in directions:
            for step in range(1, 8):
                end_row = row + dr * step
                end_col = col + dc * step

                # Stop at board edge
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break

                # Stop if duck is blocking
                if (end_row, end_col) == self.duck_location:
                    break

                end_piece = self.board[end_row][end_col]

                # Empty square is valid
                if end_piece == "--":
                    moves.append(Move((row, col), (end_row, end_col), self.board))
                # Capture enemy piece
                elif end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))
                    break  # Can't jump over enemy pieces
                # Ally piece blocks
                else:
                    break

    def getQueenMoves(self, row, col, moves):
        """Get all queen moves (combines rook and bishop)"""
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """Get all king moves (can't move to duck position)"""
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        ally_color = "w" if self.white_to_move else "b"

        for dr, dc in king_moves:
            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                # Can't move to duck position
                if (end_row, end_col) == self.duck_location:
                    continue

                end_piece = self.board[end_row][end_col]
                # Valid if empty or enemy piece
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def getCastleMoves(self, row, col, moves):
        """Generate valid castle moves considering duck blocking"""
        # Kingside castle
        if (self.white_to_move and self.current_castling_rights.wks) or \
                (not self.white_to_move and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)

        # Queenside castle
        if (self.white_to_move and self.current_castling_rights.wqs) or \
                (not self.white_to_move and self.current_castling_rights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        """Kingside castle - duck aware"""
        # Check if path is clear and not blocked by duck
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            # Check duck isn't blocking
            if (row, col+1) != self.duck_location and (row, col+2) != self.duck_location:
                # Check rook is in place
                if self.board[row][col+3][1] == "R":
                    moves.append(Move((row, col), (row, col+2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, row, col, moves):
        """Queenside castle - duck aware"""
        # Check if path is clear and not blocked by duck
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            # Check duck isn't blocking
            if (row, col-1) != self.duck_location and (row, col-2) != self.duck_location:
                # Check rook is in place
                if self.board[row][col-4][1] == "R":
                    moves.append(Move((row, col), (row, col-2), self.board, is_castle_move=True))

    def getDuckMoves(self):
        """Duck can teleport to any empty square"""
        moves = []
        current_row, current_col = self.duck_location

        for row in range(8):
            for col in range(8):
                # Can move to any empty square except current position
                if self.board[row][col] == "--" and (row, col) != (current_row, current_col):
                    moves.append(Move(
                        (current_row, current_col),
                        (row, col),
                        self.board,
                        is_duck_move=True
                    ))

        return moves

    def squareHasPiece(self, row, col):
        """Check if square has a piece (not duck or empty)"""
        return self.board[row][col] != "--" and self.board[row][col] != "DD"


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White kingside
        self.bks = bks  # Black kingside
        self.wqs = wqs  # White queenside
        self.bqs = bqs  # Black queenside


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False,
                 is_castle_move=False, is_duck_move=False, is_pawn_promotion=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.prev_no_progress_count = 0

        # Special move flags
        self.is_duck_move = is_duck_move
        self.is_pawn_promotion = is_pawn_promotion
        self.is_enpassant_move = is_enpassant_move
        self.is_castle_move = is_castle_move

        # Capture logic (can't capture duck)
        self.is_capture = (
            self.piece_captured != "--"
            and not self.is_duck_move
            and self.piece_captured != "DD"
        )

        # Move ID for comparison
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """Override equals method"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        """Get standard chess notation with duck move support"""
        if self.is_duck_move:
            return "D" + self.getRankFile(self.end_row, self.end_col)

        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"

        if self.is_castle_move:
            return "0-0" if self.end_col > self.start_col else "0-0-0"

        if self.is_enpassant_move:
            return (self.getRankFile(self.start_row, self.start_col)[0] + "x" +
                    self.getRankFile(self.end_row, self.end_col) + " e.p.")

        if self.is_capture:
            if self.piece_moved[1] == "p":
                return (self.cols_to_files[self.start_col] + "x" +
                        self.getRankFile(self.end_row, self.end_col))
            else:
                return (self.piece_moved[1] + "x" +
                        self.getRankFile(self.end_row, self.end_col))
        else:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.end_row, self.end_col)
            else:
                return (self.piece_moved[1] +
                        self.getRankFile(self.end_row, self.end_col))

    def getRankFile(self, row, col):
        """Convert row/col to chess notation (e.g., (0,0) -> 'a8')"""
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __str__(self):
        """String representation for printing moves"""
        if self.is_duck_move:
            return f"Duck to {self.getRankFile(self.end_row, self.end_col)}"

        if self.is_castle_move:
            return "0-0" if self.end_col > self.start_col else "0-0-0"

        end_square = self.getRankFile(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + ("Q" if self.is_pawn_promotion else "")

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square