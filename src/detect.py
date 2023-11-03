import os

import cv2
import numpy as np
from ultralytics import YOLO

model_path = os.path.join(os.getcwd(), "YOLO_model", "weights", "best.pt")
model = YOLO(model_path)

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
    img = board.img[:, :, :3]
    pos = np.zeros((8, 8), dtype=np.dtype("U1"))
    res = model.predict(img, verbose=False)[0]
    coords = res.boxes.xyxy.numpy().astype(int)[:, 0:2]
    labels = [model.names[int(c)] for c in res.boxes.cls]
    board_height, board_width, _ = img.shape
    for i in range(len(coords)):
        x, y = coords[i]
        posX = round(8 * x / board_width)
        posY = round(8 * y / board_height)
        pos[posY, posX] = piece_names[labels[i]]
    if board.color == "b":
        pos = np.flip(pos, axis=(0, 1))
    return pos


def is_square(A, threshold=10):
    center = sum(A) / 4.0
    rotated_points = [(A[0] - center) * (1j**i) + center for i in range(4)]

    for point in A:
        if not any(abs(point - rp) <= threshold for rp in rotated_points):
            return False

    return True


def getBoardCorners(board):
    board_gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(board_gray, 120, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    largest_area = 0
    largest_contour = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > largest_area:
            largest_area = area
            largest_contour = contour

    epsilon = 0.05 * cv2.arcLength(largest_contour, True)
    corners = cv2.approxPolyDP(largest_contour, epsilon, True)

    if len(corners) == 4 and largest_area > 1000000:
        points = corners.reshape(corners.shape[0], 2)
        complex_points = [x + y * 1j for x, y in points]

        if not is_square(complex_points):
            raise
        return points
    else:
        raise
