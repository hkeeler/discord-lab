from typing import cast
import pytest

from discord_lab.dice import DieExpr, DieExprRoll, DieParseException, IntTermOperationResult, MultiDie, DieType, MultiDieTermOperationResult, Operation, LabeledTerm, TermOperation, TermOperationResult

class TestDieType:

    def test_roll_d4(self):
        die_roll = DieType.D4.roll()

        assert die_roll.type == DieType.D4
        assert 1 <= die_roll.value <= 4


    def test_roll_d6(self):
        die_roll = DieType.D6.roll()

        assert die_roll.type == DieType.D6
        assert 1 <= die_roll.value <= 6


    def test_roll_d8(self):
        die_roll = DieType.D8.roll()

        assert die_roll.type == DieType.D8
        assert 1 <= die_roll.value <= 8


    def test_roll_d10(self):
        die_roll = DieType.D10.roll()

        assert die_roll.type == DieType.D10
        assert 1 <= die_roll.value <= 10


    def test_roll_d12(self):
        die_roll = DieType.D12.roll()

        assert die_roll.type == DieType.D12
        assert 1 <= die_roll.value <= 12


    def test_roll_d20(self):
        die_roll = DieType.D20.roll()

        assert die_roll.type == DieType.D20
        assert 1 <= die_roll.value <= 20


    def test_roll_d100(self):
        die_roll = DieType.D100.roll()

        assert die_roll.type == DieType.D100
        assert 1 <= die_roll.value <= 100

class TestTerm:
     
     def test_str_int_no_label(self):
         term = LabeledTerm(1)

         assert str(term) == '1'


     def test_str_int_with_label(self):
         term = LabeledTerm(2, 'Test int')

         assert str(term) == '2 (Test int)'


     def test_str_die_mult_no_label(self):
         term = LabeledTerm(MultiDie(DieType.D6, 3))

         assert str(term) == '3D6'


     def test_str_die_mult_with_label(self):
         term = LabeledTerm(MultiDie(DieType.D100), 'Test Die Mult')

         assert str(term) == 'D100 (Test Die Mult)'


class TestTermOperator:

    def test_str_add_int(self):
        term_op = TermOperation(Operation.ADD, LabeledTerm(2))

        assert str(term_op) == '+ 2'

    def test_str_add_die_mult(self):
        term_op = TermOperation(Operation.ADD, LabeledTerm(MultiDie(DieType.D6, 3)))

        assert str(term_op) == '+ 3D6'

    def test_str_sub_int(self):
        term_op = TermOperation(Operation.SUB, LabeledTerm(5))

        assert str(term_op) == '- 5'

    def test_str_sub_die_mult(self):
        term_op = TermOperation(Operation.SUB, LabeledTerm(MultiDie(DieType.D4, 6)))

        assert str(term_op) == '- 6D4'


class TestDieExpr:

    def test_term_only_int(self):
        term = LabeledTerm(3)
        expr = DieExpr(term)
        expr_str = '3'

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert roll == DieExprRoll(3, [IntTermOperationResult(3, TermOperation(Operation.NO_OP, LabeledTerm(3)))])


    def test_term_only_die_mult(self):
        term = LabeledTerm(MultiDie(DieType.D20, 2))
        expr = DieExpr(term)
        expr_str = '2D20'

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert len(roll.results) == 1
        assert 2 <= roll.value <= 40
        assert roll.results[0].term_op.operation == Operation.NO_OP
        assert roll.results[0].term_op.labeled_term.term == MultiDie(DieType.D20, 2)

        roll_results = roll.results[0]
        assert isinstance(roll_results, MultiDieTermOperationResult)


    def test_str_single_op_add_int(self):
        term_1 = LabeledTerm(1)
        term_2 = LabeledTerm(2)
        op = Operation.ADD

        expr = DieExpr(term_1, [TermOperation(op, term_2)])
        expr_str = '1 + 2'

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert roll == DieExprRoll(3, [
                IntTermOperationResult(1, TermOperation(Operation.NO_OP, LabeledTerm(1))),
                IntTermOperationResult(2, TermOperation(Operation.ADD, LabeledTerm(2)))
            ]
        )


    def test_str_single_op_sub_die_mult(self):
        term_1 = LabeledTerm(MultiDie(DieType.D20))
        term_2 = LabeledTerm(2)
        op = Operation.SUB

        expr = DieExpr(term_1, [TermOperation(op, term_2)])
        expr_str = 'D20 - 2'

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert len(roll.results) == 2


    def test_str_single_op_sub_die_mult_with_labels(self):
        term_1 = LabeledTerm(MultiDie(DieType.D20))
        term_2 = LabeledTerm(2, "STR")
        op = Operation.SUB

        expr = DieExpr(term_1, [TermOperation(op, term_2)])
        expr_str = 'D20 - 2 (STR)'

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert len(roll.results) == 2       


    def test_str_single_op_complex(self):
        term_1 = LabeledTerm(MultiDie(DieType.D20))
        term_op_1 = TermOperation(Operation.SUB, LabeledTerm(2, "INT"))
        term_op_2 = TermOperation(Operation.ADD, LabeledTerm(MultiDie(DieType.D4), "Acid"))
        term_op_3 = TermOperation(Operation.ADD, LabeledTerm(MultiDie(DieType.D6, 2), "Fire"))

        expr = DieExpr(term_1, [term_op_1, term_op_2, term_op_3])
        expr_str = "D20 - 2 (INT) + D4 (Acid) + 2D6 (Fire)"

        assert str(expr) == expr_str
        assert DieExpr.parse(expr_str) == expr

        roll = expr.roll()
        assert len(roll.results) == 4


    def test_str_raise_parse_error(self):
        expr_str = "WTF"

        with pytest.raises(DieParseException) as dpe:
            DieExpr.parse(expr_str)

        assert str(dpe.value) == f'Invalid die roll expression `{expr_str}`'
