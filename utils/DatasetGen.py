import os
import platform
import random
import time
import urllib.parse
import webbrowser

import chess
import pyautogui

from Board import Board


def random_pawns(piece):
    return (
        "".join(random.sample([piece] * 3 + ["1"] * 5, 8))
        .replace("11111", "5")
        .replace("1111", "4")
        .replace("111", "3")
        .replace("11", "2")
    )


def generate_balanced_chess_com_links(n_pos, num_moves=10):
    base_url = "https://www.chess.com/practice/custom?"
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

        encoded_moves = "%20".join(moves_made)
        links.append(
            f"{base_url}fen={urllib.parse.quote(fen)}&moveList={encoded_moves}"
        )

    return links


def open_and_close_links(links, wait_time=5):
    board = None
    for link in links:
        webbrowser.open(link)
        time.sleep(wait_time)

        if board is None:
            board = Board()

        board.update()
        board.save_screenshot()
        if platform.system() == "Darwin":  # macOS
            pyautogui.hotkey("command", "w")
        elif platform.system() == "Windows":
            pyautogui.hotkey("ctrl", "w")


if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)

    # num_moves has to be an even number to prevent the bot making a move
    links = generate_balanced_chess_com_links(n_pos=10, num_moves=64)
    open_and_close_links(links)
