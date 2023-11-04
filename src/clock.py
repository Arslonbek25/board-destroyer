import random

import numpy as np


class Clock:
    def __init__(
        self, max_time, time_advantage_percent=25, k=0.3, randomness_factor=0.1
    ):
        self.max_time = max_time
        self.bot_total_time = 0
        self.opponent_total_time = 0
        self.time_advantage_percent = time_advantage_percent
        self.k = k
        self.randomness_factor = randomness_factor
        self.min_time = 0.1
        self.phase_peak_times = {
            "opening": max_time * 0.3,
            "middlegame": max_time * 1,
            "endgame": max_time * 0.8,
        }

    def calculate_move_time(self, opponents_move_time, num_pieces):
        # Scale the peak time based on the game phase
        max_time = self.phase_peak_times.get(self.get_phase(num_pieces), self.max_time)

        # Update the opponent's total time
        self.opponent_total_time += opponents_move_time

        # Maintain the average time advantage
        desired_bot_total_time = (
            1 - self.time_advantage_percent / 100
        ) * self.opponent_total_time

        # Calculate the maximum allowed time for the next move
        max_allowed_time = desired_bot_total_time - self.bot_total_time

        # Symmetrical exponential decay function to determine the base move time
        base_move_time = self.min_time
        if opponents_move_time <= max_time:
            base_move_time += (max_time - self.min_time) * np.exp(
                self.k * (opponents_move_time - max_time)
            )
        else:
            base_move_time += (max_time - self.min_time) * np.exp(
                self.k * (max_time - opponents_move_time)
            )

        # Adjust the move time to be within the allowed maximum time while respecting the minimum time
        move_time = min(base_move_time, max_allowed_time)
        move_time = max(move_time, self.min_time)

        # Add randomness to the move time to avoid predictability
        move_time *= random.uniform(
            1 - self.randomness_factor, 1 + self.randomness_factor
        )

        self.bot_total_time += move_time

        return move_time

    def get_phase(self, num_pieces):
        if num_pieces >= 28:
            return "opening"
        elif num_pieces >= 16:
            return "middlegame"
        else:
            return "endgame"
