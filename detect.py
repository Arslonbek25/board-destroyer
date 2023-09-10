import os

import cv2 as cv
import numpy as np
from ultralytics import YOLO

model_path = os.path.join(os.getcwd(), "model", "weights", "best.pt")
model = YOLO(model_path)


def draw_boxes(board, xyxy_coords, class_names):
    for box, label in zip(xyxy_coords, class_names):
        x1, y1, x2, y2 = box
        cv.rectangle(board, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv.putText(
            board, label, (x1, y1 + 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 6
        )

    cv.imshow("Result", board)
    cv.waitKey(0)
    cv.destroyAllWindows()


piece_names = {
    "white-king": "K",
    "white-queen": "Q",
    "white-rook": "R",
    "white-bishop": "B",
    "white-knight": "N",
    "white-pawn": "P",
    "black-king": "k",
    "black-queen": "q",
    "black-rook": "r",
    "black-bishop": "b",
    "black-knight": "n",
    "black-pawn": "p",
}


def find_pieces(board):
    pos = np.zeros((8, 8), dtype=np.dtype("U1"))
    res = model.predict(board)[0]
    coords = res.boxes.xyxy.numpy().astype(int)[:, 0:2]
    labels = [model.names[int(c)] for c in res.boxes.cls]
    board_height, board_width, _ = board.shape

    for i in range(len(coords)):
        x, y = coords[i]
        posX = round(8 * x / board_width)
        posY = round(8 * y / board_height)
        pos[posY, posX] = piece_names[labels[i]]

    return pos
