import os
import time

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
piece_names_by_id = {
    int(k): piece_names.get(v, v) for k, v in getattr(model, "names", {}).items()
}


def find_pieces(board, recorder=None):
    img = board.img[:, :, :3]
    pos = np.zeros((8, 8), dtype=np.dtype("U1"))
    
    t0 = time.perf_counter()
    res = model.predict(img, verbose=False)[0]
    t1 = time.perf_counter()
    # timing handled by caller for metrics
    coords = res.boxes.xyxy.numpy().astype(int)[:, 0:2]
    labels = res.boxes.cls.tolist() if hasattr(res.boxes.cls, "tolist") else list(res.boxes.cls)
    board_height, board_width, _ = img.shape
    for i in range(len(coords)):
        x, y = coords[i]
                # floor + clamp to avoid posX/posY becoming 8 due to rounding near edges
        posX = int(8 * x / board_width)
        posY = int(8 * y / board_height)

        # clamp to [0..7]
        if posX < 0:
            posX = 0
        elif posX > 7:
            posX = 7

        if posY < 0:
            posY = 0
        elif posY > 7:
            posY = 7


        raw_label = labels[i] if i < len(labels) else None
        label_id = None
        label_name = None

        if isinstance(raw_label, (int,)):
            label_id = int(raw_label)
        elif isinstance(raw_label, str):
            s = raw_label.strip()
            if s.isdigit():
                label_id = int(s)
            else:
                label_name = s
        else:
            try:
                label_id = int(raw_label)
            except Exception:
                label_name = str(raw_label)

        if label_id is not None and label_name is None:
            try:
                label_name = model.names.get(label_id) if isinstance(model.names, dict) else None
            except Exception:
                label_name = None

        piece = None
        if label_id is not None:
            piece = piece_names_by_id.get(label_id)
        elif label_name is not None:
            piece = piece_names.get(label_name, label_name)
        
        if not (0 <= posX < 8 and 0 <= posY < 8):
            if recorder is not None:
                recorder.event(
                    "oob_detection",
                    posX=int(posX),
                    posY=int(posY),
                    label_id=label_id,
                    label_name=label_name,
                    raw_label=str(raw_label),
                    raw_x=float(x),
                    raw_y=float(y),
                    board_w=float(board_width),
                    board_h=float(board_height),
                    corners=board.corners.tolist()
                    if hasattr(board, "corners") and board.corners is not None
                    else None,
                )
            continue

        if piece is None:
            continue

        pos[posY, posX] = piece
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
