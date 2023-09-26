import chess.pgn
import numpy as np

import analysis
import control
import detect
from board import Board

board = Board()

turn = control.get_turn()
color = control.get_color()


def change_turn():
    global turn
    turn = "b" if turn == "w" else "w"


def run():
    while True:
        board.update()
        pos = detect.find_pieces(board.img[:, :, :3])
        fen = analysis.get_fen(pos, turn)
        board.set_fen(fen)
        if not np.array_equal(board.prev_pos, pos):
            board_changed = board.prev_pos is not None and pos is not None
            if board_changed:
                move_made = analysis.find_move(board.prev_pos, pos)
                if move_made == "error": # TODO: remove
                    print(board.prev_pos)
                    print(pos) 
                board.board.push_san(move_made)
            our_turn = color == turn
            if our_turn:
                best_move = board.get_best_move()
                control.play_best_move(board, best_move)
            change_turn()
            board.prev_pos = np.copy(pos)
        game = chess.pgn.Game.from_board(board.board)
        print(game) # TODO: remove
        print("FEN", board.board.fen())
        is_game_over = board.board.is_game_over()
        if is_game_over:
            print("Game over")
            break


if __name__ == "__main__":
    run()
