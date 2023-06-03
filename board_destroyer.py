import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
from engine import get_best_move

# TODO: save images in memory after loading them to save computing time

# Load and resize the image
img_board = cv2.imread("assets/cb4.png")
resize_factor = 800 / (sum(img_board.shape[:2]) / 2)
img_board = cv2.resize(img_board, (0, 0), fx=resize_factor, fy=resize_factor)

# Convert to grayscale
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)

# Calculate the square size
bh, bw = img_board_gray.shape
sq_size = int((bh + bw) / 16 * 0.97)

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
coords = np.zeros((8, 8), dtype=np.dtype("U1"))


def find_piece(board, piece):
    img_piece = cv2.resize(
        cv2.imread(f"assets/{piece}.png", cv2.IMREAD_UNCHANGED),
        (sq_size, sq_size),
    )
    img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)
    h, w = img_piece_gray.shape

    img_piece_inverted = cv2.bitwise_not(img_piece_gray)
    if piece.startswith("black"):
        mask = cv2.threshold(img_piece_inverted, 70, 255, cv2.THRESH_BINARY)[1]
    else:
        mask = img_piece[:, :, 3]

    matches = cv2.matchTemplate(board, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
    locs = np.where(matches <= 0.095)
    rects = [(x, y, x + w, y + h) for x, y in zip(*locs[::-1])]

    return non_max_suppression(np.array(rects))


# Highlight all pieces
for piece_name, key in piece_names.items():
    pieces = find_piece(img_board_gray, piece_name)
    for piece in pieces:
        x, y, h, w = piece
        posX = round(8 * x / bw)
        posY = round(8 * y / bh)
        cv2.rectangle(img_board, (x, y), (h, w), (0, 0, 255), 3)
        coords[posY, posX] = key


def get_fen(coords):
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


cv2.imshow("Chess", img_board)
cv2.waitKey()

turn = None
while turn not in ["b", "w"]:
    turn = input("Whose turn is it? (b/w): ")


fen = get_fen(coords)

best_move = get_best_move(fen)


def san_to_coords(san):
    ranks = "abcdefgh"
    files = "12345678"
    x1 = ranks.index(san[0])
    y1 = 7 - files.index(san[1])
    x2 = ranks.index(san[2])
    y2 = 7 - files.index(san[3])
    return [x1, y1, x2, y2]


move_coords = san_to_coords(str(best_move.move))
move_coords = list(map(lambda z: z * sq_size, move_coords))
print(move_coords)
