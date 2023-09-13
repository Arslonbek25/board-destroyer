import chess
import chess.engine
import numpy as np

is_game_over = False


def init_engine():
    engine_path = "/usr/local/bin/stockfish"
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine.configure({"Skill Level": 20})
    return engine


def get_best_move(fen, engine):
    board = chess.Board(fen)
    is_game_over = board.is_game_over()
    result = engine.play(board, chess.engine.Limit(time=1))
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


if __name__ == "__main__":
    # fen = "r1bq1rk1/1pp1nppp/1b1p1n2/pP2p3/PNB1P3/1QPP1N2/5PPP/RNB1K2R w"
    # board = chess.Board(fen)
    # engine_path = "/usr/local/bin/stockfish"

    # engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    # info = engine.analyse(board, chess.engine.Limit(time=0.1))
    # best_move = info["pv"][0]
    # print(best_move)
    engine = init_engine()
    fen2 = "r1bq1rk1/1pp1nppp/1b1p1n2/pP2p3/PNB1P3/1QPP1N2/5PPP/R1BQK2R w KQ - 0 1"
    fen = "r1bq1rk1/1pp1nppp/1b1p1n2/pP2p3/PNB1P3/1QPP1N2/5PPP/RNB1K2R w KQ - 0 1"

    print(get_best_move(fen, engine))
    engine.quit()
