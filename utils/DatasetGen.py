import platform
import random
import time
import urllib.parse
import webbrowser

import chess
import pyautogui


def random_pawns(piece):
    return (
        "".join(random.sample([piece] * 3 + ["1"] * 5, 8))
        .replace("11111", "5")
        .replace("1111", "4")
        .replace("111", "3")
        .replace("11", "2")
    )


def generate_balanced_chess_com_links(n, num_moves=10):
    base_url = "https://www.chess.com/practice/custom?"
    links = []
    fen = f"rnbqkbnr/{random_pawns('p')}/8/8/8/8/{random_pawns('P')}/RNBQKBNR w KQkq - 0 1"

    for _ in range(n):
        board = chess.Board(fen)
        moves_made = []

        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            non_capture_moves = [
                move for move in legal_moves if not board.is_capture(move)
            ]

            if not non_capture_moves:
                moves_made = []
                board.set_fen(fen)
                break

            move = random.choice(non_capture_moves)
            moves_made.append(move.uci())
            board.push(move)

        encoded_moves = "%20".join(moves_made)
        links.append(
            f"{base_url}fen={urllib.parse.quote(fen)}&moveList={encoded_moves}"
        )

    return links


def open_and_close_links(links, wait_time=5):
    for link in links:
        print(link)
        webbrowser.open(link)
        time.sleep(wait_time)

        # close the tab
        if platform.system() == "Darwin":  # macOS
            print("CLOSING TAB")
            pyautogui.hotkey("command", "w")
        elif platform.system() == "Windows":
            pyautogui.hotkey("ctrl", "w")
        time.sleep(1)


if __name__ == "__main__":
    links = generate_balanced_chess_com_links(5, 95)
    open_and_close_links(links)
