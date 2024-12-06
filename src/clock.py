import random

import numpy as np


class Clock:
    def __init__(self, config):
        self.config = config
        self.tc = config.time_control
        self.time_advantage = config.time_advantage
        self.k = config.k
        self.randomness_factor = config.randomness_factor
        self.bot_total_time = 0
        self.opponent_total_time = 0

    def calculate_move_time(self, opponents_move_time, num_pieces):
        self.tc = self.config.time_control
        self.opponent_total_time += opponents_move_time

        phase = self.get_phase(num_pieces)
        max_time = self.tc.max_time * self.config.phase_factors[phase]

        base_move_time = self.calculate_base_time(opponents_move_time, max_time)

        desired_bot_total_time = (
            1 - self.time_advantage / 100
        ) * self.opponent_total_time

        if self.bot_total_time > desired_bot_total_time:

            adjustment_factor = 0.5
            time_difference = desired_bot_total_time - self.bot_total_time
            move_time = base_move_time + adjustment_factor * time_difference
        else:
            move_time = base_move_time

        move_time = min(move_time, opponents_move_time)
        move_time = min(max(move_time, self.tc.min_time), max_time)

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
        elif num_pieces >= 6:
            return "endgame"
        else:
            return "late_endgame"

    def calculate_base_time(self, opponents_move_time, max_time):
        if opponents_move_time <= max_time:
            return self.tc.min_time + (max_time - self.tc.min_time) * np.exp(
                self.k * (opponents_move_time - max_time)
            )
        else:
            return self.tc.min_time + (max_time - self.tc.min_time) * np.exp(
                self.k * (max_time - opponents_move_time)
            )


if __name__ == "__main__":
    c = Clock("puzzle")
    for i in range(4):
        opp = random.uniform(0.1, 0.1)
        bot = c.calculate_move_time(opp, 20)
        print(
            f"Opponent {round(opp, 2)}s",
            f"Bot {round(bot, 2)}s",
        )
    s = c.opponent_total_time / c.bot_total_time
    print(round(s, 2), "second advantage")
    print(f"Time advantage {round((s - 1) * 100, 2)}%")
