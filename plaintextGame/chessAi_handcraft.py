"""
Handling the AI moves for Duck Chess.
"""

import math
import random

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
DEPTH = 1  # reduce for testing; bump back up as needed

# Global to hold the chosen move at the root
next_move = None


def findBestMove(game_state, valid_moves, return_queue):
    global next_move
    next_move = None

    enemy_king = "bK" if game_state.white_to_move else "wK"
    for move in valid_moves:
        if not move.is_duck_move and move.piece_captured == enemy_king:
            return_queue.put(move)
            return

    # Only consider piece moves at the root
    piece_moves = [m for m in valid_moves if not m.is_duck_move]
    _ = negamax_full(game_state, piece_moves, DEPTH, -CHECKMATE, CHECKMATE, 1)
    return_queue.put(next_move)


def negamax_full(game_state, moves, depth, alpha, beta, color):
    global next_move

    enemy_king = "bK" if game_state.white_to_move else "wK"
    for move in moves:
        if move.piece_captured == enemy_king:
            if depth == DEPTH:
                next_move = move
            return color * CHECKMATE

    # Base case
    if depth == 0 or not moves:
        return color * scoreBoard(game_state)

    max_score = -math.inf
    for move in moves:
        # ─────────── SNAPSHOT ───────────
        orig_white = game_state.white_to_move
        orig_duck = game_state.duck_move_phase

        # 1) Piece move
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()

        # 2) Duck phase (must be True here)
        #    pick the best immediate duck move
        duck_moves = [m for m in next_moves if m.is_duck_move]
        best_duck = None
        best_duck_score = -math.inf
        for dm in duck_moves:
            game_state.makeMove(dm)
            sc = -negamax_full(
                game_state,
                [m for m in game_state.getValidMoves() if not m.is_duck_move],
                depth - 1,
                -beta,
                -alpha,
                -color,
            )
            game_state.undoMove()
            if sc > best_duck_score:
                best_duck_score, best_duck = sc, dm

        # 3) Apply & evaluate the best duck
        if best_duck:
            game_state.makeMove(best_duck)
            score = -negamax_full(
                game_state,
                [m for m in game_state.getValidMoves() if not m.is_duck_move],
                depth - 1,
                -beta,
                -alpha,
                -color,
            )
            game_state.undoMove()
        else:
            # (should never happen: there’s always at least one duck move)
            score = best_duck_score

        # ─────── UNDO BOTH MOVES ───────
        game_state.undoMove()  # undo the piece move

        # ────────── RESTORE STATE ─────────
        game_state.white_to_move = orig_white
        game_state.duck_move_phase = orig_duck

        # ─── record move at root ───
        if depth == DEPTH and score > max_score:
            next_move = move

        max_score = max(max_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    return max_score


def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    Now considers duck position in evaluation.
    """
    if game_state.game_over:
        if game_state.winner == 'w':
            return CHECKMATE
        elif game_state.winner == 'b':
            return -CHECKMATE
        else:
            return STALEMATE  # 平局

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
