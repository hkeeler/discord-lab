from discord_lab.character import Character


class TestCharacter:

    def test_gen_level_0(self):
        for _ in range(1000):
            character = Character.gen(level=0)

            assert character.level == 0
            assert character.xp == 0
            assert len(character.abilities) == 6
            assert character.name
            assert character.ancestry
            assert character.background
            assert character.alignment
            assert character.diety
            assert character.hp_max > 0
            assert character.hp == character.hp_max
            assert character.ac > 0
            assert len(character.gear) > 0
            assert len(character.classes) == 0
            assert len(character.talents) == 0
