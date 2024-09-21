import operator
from typing import Callable

from pyparsing import CaselessLiteral, Combine, Group, Optional, ParseResults, Suppress, ZeroOrMore, alphas, nums, Literal, Word

from discord_lab.dice import DieMultiplier, DieRoll

def term_to_int(term: int|tuple[int,list[DieRoll]]) -> int:
    match term:
        case int():
            term_val = term
        case tuple():
            term_val = term[0]
        case _:
            raise ValueError(f"{term} could not be processed")
        
    return term_val


def calc_expr(tokens: ParseResults) -> tuple[int,ParseResults]:
    total:int = 0

    for idx, token in enumerate(tokens):

        # First item in list does not have an operation associated with it
        if idx == 0:
            total = term_to_int(token[0])
        else:
            op_symbol = token[0]
            op_fn = operations[op_symbol]
            term_val = term_to_int(token[1][0])
            total = op_fn(total, term_val)

    return total, tokens


operations: dict[str,Callable[[int,int],int]] = {
    '+': operator.add,
    '-': operator.sub
}

d4 = Literal('4')
d6 = Literal('6')
d8 = Literal('8')
d10 = Literal('10')
d12 = Literal('12')
d20 = Literal('20')
d100 = Literal('100')

add_op = Literal('+')
sub_op = Literal('-')
op = add_op | sub_op

l_paren = Suppress("(")
r_paren = Suppress(")")
label = Word(alphas + ' :', max=20)
label_wrap = l_paren + label + r_paren

integer = Word(nums).set_parse_action(lambda tokens: int(tokens[0]))
mult = Word(nums)
die_mult_sep = CaselessLiteral('D')
die_type = d100 | d20 | d12 | d10 | d8 | d6 | d4
roll_mult = Combine(Optional(mult) + die_mult_sep + die_type).set_parse_action(lambda tokens: DieMultiplier.parse(tokens[0]).roll())

term = roll_mult | integer

commented_term = Group(term + Optional(label_wrap))

expr = (commented_term + ZeroOrMore(Group(op + commented_term))).set_parse_action(calc_expr)

roll_mult.run_tests(\
    """
    # Test all die types
    D4
    D6
    D8
    D10
    D12
    D20
    D100

    # Invalid die type
    D99

    # D6, no mult, lower
    d6
                    
    # D6, no mult
    D6

    # D6, 1 mult, lower
    1d6

    # D6, 1 mult
    1D6

    # D6, 2 mult
    2D6

    # Invalid
    # TODO: Check this in parse so it does not fail 
    0D10
    """)

term.run_tests(\
    """
    # Just integer
    1

    # Negative integer
    -1

    # Just die
    D6
    
    # Die w/ mult
    3D6
    """)

commented_term.run_tests(\
    """
    1
    D6
    1(abc)
    D6(def)
    42 (ghi)
    D100 (jkl)
    99 (mno mno mno)
    3D6 (pqr pqr pqr)
    101  (stu)
    2D10  (vwxyz)

    # label too long
    # FIXME: Can we get a better error message?
    D6 (abcdefghijklmnopqrstuvwxyz)
    """)

expr.run_tests(\
    """\
    6
    6 (abc)
    D6
    D6 (def)
    3D6
    3D6 (ghi)
    3D6 -1
    3D6 - 1
    D8 (Sword) - 1 (STR) + D4
    """)
