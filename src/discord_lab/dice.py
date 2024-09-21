from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import re
from secrets import randbelow
from typing import override


class DieParseException(Exception):
    pass


@dataclass
class DieRoll:
    value: int
    type: DieType


class DieType(IntEnum):
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

    def roll(self) -> DieRoll:
        return DieRoll(randbelow(self) + 1, self)


@dataclass(frozen=True)
class DieMultiplier:
    type: DieType
    multiplier: int

    def __post_init__(self):
        if self.multiplier < 1:
            raise ValueError(f'Die multiplier {self.multiplier} is less than 1')

    def roll(self) -> tuple[int,list[DieRoll]]:
        rolls = [self.type.roll() for x in range(self.multiplier)]

        return sum(r.value for r in rolls), rolls


    @staticmethod
    def parse(die_mult: str) -> DieMultiplier:

        # regex for parsing "3D6" style die side and multiplier strings
        match = re.match(r'^(\d+)?[dD](\d+)$', die_mult.strip())

        if not match:
            raise DieParseException(f'"{die_mult}" is invalid. Should be of the form D20 or 3D6.')
        
        mult = int(match.group(1) or "1")
        parsed_sides = int(match.group(2))
        
        try:
            die_type = DieType(parsed_sides)
        except ValueError:
            valid_sides = ', '.join([str(x.value) for x in DieType])
            raise DieParseException(f'{parsed_sides}-sided dice not supported. Must be one of: {valid_sides}')

        return DieMultiplier(die_type, mult)

    @override
    def __str__(self) -> str:
        return f"{self.multiplier}{self.type.name}"

