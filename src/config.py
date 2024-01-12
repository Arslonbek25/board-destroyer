class TimeControl:
    def __init__(self, min_time, max_time, skill_level, depth=None):
        self.min_time = min_time
        self.max_time = max_time
        self.skill_level = skill_level
        self.depth = depth


class Config:
    rapid = TimeControl(1.5, 15, 3)
    blitz = TimeControl(0.1, 8, 3)
    bullet = TimeControl(0.1, 2, 0)
    puzzle = TimeControl(0.1, 0.3, 20, 16)

    turn = "b"
    color = "b"
    timecontrol = "puzzle"
    
    game_running = False
    time_advantage_percent = 20
    lines = 1
    randomness_factor = 0.15
    k = 0.15  # The rate of change in base time calculation. Faster for larger k values and slower for smaller k values.

    phase_factors = {
        "opening": 0.3,
        "middlegame": 1,
        "endgame": 0.6,
    }
