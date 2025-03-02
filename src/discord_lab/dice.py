from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
import re
from secrets import randbelow
from typing import override, ClassVar

from pyparsing import CaselessLiteral, Combine, Optional, ParseException, ParseResults, Suppress, ZeroOrMore, alphas, nums, Literal, Word


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
class MultiDieRoll:
    # FIXME: This should be calculated
    value: int
    details: list[DieRoll]


@dataclass(frozen=True)
class MultiDie:
    type: DieType
    multiplier: int = 1

    def __post_init__(self):
        if self.multiplier < 1:
            raise ValueError(f'Die multiplier {self.multiplier} is less than 1')

    def roll(self) -> MultiDieRoll:
        rolls = [self.type.roll() for x in range(self.multiplier)]
        total = sum(r.value for r in rolls)

        return MultiDieRoll(total, rolls)


    @staticmethod
    def parse(multi_die_expr: str) -> MultiDie:

        # regex for parsing "3D6" style die side and multiplier strings
        match = re.match(r'^(\d+)?[dD](\d+)$', multi_die_expr.strip())

        if not match:
            raise DieParseException(f'"{multi_die_expr}" is invalid. Should be of the form D20 or 3D6.')
        
        mult = int(match.group(1) or "1")
        parsed_sides = int(match.group(2))
        
        try:
            die_type = DieType(parsed_sides)
        except ValueError:
            valid_sides = ', '.join([str(x.value) for x in DieType])
            raise DieParseException(f'{parsed_sides}-sided dice not supported. Must be one of: {valid_sides}')

        return MultiDie(die_type, mult)

    @override
    def __str__(self) -> str:
        _str = self.type.name
        if self.multiplier > 1:
            _str = f"{self.multiplier}{_str}"

        return _str


class Operation(Enum):
    ADD = '+'
    SUB = '-'
    NO_OP = None

    def apply(self, val_1: int, val_2: int) -> int:
        match self:
            case Operation.ADD:
                return val_1 + val_2
            case Operation.SUB:
                return val_1 - val_2
            case Operation.NO_OP:
                return val_1
            case _:
                raise ValueError(f"{self.name} operation not supported")


@dataclass
class TermRoll:
    # FIXME: This should be calculated
    value: int
    details: int|MultiDieRoll


@dataclass
class LabeledTerm:
    term: int|MultiDie
    label: str|None = None

    def roll(self) -> TermRoll:
        total:int = 0

        match self.term:
            case int():
                return TermRoll(self.term, self.term)
            case MultiDie():
                multi_die_roll = self.term.roll()
                return TermRoll(multi_die_roll.value, multi_die_roll)
            case _:
                raise ValueError(f"Term type {type(self.term)} not supported")
            

    @override
    def __str__(self) -> str:
        _str = str(self.term)
        if self.label:
            _str += f" ({self.label})"

        return _str


@dataclass
class TermOperation:
    operation: Operation
    labeled_term: LabeledTerm

    @override
    def __str__(self) -> str:
        _str = str(self.labeled_term)
        if self.operation.value:
            _str = f"{self.operation.value} {_str}"

        return _str


@dataclass
class TermOperationResult:
    value: int
    term_op: TermOperation


@dataclass
class IntTermOperationResult(TermOperationResult):
    pass

@dataclass
class MultiDieTermOperationResult(TermOperationResult):
    rolls: MultiDieRoll


@dataclass
class DieExprRoll:
    # FIXME: This should be calculated
    value: int
    results: list[TermOperationResult]


class DieExprParser:

    def __init__(self):
        d4 = Literal('4')
        d6 = Literal('6')
        d8 = Literal('8')
        d10 = Literal('10')
        d12 = Literal('12')
        d20 = Literal('20')
        d100 = Literal('100')

        add_op = Literal('+')
        sub_op = Literal('-')
        op = (add_op | sub_op).set_parse_action(lambda tokens: Operation(tokens[0]))

        l_paren = Suppress("(")
        r_paren = Suppress(")")
        label = Word(alphas + ' _-:', max=20)
        label_wrap = l_paren + label + r_paren

        integer = Word(nums).set_parse_action(lambda tokens: int(tokens[0]))
        multiplier = Word(nums)
        multi_die_sep = CaselessLiteral('D')
        die_type = d100 | d20 | d12 | d10 | d8 | d6 | d4
        roll_mult = Combine(Optional(multiplier) + multi_die_sep + die_type).set_parse_action(lambda tokens: MultiDie.parse(tokens[0]))

        term = roll_mult | integer
        labeled_term = (term + Optional(label_wrap)).set_parse_action(self.tokens_to_term)
        term_op = (op + labeled_term).set_parse_action(lambda tokens: TermOperation(tokens[0], tokens[1]))

        self.expr = (labeled_term + ZeroOrMore(term_op)).set_parse_action(lambda tokens: DieExpr(tokens[0], tokens[1:]))

    @staticmethod
    def tokens_to_term(tokens: ParseResults) -> LabeledTerm:
        term = LabeledTerm(tokens[0])
        try:
            term.label = tokens[1]
        except IndexError:
            pass

        return term

    def parse(self, expr_str: str) -> DieExpr:
        return self.expr.parse_string(expr_str)[0]

die_expr_parser = DieExprParser()


@dataclass
class DieExpr:
    # TODO: Convert this over to just a single list?
    first_term: LabeledTerm
    term_ops: list[TermOperation] = field(default_factory=list)
    parser: ClassVar[DieExprParser] = die_expr_parser

    @classmethod
    def parse(cls, expr_str: str) -> DieExpr:
        try:
            return cls.parser.parse(expr_str)
        except ParseException as pe:
            raise DieParseException(f"Invalid die roll expression `{expr_str}`") from pe

    def roll(self) -> DieExprRoll:
        first_term = self.first_term
        first_term_term = first_term.term
        first_term_result: TermOperationResult
        match first_term_term:
            case int():
                first_term_result = IntTermOperationResult(first_term_term, TermOperation(Operation.NO_OP, first_term))
            case MultiDie():
                rolls = first_term_term.roll()
                first_term_result = MultiDieTermOperationResult(rolls.value, TermOperation(Operation.NO_OP, first_term), rolls)

        total = first_term_result.value
        term_op_results = [first_term_result]

        for term_op in self.term_ops:
            term_op_term = term_op.labeled_term.term
            term_op_result: TermOperationResult
            match term_op_term:
                case int():
                    term_op_result = IntTermOperationResult(term_op_term, TermOperation(term_op.operation, term_op.labeled_term))
                case MultiDie():
                    rolls = term_op_term.roll()
                    term_op_result = MultiDieTermOperationResult(rolls.value, TermOperation(term_op.operation, term_op.labeled_term), rolls)

            total = term_op.operation.apply(total, term_op_result.value)
            term_op_results.append(term_op_result)

        return DieExprRoll(total, term_op_results)

    @override
    def __str__(self) -> str:
        _str = str(self.first_term)
        for term_op in self.term_ops:
            _str += f" {term_op}"

        return _str

    
class DieExprMultiRollType(Enum):
    BEST = 'Best / Advantage'
    WORST = 'Worst / Disadvantage'

    def resolve(self, roll_1: DieExprRoll, roll_2: DieExprRoll) -> DieExprMultiRollResult:
        result_roll: DieExprRoll

        if self == DieExprMultiRollType.ADVANTAGE:
            if roll_1.value > roll_2.value:
                result_roll = roll_1
            else:
                result_roll = roll_2
        else:
            if roll_1.value < roll_2.value:
                result_roll = roll_1
            else:
                result_roll = roll_2
            
        return DieExprMultiRollResult(self, (roll_1, roll_2), result_roll)
            

@dataclass
class DieExprMultiRollResult:
    type: DieExprMultiRollType
    rolls: tuple[DieExprRoll, DieExprRoll]
    resolved_roll: DieExprRoll
     

@dataclass
class DieExprMultiRoll:
    die_expr: DieExpr
    type: DieExprMultiRollType

    def roll(self) -> DieExprMultiRollResult:
        roll_1 = self.die_expr.roll()
        roll_2 = self.die_expr.roll()

        return self.type.resolve(roll_1, roll_2)
