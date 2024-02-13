import os
import platform
import random
import sys
import time
import urllib.parse
import webbrowser

import chess
import pyautogui

from src.config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from board import Board


def random_pawns(piece):
    return (
        "".join(random.sample([piece] * 3 + ["1"] * 5, 8))
        .replace("11111", "5")
        .replace("1111", "4")
        .replace("111", "3")
        .replace("11", "2")
    )


def generate_balanced_chess_com_links(n_pos, num_moves=10, site="chess"):
    base_url = "https://www.chess.com/practice/custom?"
    lichess_base_url = "https://lichess.org/editor/"
    links = []

    for _ in range(n_pos):
        fen = f"rnbqkbnr/{random_pawns('p')}/8/8/8/8/{random_pawns('P')}/RNBQKBNR w KQkq - 0 1"
        board = chess.Board(fen)
        moves_made = []

        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            non_capture_moves = [
                move for move in legal_moves if not board.is_capture(move)
            ]

            if not non_capture_moves:
                moves_made = []
                break

            move = random.choice(non_capture_moves)
            moves_made.append(move.uci())
            board.push(move)

        if len(moves_made) != num_moves:
            continue

        # print("Move history", moves_made)
        print("FEN:", board.fen())  # Print the FEN of the board

        encoded_moves = "%20".join(moves_made)
        if site == "chess":
            links.append(
                f"{base_url}fen={urllib.parse.quote(board.fen())}&moveList={encoded_moves}"
            )
        elif site == "lichess":
            links.append(f"{lichess_base_url}{board.fen()}")

    return links


def open_and_close_links(links, wait_time=3):
    board = None
    config = Config()
    config.load()

    for link in links:
        webbrowser.open(link)
        time.sleep(wait_time)

        if board is None:
            time.sleep(2)

            board = Board(util=True)

        board.update()
        board.save_screenshot()
        if platform.system() == "Darwin":  # macOS
            pyautogui.hotkey("command", "w")
        elif platform.system() == "Windows":
            pyautogui.hotkey("ctrl", "w")
    print(f"Generated {len(links)} dataset instances")


if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)

    # num_moves has to be an even number to prevent the bot making a move
    links = generate_balanced_chess_com_links(n_pos=5, num_moves=40, site="lichess")
    open_and_close_links(links)
