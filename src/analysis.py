import chess
import numpy as np


def get_fen(coords, turn):
    fen = []
    for rank in coords:
        row = []
        empty = 0
        for square in rank:
            if square:
                if empty:
                    row.append(str(empty))
                    empty = 0
                row.append(square)
            else:
                empty += 1
        if empty:
            row.append(str(empty))
        fen.append("".join(row))

    return "/".join(fen) + f" {turn}"


def find_move(board):
    before, after = board.prev_pos, board.pos
    indices_to_files = "abcdefgh"
    diff = before != after
    changed_indices = np.argwhere(diff)

    # Find the moved piece's original and new positions
    moved_piece_pos_before = [pos for pos in changed_indices if before[tuple(pos)]]
    moved_piece_pos_after = [pos for pos in changed_indices if after[tuple(pos)]]

    # If a pawn reaches the last rank, it must be promoted.
    # Determine if a promotion has occurred
    def detect_promotion(from_square, to_square, after_board):
        from_piece = before[tuple(from_square)]
        to_piece = after_board[tuple(to_square)]
        # Check if the piece moved from the second to the last rank
        if from_piece in "Pp" and ((from_piece.isupper() and to_square[0] == 0) or (from_piece.islower() and to_square[0] == 7)):
            # Return lowercase for UCI format
            return to_piece.lower() 
        return None

    if len(changed_indices) == 2:  # Regular move or capture
        # Identify which square contains the moved piece in 'after'
        if after[tuple(changed_indices[0])]:
            from_square, to_square = changed_indices[1], changed_indices[0]
        else:
            from_square, to_square = changed_indices[0], changed_indices[1]

        from_file, from_rank = from_square[::-1]
        to_file, to_rank = to_square[::-1]

        # Convert board indices to chess square
        move = f"{indices_to_files[from_file]}{8-from_rank}{indices_to_files[to_file]}{8-to_rank}"

        # Check for promotion and append promotion piece if there was a promotion
        promotion_piece = detect_promotion(from_square, to_square, after)
        if promotion_piece:
            move += promotion_piece  # For UCI, promotion piece is appended directly
        return move

    elif len(changed_indices) == 4:
        # Castling
        if (
            "K" in before[tuple(moved_piece_pos_before[0])]
            or "k" in before[tuple(moved_piece_pos_before[0])]
        ):
            if (
                abs(moved_piece_pos_before[0][1] - moved_piece_pos_after[1][1]) == 2
            ):  # Kingside
                return (
                    "e1g1"
                    if before[tuple(moved_piece_pos_before[0])] == "K"
                    else "e8g8"
                )
            else:  # Queenside
                return (
                    "e1c1"
                    if before[tuple(moved_piece_pos_before[0])] == "K"
                    else "e8c8"
                )
        # En-passant
        else:
            start = moved_piece_pos_before[0]
            end = moved_piece_pos_after[0]
            start_file, start_rank = start[::-1]
            end_file, end_rank = end[::-1]
            move = f"{indices_to_files[start_file]}{8-start_rank}{indices_to_files[end_file]}{8-end_rank}"
            return move

    return "error"


def get_board_position(board):
    position = []
    for rank in range(8, 0, -1):
        row = []
        for file in range(1, 9):
            piece = board.piece_at(chess.square(file - 1, rank - 1))
            if piece:
                row.append(piece.symbol())
            else:
                row.append("")
        position.append(row)
    return position


if __name__ == "__main__":
    # Tests
    prev = np.array(
        [
            ["R", "N", "B", "Q", "K", "B", "", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["", "", "", "", "", "N", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "p", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["p", "p", "p", "", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"],
        ],
        dtype=np.dtype("U1"),
    )

    # after = np.array(
    #     [
    #         ["r", "n", "b", "q", "k", "b", "n", "r"],
    #         ["p", "p", "p", "p", "p", "p", "p", ""],
    #         ["", "", "", "", "", "", "", ""],
    #         ["", "", "", "", "", "", "", "p"],
    #         ["", "", "", "", "", "", "", ""],
    #         ["", "", "", "", "", "", "", ""],
    #         ["P", "P", "P", "P", "P", "P", "P", "P"],
    #         ["R", "N", "B", "Q", "K", "B", "N", "R"],
    #     ],
    #     dtype=np.dtype("U1"),
    # )

#     prev = np.array([
#     ["r", "n", "b", "q", "k", "b", "n", "r"],
#     ["p", "p", "p", "p", "p", "p", "p", "p"],
#     ["", "", "", "", "", "", "", ""],
#     ["", "", "", "", "", "", "", ""],
#     ["", "", "", "", "", "", "", ""],
#     ["", "", "", "", "", "", "", ""],
#     ["P", "P", "P", "P", "P", "P", "P", "P"],
#     ["R", "N", "B", "Q", "K", "B", "N", "R"]
# ], dtype=np.dtype("U1"))

#     after = np.array([
#         ["r", "n", "b", "q", "k", "b", "n", "r"],
#         ["p", "p", "p", "p", "p", "p", "p", "p"],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "N", "", ""],
#         ["P", "P", "P", "P", "P", "P", "P", "P"],
#         ["R", "N", "B", "Q", "K", "B", "", "R"]
#     ], dtype=np.dtype("U1"))
#     print(find_move(prev, after))  # g1f3

# prev = np.array(
#     [
#         ["r", "n", "b", "q", "k", "b", "n", "r"],
#         ["p", "p", "p", "p", "p", "p", "p", "p"],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["P", "P", "P", "P", "P", "P", "P", "P"],
#         ["R", "N", "B", "Q", "K", "B", "N", "R"],
#     ],
#     dtype=np.dtype("U1"),
# )

# after = np.array(
#     [
#         ["r", "n", "b", "q", "k", "b", "n", "r"],
#         ["p", "p", "p", "p", "p", "p", "p", "p"],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "P", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["P", "P", "P", "P", "", "P", "P", "P"],
#         ["R", "N", "B", "Q", "K", "B", "N", "R"],
#     ],
#     dtype=np.dtype("U1"),
# )
# print(find_move(prev, after))  # e2e4

# prev = np.array(
#     [
#         ["r", "n", "b", "q", "k", "b", "n", "r"],
#         ["p", "p", "p", "", "p", "p", "p", "p"],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "p", "", "", "", ""],
#         ["", "", "", "", "P", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["P", "P", "P", "P", "", "P", "P", "P"],
#         ["R", "N", "B", "Q", "K", "", "", "R"],
#     ],
#     dtype=np.dtype("U1"),
# )
# after = np.array(
#     [
#         ["r", "n", "b", "q", "k", "b", "n", "r"],
#         ["p", "p", "p", "", "p", "p", "p", "p"],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "P", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["", "", "", "", "", "", "", ""],
#         ["P", "P", "P", "P", "", "P", "P", "P"],
#         ["R", "N", "B", "Q", "K", "", "", "R"],
#     ],
#     dtype=np.dtype("U1"),
# )  # Move: d2d4

# print(find_move(prev, after))
