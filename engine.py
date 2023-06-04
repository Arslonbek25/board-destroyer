import chess
import chess.engine
import numpy as np


piece_names = {
    "white_king": "K",
    "white_queen": "Q",
    "white_rook": "R",
    "white_bishop": "B",
    "white_knight": "N",
    "white_pawn": "P",
    "black_king": "k",
    "black_queen": "q",
    "black_rook": "r",
    "black_bishop": "b",
    "black_knight": "n",
    "black_pawn": "p",
}

engine_path = "/usr/local/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Skill Level": 12})


def get_best_move(fen):
    board = chess.Board(fen)
    result = engine.play(board, chess.engine.Limit(time=0.1))
    engine.quit()
    return str(result.move)


def get_fen(coords, turn):
    fen = ""
    for row in coords:
        empty_sqs = 0
        for square_i, square in enumerate(row):
            if square == "":
                empty_sqs += 1
            if (square != "" or square_i == 7) and empty_sqs:
                fen += str(empty_sqs)
                empty_sqs = 0
            fen += square
        fen += "/"
    return "{} {}".format(fen.rstrip("/"), turn)


def san_to_coords(san, sq_size):
    ranks = "abcdefgh"
    files = "12345678"

    x1 = ranks.index(san[0])
    y1 = 7 - files.index(san[1])
    x2 = ranks.index(san[2])
    y2 = 7 - files.index(san[3])
    coords = (np.array([x1, y1, x2, y2], dtype=float) + 1) * sq_size

    return coords
