import chess
import chess.engine

engine_path = "/usr/local/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Skill Level": 12})


def get_best_move(fen):
    board = chess.Board(fen)
    print(board)
    result = engine.play(board, chess.engine.Limit(time=0.5))
    engine.quit()
    return result
