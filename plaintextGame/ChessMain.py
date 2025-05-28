"""
Main driver file.
Handling user input.
Displaying current GameStatus object.
"""

import functools
import os
import queue
import sys
from multiprocessing import Pool, Process, Queue, cpu_count

import chess.engine
import ChessAI
import ChessEngine
import pygame as p
from tqdm import tqdm

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    """
    Initialize a global directory of images.
    This will be called exactly once in the main.
    """
    pieces = [
        "wp",
        "wR",
        "wN",
        "wB",
        "wK",
        "wQ",
        "bp",
        "bR",
        "bN",
        "bB",
        "bK",
        "bQ",
        "DD",
    ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(os.path.join("images/", "" + piece + ".png")),
            (SQUARE_SIZE, SQUARE_SIZE),
        )


def is_ai_player(player_type):
    return player_type in ("ai_random", "ai_handcraft", "ai_nnue")


def run_ai_vs_ai(game_state, player_one, player_two):
    import queue

    while not game_state.checkmate and not game_state.stalemate:
        white_to_move = game_state.white_to_move
        player_type = player_one if white_to_move else player_two
        valid_moves = game_state.getValidMoves()

        if not valid_moves:
            break

        if player_type == "ai_random":
            q = queue.Queue()
            ChessAI.findRandomMove(valid_moves, q)
            move = q.get()
        else:
            mode = player_type.split("_")[1]  # 'handcraft' or 'nnue'
            q = queue.Queue()
            ChessAI.findBestMove(game_state, valid_moves, q, mode=mode)
            move = q.get()

        game_state.makeMove(move)

    if game_state.checkmate:
        # The side to move is checkmated, so the other side won
        winner_color = "White" if not game_state.white_to_move else "Black"
        loser_color = "Black" if winner_color == "White" else "White"
        winner_type = player_one if winner_color == "White" else player_two
        loser_type = player_two if loser_color == "Black" else player_one
        print(
            f"Checkmate! {winner_color} ({winner_type}) beats over "
            f"{loser_color} ({loser_type}) the game!"
        )
    elif game_state.stalemate:
        print("Game ended in a stalemate (draw).")
    else:
        print("Game ended without checkmate or stalemate.")


def main(player_one, player_two,visualize_game=True):
    # 'human', 'ai_random', 'ai_handcraft', 'ai_nnue'
    #player_one = "ai_handcraft"  # white
    #player_two = "ai_random"  # black
    #visualize_game = True  # True to show pygame UI, False to run silently if AI vs AI

    if visualize_game is False:
        # If any player is human, can't run non-visual mode
        if not (is_ai_player(player_one) and is_ai_player(player_two)):
            raise ValueError(
                "Non-visual mode only supports AI vs AI (no human players)."
            )
        # Run silent AI vs AI mode
        game_state = ChessEngine.GameState()
        run_ai_vs_ai(game_state, player_one, player_two)
        return

    # If visualize_game is True, run pygame UI mode (human or AI players)
    p.init()

    screen = p.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    title = f"Black: {player_two}   White: {player_one}"
    p.display.set_caption(title)

    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    loadImages()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)

    while running:
        human_turn = (game_state.white_to_move and player_one == "human") or (
            not game_state.white_to_move and player_two == "human"
        )

        # Duck move phase handling
        if game_state.duck_move_phase:
            duck_move_possible = any(move.is_duck_move for move in valid_moves)
            if not duck_move_possible:
                # Skip duck move phase if no valid duck moves
                game_state.white_to_move = not game_state.white_to_move
                game_state.duck_move_phase = False
                valid_moves = game_state.getValidMoves()
                move_made = True

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    # Duck move selection
                    if game_state.duck_move_phase:
                        if col < 8:  # Make sure click is on board
                            duck_move = ChessEngine.Move(
                                game_state.duck_location,
                                (row, col),
                                game_state.board,
                                is_duck_move=True,
                            )
                            if duck_move in valid_moves:
                                game_state.makeMove(duck_move)
                                move_made = True
                                animate = True
                                square_selected = ()
                                player_clicks = []

                    # Piece move selection
                    else:
                        if (
                            square_selected == (row, col) or col >= 8
                        ):  # user clicked the same square twice
                            square_selected = ()  # deselect
                            player_clicks = []  # clear clicks
                        else:
                            square_selected = (row, col)
                            player_clicks.append(square_selected)

                        if len(player_clicks) == 2:  # after 2nd click
                            move = ChessEngine.Move(
                                player_clicks[0], player_clicks[1], game_state.board)
                            for valid_move in valid_moves:
                                if move == valid_move and not valid_move.is_duck_move:
                                    game_state.makeMove(valid_move)
                                    move_made = True
                                    animate = True
                                    square_selected = ()
                                    player_clicks = []
                                    break
                            if not move_made:
                                player_clicks = [square_selected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # reset the game when 'r' is pressed
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                current_player = player_one if game_state.white_to_move else player_two

                if current_player == "ai_random":
                    move_finder_process = Process(
                        target=ChessAI.findRandomMove, args=(
                            valid_moves, return_queue))
                elif current_player == "ai_handcraft":
                    move_finder_process = Process(
                        target=ChessAI.findBestMove, args=(
                            game_state, valid_moves, return_queue, "handcraft"), )
                elif current_player == "ai_nnue":
                    move_finder_process = Process(
                        target=ChessAI.findBestMove,
                        args=(game_state, valid_moves, return_queue, "nnue"),
                    )
                else:
                    # fallback random AI
                    move_finder_process = Process(
                        target=ChessAI.findRandomMove, args=(
                            valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1],
                            screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        # Highlight duck location during duck move phase
        if game_state.duck_move_phase and human_turn:
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(150)
            s.fill(p.Color("orange"))
            screen.blit(
                s,
                (
                    game_state.duck_location[1] * SQUARE_SIZE,
                    game_state.duck_location[0] * SQUARE_SIZE,
                ),
            )
            # Draw "DUCK MOVE" text
            font = p.font.SysFont("Arial", 24, True)
            text = font.render("DUCK MOVE", True, p.Color("red"))
            screen.blit(text, (BOARD_WIDTH // 2 - text.get_width() // 2, 10))

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected):
    """
    Responsible for all the graphics within current game state.
    """
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # draw pieces on top of those squares


def drawBoard(screen):
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(
                screen,
                color,
                p.Rect(
                    column *
                    SQUARE_SIZE,
                    row *
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE),
            )


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight square selected and moves for piece selected.
    """
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("green"))
        screen.blit(
            s,
            (last_move.end_col *
             SQUARE_SIZE,
             last_move.end_row *
             SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
            "w" if game_state.white_to_move else "b"
        ):  # square_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            # transparency value 0 -> transparent, 255 -> opaque
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(
                        s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(
                    IMAGES[piece],
                    p.Rect(
                        column * SQUARE_SIZE,
                        row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    ),
                )


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log.

    """
    move_log_rect = p.Rect(
        BOARD_WIDTH,
        0,
        MOVE_LOG_PANEL_WIDTH,
        MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color("white"))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - text_object.get_width() / 2,
        BOARD_HEIGHT / 2 - text_object.get_height() / 2,
    )
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color("black"))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 1  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (
            move.start_row + d_row * frame / frame_count,
            move.start_col + d_col * frame / frame_count,
        )
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(
            move.end_col * SQUARE_SIZE,
            move.end_row * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != "--":
            if move.is_enpassant_move:
                enpassant_row = (
                    move.end_row + 1
                    if move.piece_captured[0] == "b"
                    else move.end_row - 1
                )
                end_square = p.Rect(
                    move.end_col * SQUARE_SIZE,
                    enpassant_row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                )
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(
            col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), )
        p.display.flip()
        clock.tick(60)


def run_single_game(dummy_arg, player_one, player_two):
    game_state = ChessEngine.GameState()
    try:
        while not game_state.checkmate and not game_state.stalemate:
            white_to_move = game_state.white_to_move
            player_type = player_one if white_to_move else player_two
            valid_moves = game_state.getValidMoves()
            if not valid_moves:
                break

            q = queue.Queue()
            if player_type == "ai_random":
                ChessAI.findRandomMove(valid_moves, q)
            else:
                mode = player_type.split("_")[1]  # e.g. 'handcraft', 'nnue'
                ChessAI.findBestMove(game_state, valid_moves, q, mode=mode)
            move = q.get()
            if move is None:
                move = valid_moves[0]
            game_state.makeMove(move)
    except Exception as e:
        if "Maximum number of moves" in str(e):
            return "over200"  # "Maximum number of moves (200) exceeded."
        else:
            raise  # re-raise any other exceptions

    if game_state.checkmate:
        winner_color = "White" if not game_state.white_to_move else "Black"
        return winner_color
    elif game_state.stalemate:
        return "Draw"
    else:
        return "Unknown"


def run_parallel_games(player_one, player_two, num_games=100, num_workers=4):
    func = functools.partial(
        run_single_game, player_one=player_one, player_two=player_two
    )
    with Pool(processes=num_workers) as pool:
        results = []
        for result in tqdm(
            pool.imap_unordered(func, range(num_games)), total=num_games
        ):
            results.append(result)

    white_wins = results.count("White")
    black_wins = results.count("Black")
    #over200 = results.count("over200")
    draws = results.count("Draw")

    print(f"Out of {num_games} games:")
    print(
        f"White ({player_one}) wins: {white_wins} ({
            white_wins /
            num_games:.2%})"
    )
    print(
        f"Black ({player_two}) wins: {black_wins} ({
            black_wins /
            num_games:.2%})"
    )
    print(f"Draws: {draws} ({draws / num_games:.2%})")
    #print(f"over200: {over200} ({over200 / num_games:.2%})")


if __name__ == "__main__":
    # 'human', 'ai_random', 'ai_handcraft', 'ai_nnue'
    player_one="ai_handcraft"
    player_two="ai_nnue"
    
    #to run the testing(DO NOT use human here)
    #run_parallel_games(player_one, player_two, num_games=10, num_workers=cpu_count()//2)

    #to run the game
    main(player_one, player_two,visualize_game=True)