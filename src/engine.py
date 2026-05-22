import threading

import chess
import chess.engine


class Engine:
    def __init__(self, skill_level: int):
        self._engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        self._engine.configure({"Skill Level": skill_level})
        self._calc_thread: threading.Thread | None = None
        self._top_lines: list = []

    def quit(self) -> None:
        self._engine.quit()

    def best_move(
        self, board: chess.Board, time: float | None, depth: int | None
    ) -> str:
        result = self._engine.play(
            board, chess.engine.Limit(time=time, depth=depth)
        )
        return str(result.move)

    def try_anticipated(self, last_move: chess.Move) -> str | None:
        """If anticipation hit a line starting with last_move, return its next ply."""
        if self._calc_thread is None:
            return None
        self._calc_thread.join()
        self._calc_thread = None
        for line in self._top_lines:
            if line and line[0] == last_move and len(line) > 1:
                return str(line[1])
        return None

    def anticipate(self, board: chess.Board, lines: int) -> None:
        if lines <= 0:
            return
        snapshot = board.copy()
        self._calc_thread = threading.Thread(
            target=self._run_anticipation, args=(snapshot, lines)
        )
        self._calc_thread.start()

    def _run_anticipation(self, board: chess.Board, lines: int) -> None:
        result = self._engine.analyse(
            board, chess.engine.Limit(depth=12), multipv=lines
        )
        self._top_lines = [r.get("pv") for r in result]
