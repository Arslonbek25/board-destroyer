import cv2
import numpy as np

from controls import get_prop, playMove
from detection import getChessboardCorners, find_piece, find_all_pieces
from engine import get_best_move, get_fen, san_to_coords, piece_names


img_board = cv2.imread("assets/screenshot-4.png")
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)

prop = get_prop(img_board_gray)
corners = getChessboardCorners(img_board_gray)
topLeftCorner = corners[0]
img_board = img_board[corners[0, 1] : corners[2, 1], corners[0, 0] : corners[2, 0]]

bh, bw = img_board.shape[:2]
sq_size_orig = int((bh + bw) / 16 * 0.99)

scale = 800 / img_board.shape[0]

img_board = cv2.resize(img_board, (0, 0), fx=scale, fy=scale)
bh, bw = img_board.shape[:2]
sq_size = int((bh + bw) / 16 * 0.99)

img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)

coords = find_all_pieces(img_board_gray, sq_size, bw, bh)


def getTurn():
    turn = ""
    while turn not in ["b", "w"]:
        turn = input("Whose turn is it? (b/w): ")


def play_best_move(fen):
    best_move = get_best_move(fen)
    move_coords = san_to_coords(best_move, sq_size_orig)

    move_coords[:2] += topLeftCorner - sq_size / 2
    move_coords[2:] += topLeftCorner - sq_size / 2

    playMove(move_coords, prop)


turn = getTurn()
fen = get_fen(coords, turn)

play_best_move(fen)
