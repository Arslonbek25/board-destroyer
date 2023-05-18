import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

img_board = cv2.imread("assets/cb.png")
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)

piece_names = {
    # "white_king": "K",
    # "white_queen": "Q",
    # "white_rook": "R",
    # "white_bishop": "B",
    # "white_knight": "N",
    # "white_pawn": "P",
    "black_king": "k",
    "black_queen": "q",
    "black_rook": "r",
    "black_bishop": "b",
    "black_knight": "n",
    "black_pawn": "p",
}


def find_piece(board, piece):
    img_piece = cv2.imread(f"assets/{piece}.png", cv2.IMREAD_UNCHANGED)
    img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)

    h, w = img_piece_gray.shape
    mask = img_piece[:, :, 3]

    res = cv2.matchTemplate(board, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
    loc = np.where(res <= 0.1)

    rects = [(x, y, x + w, y + h) for x, y in zip(*loc[::-1])]

    return non_max_suppression(np.array(rects))


# Highlight all pieces
# for piece_name in piece_names.keys():
#     print(piece_name)
#     pieces = find_piece(img_board_gray, piece_name)
#     for r in pieces:
#         x, y, h, w = r
#         cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 5)

# Testing one piece
# pieces = find_piece(img_board_gray, "black_pawn")
# for r in pieces:
#     x, y, h, w = r
#     cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 5)

cv2.imshow("Chess", img_board_gray)
cv2.waitKey()
cv2.imshow("Chess", cv2.imread("assets/white_pawn.png", 0))
cv2.waitKey()
