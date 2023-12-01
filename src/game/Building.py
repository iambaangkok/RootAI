from enum import StrEnum


class Building(StrEnum):
    EMPTY = 'empty'
    RUIN = 'ruin'
    SAWMILL = 'sawmill'
    WORKSHOP = 'workshop'
    RECRUITER = 'recruiter'
    ROOST = 'roost'
    BASE = 'base'

    def to_number(self) -> int:
        mapping: dict[str, int] = {
            "EMPTY": 0,
            "RUIN": 1,
            "SAWMILL": 2,
            "WORKSHOP": 3,
            "RECRUITER": 4,
            "ROOST": 5,
            "BASE": 6,
        }
        return mapping[self.name]
