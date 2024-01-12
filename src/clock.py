import random

import numpy as np


class Clock:
    def __init__(self, config_instance):
        self.config_instance = config_instance
        self.tc = config_instance.time_control
        self.time_advantage = config_instance.time_advantage
        self.k = config_instance.k
        self.randomness_factor = config_instance.randomness_factor
        self.bot_total_time = 0
        self.opponent_total_time = 0

    def calculate_move_time(self, opponents_move_time, num_pieces):
        self.tc = self.config_instance.time_control
        print("Time control:", self.config_instance.time_control)
        print(self.tc.min_time, self.tc.max_time, self.tc.skill_level)

        # Update the opponent's total time
        self.opponent_total_time += opponents_move_time

        # Determine the game phase and adjust max_time
        phase = self.get_phase(num_pieces)
        max_time = self.tc.max_time * self.config_instance.phase_factors[phase]

        # Calculate base move time
        base_move_time = self.calculate_base_time(opponents_move_time, max_time)

        # Calculate the desired bot total time to maintain the time advantage
        desired_bot_total_time = (
            1 - self.time_advantage / 100
        ) * self.opponent_total_time

        # Check if the bot needs to catch up or maintain the advantage
        if self.bot_total_time > desired_bot_total_time:
            # Bot needs to catch up
            adjustment_factor = 0.5  # Adjust this factor for smoothness
            time_difference = desired_bot_total_time - self.bot_total_time
            move_time = base_move_time + adjustment_factor * time_difference
        else:
            # Bot has the advantage or is on par, continue with normal play
            move_time = base_move_time

        # Ensure move time is within acceptable range
        move_time = min(move_time, opponents_move_time)
        move_time = min(max(move_time, self.tc.min_time), max_time)

        # Add randomness to avoid predictability
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
