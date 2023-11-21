import analysis
import control
import detect
from board import Board


def run():
    board = Board()
    while not board.game_over():
        board.update()
        board.pos = detect.find_pieces(board)
        is_first_move = board.prev_pos is None
        if is_first_move:
            fen = analysis.get_fen(board.pos, board.turn)
            board.set_fen(fen)
        if board.pos_changed():
            if not board.is_our_turn():
                if not is_first_move:
                    move_made = analysis.find_move(board)
                    board.push_move(move_made)
                board.switch_turn(is_first_move)
            if board.is_our_turn():
                best_move = board.get_best_move()
                board.push_move(best_move)
                control.play_move(board, best_move)
                board.pos = analysis.get_board_position(board.board)
                board.switch_turn()
    print("Game over\n")


if __name__ == "__main__":
    run()
