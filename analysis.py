import numpy as np


def get_fen(coords, turn):
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


def san_to_coords(san, sq_size):
    ranks = "abcdefgh"
    files = "12345678"

    x1 = ranks.index(san[0])
    y1 = 7 - files.index(san[1])
    x2 = ranks.index(san[2])
    y2 = 7 - files.index(san[3])
    coords = (np.array([x1, y1, x2, y2], dtype=float) + 1) * sq_size

    return coords


def to_uci(x, y):
    return chr(97 + y) + str(8 - x)


def find_move(before, after):
    indices_to_files = "abcdefgh"
    diff = before != after
    changed_indices = np.argwhere(diff)

    # Find the moved piece's original and new positions
    moved_piece_pos_before = [pos for pos in changed_indices if before[tuple(pos)]]
    moved_piece_pos_after = [pos for pos in changed_indices if after[tuple(pos)]]

    if len(changed_indices) == 2:  # Regular move or capture
        square1, square2 = changed_indices
        # Identify which square contains the moved piece in 'after'
        if after[tuple(square1)] != "":
            from_square, to_square = square2, square1
        else:
            from_square, to_square = square1, square2

        from_file, from_rank = from_square[::-1]
        to_file, to_rank = to_square[::-1]
        move = f"{indices_to_files[from_file]}{8-from_rank}{indices_to_files[to_file]}{8-to_rank}"
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


if __name__ == "__main__":
    # Tests
    prev = np.array(
        [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ],
        dtype=np.dtype("U1"),
    )

    after = np.array(
        [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ],
        dtype=np.dtype("U1"),
    )
    print(find_move(prev, after))  # e4e5

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
