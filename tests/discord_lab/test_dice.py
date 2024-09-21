import pytest

from discord_lab.dice import DieType

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

class Test