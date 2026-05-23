import random

import numpy as np


class Clock:
    def __init__(self, config):
        self.config = config
        self.bot_total_time = 0
        self.opponent_total_time = 0

    @property
    def tc(self):
        # Always read the current time_control so UI slider edits propagate.
        return self.config.time_control

    def calculate_move_time(self, opponents_move_time, num_pieces):
        tc = self.config.time_control
        k = self.config.k
        randomness_factor = self.config.randomness_factor
        time_advantage = self.config.time_advantage

        self.opponent_total_time += opponents_move_time

        phase = self.get_phase(num_pieces)
        max_time = tc.max_time * self.config.phase_factors[phase]

        base_move_time = self._base_time(opponents_move_time, max_time, tc.min_time, k)

        desired_bot_total_time = (1 - time_advantage / 100) * self.opponent_total_time

        if self.bot_total_time > desired_bot_total_time:
            adjustment_factor = 0.5
            time_difference = desired_bot_total_time - self.bot_total_time
            move_time = base_move_time + adjustment_factor * time_difference
        else:
            move_time = base_move_time

        move_time = min(move_time, opponents_move_time)
        move_time = min(max(move_time, tc.min_time), max_time)

        move_time *= random.uniform(1 - randomness_factor, 1 + randomness_factor)

        self.bot_total_time += move_time
        return move_time

    def get_phase(self, num_pieces):
        if num_pieces >= 28:
            return "opening"
        elif num_pieces >= 16:
            return "middlegame"
        elif num_pieces >= 6:
            return "endgame"
        else:
            return "late_endgame"

    def _base_time(self, opponents_move_time, max_time, min_time, k):
        if opponents_move_time <= max_time:
            return min_time + (max_time - min_time) * np.exp(
                k * (opponents_move_time - max_time)
            )
        else:
            return min_time + (max_time - min_time) * np.exp(
                k * (max_time - opponents_move_time)
            )
