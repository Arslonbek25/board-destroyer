import threading

import cv2 as cv
import numpy as np

import control
import detect
from analysis import get_fen, init_engine, is_game_over
from Board import Board

board = Board()

engine = init_engine()

turn = control.get_turn()
color = control.get_color()
first_turn = turn
prev_pos = None


def change_turn():
    global turn
    if turn == "w":
        turn = "b"
    else:
        turn = "w"


def run():
    if is_game_over:
        engine.quit()
        return

    global prev_pos, first_turn, turn

    board.update()
    board.save_screenshot()
    pos = detect.find_pieces(board.img[:, :, :3])
    fen = get_fen(pos, turn, color)
    print(fen)
    if not (prev_pos == pos).all():
        print("Position changed")
        if color == turn:
            print("Playing the move")
            control.play_best_move(board, engine, fen)
        change_turn()
    print(color, turn)
    prev_pos = np.copy(pos)
    threading.Timer(0.1, run).start()


run()
