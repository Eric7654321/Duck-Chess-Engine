"""
Handling the AI moves for Duck Chess.
"""

import math
import os
import random

import chess
import chess.engine
from ChessEngine import \
    Move  # Added: import Move class to attach get_uci method


# Added: Support Move.get_uci() for matching UCI strings
def get_uci(self):
    # Convert move to UCI format (e.g., e2e4)
    return (
        self.cols_to_files[self.start_col]
        + self.rows_to_ranks[self.start_row]
        + self.cols_to_files[self.end_col]
        + self.rows_to_ranks[self.end_row]
    )


Move.get_uci = get_uci

# Piece values and position scores remain the same as before
piece_score = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1,
    "D": 0,
}  # Duck has 0 value

FAIRY_STOCKFISH_PATH = (
    os.path.join('.', 'fairy-stockfish.exe') if sys.platform == 'win32' else
    os.path.join('.', 'fairy-stockfish_x86-64') if sys.platform.startswith('linux') else
    None
)

knight_scores = [
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
    [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
    [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
    [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
    [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
    [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
    [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
]

bishop_scores = [
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
    [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
    [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
    [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
    [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
]

rook_scores = [
    [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25],
]

queen_scores = [
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
]

pawn_scores = [
    [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
    [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
    [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
    [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
    [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
    [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
]

piece_position_scores = {
    "wN": knight_scores,
    "bN": knight_scores[::-1],
    "wB": bishop_scores,
    "bB": bishop_scores[::-1],
    "wQ": queen_scores,
    "bQ": queen_scores[::-1],
    "wR": rook_scores,
    "bR": rook_scores[::-1],
    "wp": pawn_scores,
    "bp": pawn_scores[::-1],
}

# Add duck position scores (ducks are best in the center)
duck_scores = [
    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    [0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1],
    [0.1, 0.2, 0.3, 0.3, 0.3, 0.3, 0.2, 0.1],
    [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
    [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
    [0.1, 0.2, 0.3, 0.3, 0.3, 0.3, 0.2, 0.1],
    [0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1],
    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
]

piece_position_scores["DD"] = duck_scores

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def findBestMove(game_state, valid_moves, return_queue):
    """
    Find the best move considering duck chess rules.
    Handles both piece movement phase and duck movement phase.
    """
    global next_move
    next_move = None

    # Separate duck moves from piece moves
    duck_moves = [move for move in valid_moves if move.is_duck_move]
    piece_moves = [move for move in valid_moves if not move.is_duck_move]

    if game_state.duck_move_phase:
        # Duck movement phase - find best duck move
        if duck_moves:
            findBestDuckMove(game_state, duck_moves)
    else:
        # Piece movement phase - find best piece move
        if piece_moves:
            random.shuffle(piece_moves)
            findMoveNegaMaxAlphaBeta(
                game_state,
                piece_moves,
                DEPTH,
                -CHECKMATE,
                CHECKMATE,
                1 if game_state.white_to_move else -1,
            )

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
        enemy_color = "b" if game_state.white_to_move else "w"

        # Check if duck is blocking enemy pieces
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = game_state.board[r][c]
                    if piece == "--":
                        continue
                    if piece[0] == enemy_color:
                        # Modified: weight blocking queen/rook higher
                        if piece[1] == "Q":
                            blocking_score += 3  # high bonus for blocking enemy queen
                        elif piece[1] == "R":
                            blocking_score += 2  # bonus for blocking enemy rook
                        elif piece[1] == "B":
                            blocking_score += 1  # bonus for blocking enemy bishop
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
                    if piece[0] == ("w" if game_state.white_to_move else "b"):
                        own_piece_penalty += 1  # penalty for blocking our own pieces
                    break

        total_score = position_score * 10 + blocking_score - own_piece_penalty

        if total_score > best_score:
            best_score = total_score
            best_move = move

    next_move = best_move if best_move else random.choice(valid_duck_moves)


def findMoveNegaMaxAlphaBeta(
    game_state, valid_moves, depth, alpha, beta, turn_multiplier
):
    # Modified: integrate Stockfish move at root and ensure full move search
    """
    NegaMax algorithm with alpha-beta pruning for piece moves.
    """
    global next_move
    top_level = depth == DEPTH
    # If at root depth, get Stockfish's recommended move first
    if top_level:
        try:
            # Use Fairy-Stockfish to get best move in UCI
            fen = convert_to_fen(game_state)
            with chess.engine.SimpleEngine.popen_uci(FAIRY_STOCKFISH_PATH) as engine:
                engine.configure(
                    {
                        "EvalFile": os.path.join(
                            "NNUE model", "NNUE model/duck-ba21f91f5d81.nnue"
                        )
                    }
                )
                board = chess.Board(fen)
                result = engine.play(board, chess.engine.Limit(time=0.5))
                best_uci = result.move.uci()
            # Find corresponding Move object in valid_moves
            for move in valid_moves:
                if move.get_uci() == best_uci:
                    # Use this as next_move and evaluate one-ply deeper
                    next_move = move  # prioritize Stockfish move
                    game_state.makeMove(move)
                    next_moves = game_state.getValidMoves()
                    piece_moves = [m for m in next_moves if not m.is_duck_move]
                    score = -findMoveNegaMaxAlphaBeta(
                        game_state,
                        piece_moves,
                        depth - 1,
                        -beta,
                        -alpha,
                        -turn_multiplier,
                    )
                    game_state.undoMove()
                    return score
        except Exception as e:
            # If engine fails, proceed with regular search
            print(f"[DEBUG] Stockfish move not used due to error: {e}")
            pass

    if depth == 0:
        # Optionally combine Stockfish eval with positional eval
        fs_score = evaluate_position_with_fairy_stockfish(game_state)
        pos_score = scoreBoard(game_state)
        # Weighted combination (80% Stockfish, 20% positional)
        combined_score = fs_score * 0.8 + pos_score * 0.2
        return turn_multiplier * combined_score

    best_score = -CHECKMATE
    best_move_local = None
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        # Skip duck moves when evaluating board state
        piece_moves = [m for m in next_moves if not m.is_duck_move]
        score = -findMoveNegaMaxAlphaBeta(
            game_state, piece_moves, depth - 1, -beta, -alpha, -turn_multiplier
        )
        game_state.undoMove()

        if score > best_score:
            best_score = score
            best_move_local = move
        if best_score > alpha:
            alpha = best_score
        if alpha >= beta:
            break

    if top_level and best_move_local is not None:
        next_move = best_move_local
    return best_score


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
                    piece_position_score = (
                        duck_scores[row][col] * 0.5
                    )  # Duck position is less important
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


def evaluate_position_with_fairy_stockfish(game_state):
    # 轉換成 FEN 字串
    fen = convert_to_fen(game_state)

    # 初始化 fairy-stockfish 引擎
    try:
        with chess.engine.SimpleEngine.popen_uci(FAIRY_STOCKFISH_PATH) as engine:
            print("[DEBUG] FEN passed to Stockfish:", fen)
            # 設定 NNUE 模型路徑（若有需要）
            engine.configure(
                {
                    "UCI_EvalFile": os.path.join(
                        "NNUE model", "NNUE model/duck-ba21f91f5d81.nnue"
                    )
                }
            )

            # 計算 position 評分
            board = chess.Board(fen)
            result = engine.analyse(board, chess.engine.Limit(time=0.5))
            score = result["score"].white().score(mate_score=10000)
            if score is None:
                score = 0
            score = int(score)
            return score if game_state.white_to_move else -score
    except Exception as e:
        print(f"[Error] 評估失敗：{e}")
        return 0


def convert_to_fen(game_state):
    rows = []
    for r in range(8):
        empty = 0
        row_str = ""
        for c in range(8):
            piece = game_state.board[r][c]
            if piece == "--" or piece == "DD":
                empty += 1
            else:
                if empty != 0:
                    row_str += str(empty)
                    empty = 0
                piece_char = piece[1]
                if piece[0] == "w":
                    row_str += piece_char.upper()
                else:
                    row_str += piece_char.lower()
        if empty != 0:
            row_str += str(empty)
        rows.append(row_str)
    board_fen = "/".join(rows)

    turn = "w" if game_state.white_to_move else "b"

    # castling/en passant 先忽略或改進
    fen = f"{board_fen} {turn} - - 0 1"
    return fen
