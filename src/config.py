class TimeControl:
    def __init__(self, min_time, max_time, skill_level, time_advantage=20):
        self.min_time = min_time
        self.max_time = max_time
        self.skill_level = skill_level
        self.time_advantage = time_advantage


class Config:
    rapid = TimeControl(0.5, 15, 3)
    blitz = TimeControl(0.1, 6, 20)
    bullet = TimeControl(0.1, 1, 3)

    time_advantage_percent = 20
    randomness_factor = 0.1
    phase_factors = {
        "opening": 0.4,
        "middlegame": 1,
        "endgame": 0.6,
    }
