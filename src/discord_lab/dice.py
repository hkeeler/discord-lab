from dataclasses import dataclass
from enum import IntEnum
import re
from secrets import randbelow

class DieSides(IntEnum):
    FOUR = 4
    SIX = 6
    EIGHT = 8
    TEN = 10
    TWELVE = 12
    TWENTY = 20
    HUNDRED = 100


@dataclass
class Die:
    sides: DieSides

    def roll(self) -> int:
        return randbelow(self.sides) + 1
    

class DieParseException(Exception):
    pass


def parse_die_mult(die_mult: str) -> tuple[Die,int]:
    match = re.match(r'^(\d+)?[dD](\d+)$', die_mult.strip())
    if not match:
        raise DieParseException(f'"{die_mult}" is invalid. Should be of the form D20 or 3D6.')
    
    mult = int(match.group(1) or "1")
    parsed_sides = int(match.group(2))
    
    try:
        sides = DieSides(parsed_sides)
    except ValueError:
        valid_sides = ', '.join([str(x.value) for x in DieSides])
        raise DieParseException(f'{parsed_sides}-sided dice not supported. Must be one of: {valid_sides}')

    die = Die(sides)

    return die, mult


def roll_die_mult(die_mult: str) -> list[int]:
    die, mult = parse_die_mult(die_mult)

    return [die.roll() for d in range(mult)]
