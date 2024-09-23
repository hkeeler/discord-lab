from discord_lab.dice import DieExpr, DieExprRoll, DieRoll, DieType, IntTermOperationResult, LabeledTerm, MultiDie, MultiDieRoll, MultiDieTermOperationResult, Operation, TermOperation
from discord_lab.interactions.lambda import die_roll_to_md, render_expr_roll, render_multidie_roll


class TestDieRollToMd:

    def test_single_die(self):
        md = die_roll_to_md(DieRoll(17, DieType.D20))
        
        assert md.startswith('<:d20_17:')


    def test_d100_die(self):
        md = die_roll_to_md(DieRoll(42, DieType.D100))
        
        # WARN: This is brittle. Updating die emoji images will break this.
        assert md == '<:d10_40:1282474836551139380><:d10_2:1282232090938708035>'


    def test_render_multidie_roll_single(self):
        md = render_multidie_roll(MultiDieRoll(17, [DieRoll(17, DieType.D20)]))

        # WARN: This is brittle. Updating die emoji images will break this.
        assert md == '17 (<:d20_17:1282233108376059914>)'


    def test_render_multidie_roll_multi(self):
        md = render_multidie_roll(
            MultiDieRoll(
                15,
                [
                    DieRoll(5, DieType.D6),
                    DieRoll(4, DieType.D6),
                    DieRoll(6, DieType.D6),
                ]
            )
        )

        # WARN: This is brittle. Updating die emoji images will break this.
        assert md == '15 (<:d6_5:1282212308982169653> <:d6_4:1282212289310621717> <:d6_6:1282212638297817198>)'


    def test_render_expr_roll(self):
        md = render_expr_roll(
            DieExprRoll(11,[
                    MultiDieTermOperationResult(9, TermOperation(Operation.NO_OP, LabeledTerm(MultiDie(DieType.D6, 2), "Sword")), MultiDieRoll(9, [DieRoll(5, DieType.D6), DieRoll(4, DieType.D6)])),
                    IntTermOperationResult(2, TermOperation(Operation.SUB, LabeledTerm(2, "STR"))),
                    MultiDieTermOperationResult(4, TermOperation(Operation.ADD, LabeledTerm(MultiDie(DieType.D4, 1), "Acid")), MultiDieRoll(4, [DieRoll(4, DieType.D4)]))
                ]
            )
        )

        assert md == '9 (<:d6_5:1282212308982169653> <:d6_4:1282212289310621717>) (Sword) - 2 (STR) + 4 (<:d4_4:1282216878072135720>) (Acid) = 11'
