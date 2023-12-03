from __future__ import annotations

from enum import StrEnum

mapping: dict[str, int] = {
    "EMPTY": 0,
    "RUIN": 1,
    "SAWMILL": 2,
    "WORKSHOP": 3,
    "RECRUITER": 4,
    "ROOST": 5,
    "BASE": 6,
}

reverse_mapping = [key for key in mapping]


class Building(StrEnum):
    EMPTY = 'empty'
    RUIN = 'ruin'
    SAWMILL = 'sawmill'
    WORKSHOP = 'workshop'
    RECRUITER = 'recruiter'
    ROOST = 'roost'
    BASE = 'base'

    def to_number(self) -> int:
        return mapping[self.name]

    def to_building(building_id: int) -> Building:
        return Building(reverse_mapping[building_id])
