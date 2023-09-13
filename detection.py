import cv2
import numpy as np


def is_square(A, threshold=10):
    center = sum(A) / 4.0
    rotated_points = [(A[0] - center) * (1j**i) + center for i in range(4)]

    for point in A:
        if not any(abs(point - rp) <= threshold for rp in rotated_points):
            return False

    return True


def getChessboardCorners(board):
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
