import json
from dataclasses import dataclass
from enum import Enum, auto

# TODO: Refactor color to enum
class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def __str__(self):
        return self.name.lower()


@dataclass
class TimeControl:
    min_time: float
    max_time: float
    skill_level: int
    depth: int = None


@dataclass
class Config:
    def load(self):
        with open("src/settings.json", "r") as file:
            settings = json.load(file)
            for key, value in settings.items():
                if key == "time_controls":
                    value = {tc: TimeControl(**v) for tc, v in value.items()}
                setattr(self, key, value)

    def save(self):
        with open("src/settings.json", "w") as file:
            settings = self.__dict__.copy()
            settings["time_controls"] = {
                k: v.__dict__ for k, v in settings["time_controls"].items()
            }
            json.dump(settings, file, indent=4)

    @property
    def time_control(self):
        return self.time_controls[self.time_control_name]
