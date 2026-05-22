import json
from dataclasses import dataclass, fields
from enum import Enum


class Color(str, Enum):
    WHITE = "w"
    BLACK = "b"

    def __str__(self) -> str:
        return self.value


@dataclass
class TimeControl:
    min_time: float
    max_time: float
    skill_level: int
    depth: int | None = None


@dataclass
class Config:
    debug: bool
    color: Color
    time_control_name: str
    time_controls: dict[str, TimeControl]
    game_running: bool
    time_advantage: int
    lines: int
    randomness_factor: float
    k: float
    phase_factors: dict[str, float]

    DEFAULT_PATH = "src/settings.json"

    @classmethod
    def load(cls, path: str = DEFAULT_PATH) -> "Config":
        with open(path, "r") as file:
            raw = json.load(file)

        expected = {f.name for f in fields(cls)}
        got = set(raw.keys())
        missing = expected - got
        unknown = got - expected
        if missing or unknown:
            parts = []
            if missing:
                parts.append(f"missing keys: {sorted(missing)}")
            if unknown:
                parts.append(f"unknown keys: {sorted(unknown)}")
            raise ValueError(f"settings.json schema mismatch — {'; '.join(parts)}")

        raw["color"] = Color(raw["color"])
        raw["time_controls"] = {
            name: TimeControl(**tc) for name, tc in raw["time_controls"].items()
        }

        cfg = cls(**raw)
        cfg._validate()
        return cfg

    def save(self, path: str = DEFAULT_PATH) -> None:
        payload = {
            "debug": self.debug,
            "color": self.color.value,
            "time_control_name": self.time_control_name,
            "time_controls": {
                name: tc.__dict__ for name, tc in self.time_controls.items()
            },
            "game_running": self.game_running,
            "time_advantage": self.time_advantage,
            "lines": self.lines,
            "randomness_factor": self.randomness_factor,
            "k": self.k,
            "phase_factors": self.phase_factors,
        }
        with open(path, "w") as file:
            json.dump(payload, file, indent=4)

    @property
    def time_control(self) -> TimeControl:
        return self.time_controls[self.time_control_name]

    def _validate(self) -> None:
        if self.lines < 0:
            raise ValueError(f"lines must be >= 0, got {self.lines}")
        if not 0.0 <= self.randomness_factor <= 1.0:
            raise ValueError(
                f"randomness_factor must be in [0, 1], got {self.randomness_factor}"
            )
        if self.time_control_name not in self.time_controls:
            raise ValueError(
                f"time_control_name {self.time_control_name!r} not in time_controls"
            )
        for name, tc in self.time_controls.items():
            if not 0 <= tc.skill_level <= 20:
                raise ValueError(
                    f"time_controls[{name}].skill_level must be in [0, 20], got {tc.skill_level}"
                )
            if tc.min_time < 0 or tc.max_time < 0:
                raise ValueError(
                    f"time_controls[{name}] times must be >= 0"
                )
            if tc.min_time > tc.max_time:
                raise ValueError(
                    f"time_controls[{name}].min_time > max_time"
                )
