from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import Enum
from importlib.resources import open_binary, open_text
from typing import Optional, override

# FIXME: Fix open_binary and open_text warnings
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

from discord_lab.dice import MultiDie,DieType, MultiDieRoll

import yaml


@dataclass(frozen=True)
class Language:
    name: str


@dataclass(frozen=True)
class Ancestry:
    name: str


class CoinType(Enum):
    GP = 'Gold (GP)'
    SP = 'Silver (SP)'
    CP = 'Copper (CP)'


@dataclass(frozen=True)
class CoinAmount:
    amount: int
    type: CoinType

    @staticmethod
    def parse(coin_amount_str: str) -> CoinAmount:
        try:
            amount_str, coin_type_str = coin_amount_str.split(' ')
            amount = int(amount_str)
            coin_type = CoinType[coin_type_str.upper()]
        except (ValueError, KeyError):
            raise ValueError('Cost must be of the format "5 gp"')

        return CoinAmount(amount, coin_type)

    @override
    def __str__(self) -> str:
        return f'{self.amount} {self.type.name.lower()}'


# TODO: Figure out how to handle coins and gems.
#       Currently removed from basic-gear.csv.
@dataclass(frozen=True)
class Gear:
    id: str
    name: str
    slots: int
    per_slot: int
    free_to_carry: int
    cost: CoinAmount
    description: Optional[str]

    @override
    def __str__(self) -> str:
        per_slot_str = f'-{self.per_slot}' if self.per_slot > 1 else ''
        return f'{self.name} ({self.slots}{per_slot_str})'

    @property
    def is_equipable(self) -> bool:
        return False

    @property
    def is_bundled(self) -> bool:
        return True

    @staticmethod
    def from_csv(csv_dict: dict['str',str]) -> Gear:
        id=csv_dict['id']
        name=csv_dict['name']
        description=csv_dict['description']
        
        try:
            cost = CoinAmount.parse(csv_dict['cost'])
            slots = int(csv_dict['slots'])
            per_slot = int(csv_dict['per_slot'])
            free_to_carry = int(csv_dict['free_to_carry'])
        except ValueError:
            raise ValueError(f'Could not parse "{id}" CSV entry')

        return Gear(
            id=id,
            name=name,
            cost=cost,
            slots=slots,
            per_slot=per_slot,
            free_to_carry=free_to_carry,
            description=description
        )


@dataclass
class GearQuantity:
    gear: Gear
    quantity: int

    @override
    def __str__(self) -> str:
        qty_str = f' x{self.quantity}' if self.quantity > 1 else ''
        return f'{self.gear}{qty_str}'

    @property
    def slots(self) -> int:
        slots, remainder = divmod(self.quantity, self.gear.per_slot)

        if remainder:
            slots +=1

        slots -= self.gear.free_to_carry

        return slots


class Range(Enum):
    C = 'Close'
    N = 'Near'
    F = 'Far'


class WeaponType(Enum):
    M = 'Melee'
    R = 'Ranged'


@dataclass(frozen=True)
class WeaponProperty:
    id: str
    name: str
    description: str

    @staticmethod
    def from_csv(csv_dict: dict['str',str]) -> WeaponProperty:
        return WeaponProperty(
            csv_dict['id'],
            csv_dict['name'],
            csv_dict['description']
        )


class WeaponHanded(Enum):
    H1 = 'One-handed'
    H2 = 'Two-handed'

# Q: Is this still needed?
#@dataclass
#class CharacterWeaponDamage:
#    weapon: Weapon
#    handed_damage: dict[WeaponHanded,DieMultiplier]
#
#    @override
#    def __str__(self) -> str:
#        h1_dmg = self.handed_damage.get(WeaponHanded.H1,None)
#        h2_dmg = self.handed_damage.get(WeaponHanded.H2,None)
#
#        return f"{self.weapon.name} / M "


@dataclass(frozen=True)
class Weapon(Gear):
    type_range: dict[WeaponType,Range]
    handed_damage: dict[WeaponHanded,MultiDie]
    properties: set[WeaponProperty]

    @override
    @property
    def is_equipable(self) -> bool:
        return True

    @override
    @property
    def is_bundled(self) -> bool:
        return False

    @property
    def attack_str(self) -> str:
        handed_dmg_str = "/".join([str(dm) for wh, dm in self.handed_damage.items()])
        range_type_str = "/".join([f"{t.value}({r.name})" for t,r in self.type_range.items()])
        props_str = ",".join([p.id for p in self.properties])

        return f"{self.name}: {handed_dmg_str} {range_type_str} {props_str or ''}"

    @override
    @staticmethod
    def from_csv(csv_dict: dict['str',str]) -> Weapon:
        id=csv_dict['id']
        name=csv_dict['name']
        
        try:
            cost = CoinAmount.parse(csv_dict['cost'])
            slots = int(csv_dict['slots'])

            type_range: dict[WeaponType,Range] = {}
            type_ranges_str = csv_dict['type_ranges']

            for type_range_str in type_ranges_str.split(';'):
                type_id, range_id = type_range_str.split(':')
                type_range[WeaponType[type_id]] = Range[range_id]
            
            handed_damage: dict[WeaponHanded,MultiDie] = {}
            handed_damages_str = csv_dict['handed_damages']

            for handed_damage_str in handed_damages_str.split(';'):
                handed_str, damage_str = handed_damage_str.split(':')
                handed_damage[WeaponHanded[handed_str]] = MultiDie.parse(damage_str)

            properties_str = csv_dict['properties']
            
            properties = {WEAPON_PROPERTIES[p] for p in properties_str.split(';') if p}
        except ValueError:
            raise ValueError(f'Could not parse "{id}" CSV entry')

        return Weapon(
            id=id,
            name=name,
            cost=cost,
            slots=slots,
            per_slot=1,
            free_to_carry=0,
            # FIXME: Why is this required when `Optional`
            description=None,
            type_range=type_range,
            handed_damage=handed_damage,
            properties=properties
        )


@dataclass(frozen=True)
class Armor(Gear):
    name: str

    @property
    @override
    def is_equipable(self) -> bool:
        return True


@dataclass(frozen=True)
class Talent:
    name: str


@dataclass(frozen=True)
class Class:
    name: str
    description: str
    languages: set[Language]
    weapons: set[WeaponType]
    armor: set[Armor]
    hp_dice: DieType
    talent: dict[int,Talent]


@dataclass(frozen=True)
class Level:
    number: int
    talent: bool
    level_up_at: int


class Ability(Enum):
    STR = 'Strength'
    DEX = 'Dexterity'
    CON = 'Constitution'
    INT = 'Intelligence'
    WIS = 'Wisdom'
    CHA = 'Charisma'


stat_mod = {
    1: -4,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
}

class Alignment(Enum):
    L = 'Lawful'
    N = 'Neutral'
    C = 'Chaotic'


@dataclass(frozen=True)
class Diety:
    name: str
    description: str
    alignment: Alignment


@dataclass(frozen=True)
class Background:
    name: str
    description: str


@dataclass(frozen=True)
class CharacterGear:
    gear: Gear
    equipt: bool

    def __post_init__(self):
        if self.equipt and not self.gear.is_equipable:
            raise ValueError(f'Gear "{gear.id}" is not equipable')

@dataclass
class Character:
    name: str
    abilities: dict[Ability,int]
    ancestry: Ancestry
    classes: set[Class]
    talents: list[Talent]
    alignment: Alignment
    background: Background
    diety: Diety
    level: int # TODO: Refactor to `Level`
    hp: int
    hp_max: int
    xp: int
    gear: list[CharacterGear]

    @property
    def STR(self) -> int:
        return self.abilities[Ability.STR]

    @property
    def DEX(self) -> int:
        return self.abilities[Ability.DEX]

    @property
    def CON(self) -> int:
        return self.abilities[Ability.CON]

    @property
    def INT(self) -> int:
        return self.abilities[Ability.INT]

    @property
    def WIS(self) -> int:
        return self.abilities[Ability.WIS]

    @property
    def CHA(self) -> int:
        return self.abilities[Ability.CHA]
    
    @property
    def ac(self) -> int:
        return 10 + stat_mod[self.DEX]
    
    @property
    def gear_slots(self) -> int:
        return self.STR if self.STR > 10 else 10
    
    @property
    def gear_slots_used(self) -> int:
        slots_used = 0
        gear_by_id = {cg.gear.id: cg.gear for cg in self.gear}

        count_per_gear: dict[str,int] = {}
        for cg in self.gear:
            try:
                count_per_gear[cg.gear.id] +=1
            except KeyError:
                count_per_gear[cg.gear.id] = 1

        for id, count in count_per_gear.items():
            gear = gear_by_id[id]
            if gear.slots > 1:
                slots_used += count * gear.slots
            else:
                div, mod = divmod(count, gear.per_slot)
                slots_used += div + (1 if mod else 0)

        return slots_used


    @property
    def weapons(self) -> list[Weapon]:
        #return [x for x in self.gear if isinstance(x, Weapon)]
        return [x.gear for x in self.gear if isinstance(x.gear, Weapon)]


    @staticmethod
    def gen(level: int) -> Character:
        if level > 0:
            raise ValueError("Only level 0 characters currently supported")
        
        return gen_0_level_char()



########################
# Rollers / Generators #
########################

def roll_ability_scores() -> dict[Ability,MultiDieRoll]:
    return {a: MultiDie(DieType.D6, 3).roll() for a in Ability}


def roll_character_meta(meta_type_key: str) -> dict:
    meta_type = CHARACTER_META[meta_type_key]
    die_type = DieType(meta_type['dice_type'])
    roll = die_type.roll().value

    # TODO: Improve excpetion handling for misconfigured files 
    for item in meta_type['items']:
        if roll in item['rolls']:
            return item

    raise ValueError(f'Could not find "{meta_type_key}" for roll of {roll}')
    

def roll_ancestry() -> Ancestry:
    roll_result = roll_character_meta('ancestry')

    return Ancestry(roll_result['name'])

def roll_character_name(ancestry: Ancestry) -> str:
    roll_val = DieType.D20.roll().value
    return CHARACTER_NAMES[(roll_val,ancestry.name)]


def roll_alignment() -> Alignment:
    roll_result = roll_character_meta('alignment')

    return Alignment[roll_result['code']]


def roll_diety(alignment: Alignment) -> Diety:
    roll_val = DieType.D10.roll().value

    return DIETIES[(roll_val, alignment)]


def roll_background() -> Background:
    roll_result = roll_character_meta('background')

    return Background(
        roll_result['name'],
        roll_result['description']
    )


def gen_base_character() -> Character:
    abilities = {
        ability: rolls.value for ability, rolls in roll_ability_scores().items()
    }

    ancestry = roll_ancestry()
    char_name = roll_character_name(ancestry)
    alignment = roll_alignment()
    diety = roll_diety(alignment)
    background = roll_background()

    return Character(
        name=char_name,
        abilities=abilities,
        ancestry=ancestry,
        classes=set(),
        alignment=alignment,
        background=background,
        diety=diety,
        talents=[],
        gear=[],
        level=0,
        hp_max=0,
        hp=0,
        xp=0,
    )


def roll_0_level_gear() -> list[GearQuantity]:
    gear_list = []
    num_of_rolls = DieType.D4.roll().value

    for _ in range(num_of_rolls):
        gear_roll = DieType.D12.roll().value
        gear = LEVEL_0_GEAR[gear_roll]
        gear_list.extend(gear)
    
    return gear_list


def gen_0_level_char() -> Character:
    character = gen_base_character()

    # Gear
    gear_qtys = roll_0_level_gear()
    char_gear_list: list[CharacterGear] = []

    for gear_qty in gear_qtys:
        for _ in range(gear_qty.quantity):
            char_gear_list.append(CharacterGear(gear_qty.gear, False))

    character.gear = char_gear_list

    # HP
    con_mod = stat_mod[character.CON]
    hp = con_mod if con_mod > 0 else 1
    character.hp = hp
    character.hp_max = hp

    return character


###############
# Load tables #
###############

CHARACTER_META = yaml.safe_load(
    open_binary('discord_lab.data', 'character-gen.yaml')
)

# TODO: Flesh out Ancestry and improve ex handling
CHARACTER_NAMES: dict[tuple[int,str],str] = {}
for row in csv.DictReader(
    open_text('discord_lab.data.tables', 'character-names.csv')
):
    roll = int(row.pop('d20'))
    for ancestry_name, char_name in row.items():
        CHARACTER_NAMES[(roll,ancestry_name)] = char_name


DIETIES: dict[tuple[int,Alignment],Diety] = {}
for row in csv.DictReader(
    open_text('discord_lab.data.tables', 'dieties.csv')
):
    alignment = Alignment[row['alignment']]

    roll_range_str = row['d10']
    roll_range_split = roll_range_str.split('-')
    if len(roll_range_split) == 1: 
        start = int(roll_range_split[0])
        end = start + 1
    elif len(roll_range_split) == 2:
        start = int(roll_range_split[0])
        end = int(roll_range_split[1]) + 1
    else:
        raise ValueError(f'"{roll_range_str}" is not a valid roll range')

    for x in range(start, end):
        diety = Diety(row['name'], row['description'], alignment)
        DIETIES[(x,alignment)] = diety


BASIC_GEAR: dict[str,Gear] = {
    x['id']:Gear.from_csv(x) for x in csv.DictReader(
        open_text('discord_lab.data.tables', 'basic-gear.csv')
    )
}

WEAPON_PROPERTIES: dict[str,WeaponProperty] = {
    x['id']:WeaponProperty.from_csv(x) for x in csv.DictReader(
        open_text('discord_lab.data.tables', 'weapon-properties.csv')
    )
}

WEAPON_GEAR: dict[str,Weapon] = {
    x['id']:Weapon.from_csv(x) for x in csv.DictReader(
        open_text('discord_lab.data.tables', 'weapons.csv')
    )
}

ALL_GEAR: dict[str,Gear] = BASIC_GEAR | WEAPON_GEAR

LEVEL_0_GEAR: dict[int,list[GearQuantity]] = {}
for row in csv.DictReader(
    open_text('discord_lab.data.tables', 'starting-gear-level-0.csv')
):
    gear_codes = row['gear_codes']
    gear_code_qtys = gear_codes.split(';')

    for gear_code_qty in gear_code_qtys:
        gear_code_qty_split = gear_code_qty.split(':')

        try:
            if len(gear_code_qty_split) in [1,2]:
                gear_code = gear_code_qty_split[0]
                gear = ALL_GEAR[gear_code]

                if len(gear_code_qty_split) == 2:
                    qty = int(gear_code_qty_split[1])
                else:
                    qty = 1

        except ValueError:
            raise ValueError(f'Could not parse gear_codes "{gear_codes}"')
            
        gear_quantity = GearQuantity(gear, qty)

        # TODO: Add parsing and out-of-range exception handling
        d12_roll = int(row['d12'])

        try:
            LEVEL_0_GEAR[d12_roll].append(gear_quantity)
        except KeyError:
            LEVEL_0_GEAR[d12_roll] = [gear_quantity]