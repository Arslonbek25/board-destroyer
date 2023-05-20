import cv2
import numpy as np

# Load the chess board and chess piece images
img_board = cv2.imread('assets/cb.png')
img_piece = cv2.imread('assets/black_pawn.png', cv2.IMREAD_UNCHANGED)

mask = img_piece[:,:,3] # use the inverted transparency channel for mask


# Convert both images to grayscale
img_board_gray = cv2.cvtColor(img_board, cv2.COLOR_BGR2GRAY)
img_piece_gray = cv2.cvtColor(img_piece, cv2.COLOR_BGR2GRAY)
h, w = img_piece_gray.shape

# Apply morphological operations to extract the chess piece from the board
#kernel = np.ones((5, 5), np.uint8)
#img_piece_mask = cv2.erode(img_piece_gray, kernel, iterations=1)
#img_piece_mask = cv2.dilate(img_piece_mask, kernel, iterations=1)


result = cv2.matchTemplate(img_board_gray, img_piece_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

while min_val < 0.1:

    # Draw a rectangle around the matching location
    top_left = min_loc
    bottom_right = (top_left[0] + img_piece.shape[1], top_left[1] + img_piece.shape[0])
    cv2.rectangle(img_board, top_left, bottom_right, (0, 0, 255), 2)

    #overwrite the portion of the result that has the match:
    h1 = top_left[1]-h//2
    h1 = np.clip(h1, 0, result.shape[0])

    h2 = top_left[1] + h//2 + 1
    h2 = np.clip(h2, 0, result.shape[0])

    w1 = top_left[0] - w//2
    w1 = np.clip(w1, 0, result.shape[1])

    w2 = top_left[0] + w//2 + 1
    w2 = np.clip(w2, 0, result.shape[1])
    result[h1:h2, w1:w2] = 1  # poison the result in the vicinity of this match so it isn't found again

    # look for next match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

cv2.imwrite('output.png', img_board)

# Show the result
cv2.imshow('Result', img_board)
cv2.waitKey(0)
cv2.destroyAllWindows()
