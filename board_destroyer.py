import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

# TODO: save images in memory after loading them to save computing time
img_board = cv2.imread("assets/cb.png")
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)

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

def find_piece(board, piece):
    square_size = int((board.shape[0] / 8 + board.shape[1] / 8) / 2 * 0.97)

    img_piece = cv2.resize(
        cv2.imread(f"assets/{piece}.png", cv2.IMREAD_UNCHANGED),
        (square_size, square_size),
    )
    img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)

    h, w = img_piece_gray.shape
    img_piece_inverted = cv2.bitwise_not(img_piece_gray)
    if piece.startswith("black"):
        mask = cv2.threshold(img_piece_inverted, 100, 255, cv2.THRESH_BINARY)[1]
    else:
        mask = img_piece[:, :, 3]

    matches = cv2.matchTemplate(board, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
    locs = np.where(matches <= 0.1)
    rects = [(x, y, x + w, y + h) for x, y in zip(*locs[::-1])]

    return non_max_suppression(np.array(rects))


# Highlight all pieces
for piece_name in piece_names.keys():
    pieces = find_piece(img_board_gray, piece_name)
    for piece in pieces:
        x, y, h, w = piece
        cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 5)

cv2.imshow("Chess", img_board)
cv2.waitKey()
