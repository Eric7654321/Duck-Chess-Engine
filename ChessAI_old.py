"""
Handling the AI moves for Duck Chess.
"""
import random
import math
import os

FAIRY_STOCKFISH_PATH = "fairy-stockfish.exe"
NNUE_MODEL_PATH = os.path.join("NNUE model", "duck-ba21f91f5d81.nnue")

# Piece values and position scores remain the same as before
piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1, "D": 0}  # Duck has 0 value

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}

# Add duck position scores (ducks are best in the center)
duck_scores = [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
               [0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1],
               [0.1, 0.2, 0.3, 0.3, 0.3, 0.3, 0.2, 0.1],
               [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
               [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
               [0.1, 0.2, 0.3, 0.3, 0.3, 0.3, 0.2, 0.1],
               [0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1],
               [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]

piece_position_scores["DD"] = duck_scores

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 15


def findBestMove(game_state, valid_moves, return_queue):
    """
    Find the best move using Duck NNUE evaluation on all valid moves.
    """
    global next_move
    next_move = None

    duck_moves = [move for move in valid_moves if move.is_duck_move]
    piece_moves = [move for move in valid_moves if not move.is_duck_move]

    if game_state.duck_move_phase:
        if duck_moves:
            findBestDuckMove(game_state, duck_moves)
    else:
        best_score = -math.inf
        best_move = None

        for move in piece_moves:
            game_state.makeMove(move)
            score = evaluate_position_with_fairy_stockfish(game_state)
            game_state.undoMove()

            if game_state.white_to_move and score > best_score:
                best_score = score
                best_move = move
            elif not game_state.white_to_move and score < best_score:
                best_score = score
                best_move = move

        next_move = best_move if best_move else random.choice(piece_moves)

    return_queue.put(next_move)


def findBestDuckMove(game_state, valid_duck_moves):
    """
    Find the best duck move based on strategic positioning.
    """
    global next_move
    best_score = -math.inf
    best_move = None

    for move in valid_duck_moves:
        # Score based on position (center is better)
        row, col = move.end_row, move.end_col
        position_score = duck_scores[row][col]

        # Additional strategic considerations:
        # 1. Block enemy pieces
        # 2. Don't block our own pieces
        # 3. Stay away from enemy king (to avoid blocking checks)

        # Calculate blocking score
        blocking_score = 0
        enemy_color = 'b' if game_state.white_to_move else 'w'

        # Check if duck is blocking enemy pieces
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = game_state.board[r][c]
                    if piece == "--":
                        continue
                    if piece[0] == enemy_color and piece[1] in ['Q', 'R', 'B']:
                        blocking_score += 1  # bonus for blocking enemy sliding pieces
                    break

        # Penalize if blocking our own pieces
        own_piece_penalty = 0
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = game_state.board[r][c]
                    if piece == "--":
                        continue
                    if piece[0] == ('w' if game_state.white_to_move else 'b'):
                        own_piece_penalty += 1  # penalty for blocking our own pieces
                    break

        total_score = position_score * 10 + blocking_score - own_piece_penalty

        if total_score > best_score:
            best_score = total_score
            best_move = move

    next_move = best_move if best_move else random.choice(valid_duck_moves)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    NegaMax algorithm with alpha-beta pruning for piece moves.
    """
    global next_move
    if depth == 0:
        return turn_multiplier * evaluate_position_with_fairy_stockfish(game_state)

    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()

        # Skip duck moves when evaluating board state
        piece_moves = [m for m in next_moves if not m.is_duck_move]

        score = -findMoveNegaMaxAlphaBeta(game_state, piece_moves, depth - 1, -beta, -alpha, -turn_multiplier)

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undoMove()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    Now considers duck position in evaluation.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif game_state.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] == "D":  # Duck
                    piece_position_score = duck_scores[row][col] * 0.5  # Duck position is less important
                elif piece[1] != "K":  # Other pieces (except king)
                    piece_position_score = piece_position_scores[piece][row][col]

                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                elif piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    # Add bonus for controlling center with duck
    duck_row, duck_col = game_state.duck_location
    center_control = duck_scores[duck_row][duck_col]
    score += center_control * 0.3  # Small bonus for good duck position

    return score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)


import chess
import chess.engine
import os

FAIRY_STOCKFISH_PATH = "fairy-stockfish.exe"


def evaluate_position_with_fairy_stockfish(game_state):
    """
    使用 Fairy-Stockfish 評估目前局面。
    """
    fen = game_state.get_fen()
    try:
        board = chess.variant.DuckChessBoard()
        board.set_fen(fen)

        with chess.engine.SimpleEngine.popen_uci(FAIRY_STOCKFISH_PATH) as engine:
            # 如果有 NNUE 模型就加載，沒有可以略過
            if os.path.exists(NNUE_MODEL_PATH):
                engine.configure({"EvalFile": NNUE_MODEL_PATH})

            result = engine.analyse(board, chess.engine.Limit(time=100.0))
            score = result["score"].white().score(mate_score=10000)

            return score if game_state.white_to_move else -score

    except Exception as e:
        with open("stockfish_debug.log", "a") as f:
            f.write(f"[ERROR] Failed to evaluate with Stockfish: {e}\n")
        return 0

def convert_to_fen(game_state):
    rows = []
    for r in range(8):
        empty = 0
        row_str = ""
        for c in range(8):
            piece = game_state.board[r][c]
            if piece == "DD":
                if empty:
                    row_str += str(empty)
                    empty = 0
                row_str += 'D'  # Duck
            elif piece == "--":
                empty += 1
            else:
                if empty:
                    row_str += str(empty)
                    empty = 0
                p = piece[1]
                row_str += p.upper() if piece[0] == "w" else p.lower()
        if empty:
            row_str += str(empty)
        rows.append(row_str)
    board_fen = "/".join(rows)
    turn = "w" if game_state.white_to_move else "b"
    # Castling and en passant: - -
    return f"{board_fen} {turn} - - 0 1"

