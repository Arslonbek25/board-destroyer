class TimeControl:
    def __init__(self, min_time, max_time, skill_level, depth=None):
        self.min_time = min_time
        self.max_time = max_time
        self.skill_level = skill_level
        self.depth = depth


class Config:
    rapid = TimeControl(0.3, 15, 5)
    blitz = TimeControl(0.3, 6, 4)
    bullet = TimeControl(0.1, 0.6, 4)
    puzzle = TimeControl(0.1, 0.3, 20, 20)

    time_advantage_percent = 20
    randomness_factor = 0.15
    k = 0.2
    phase_factors = {
        "opening": 0.3,
        "middlegame": 1,
        "endgame": 0.6,
    }
