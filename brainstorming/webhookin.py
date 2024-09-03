#!/usr/bin/env python3

from pprint import pprint
import requests as r

from discord_lab.character import *

ascii_card_slim = """
┌──────────────────────────────────────────────────────┐
│ Dorn                               Hans / @saskwotch │
├──────────────┬─────────────────────────┬─────────────┤
"""

ascii_card = """
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Dorn                                                               Hans / @saskwotch │
├──────────────┬─────────────────────────┬─────────────────────────────────────────────┤
│ STR: 12 / +1 │ Ancestry: Elf           │ Talents / Spells                            │
│ DEX: 10 / +0 │ Class: Fighter          ├─────────────────────────────────────────────┤
│ CON: 10 / +0 │ Title: Bandit           │ 1. +1 to melee attacks                      │
│ INT: 12 / +1 │ Alignment: Lawful       │ 2. +2 Constitution                          │
│ WIS: 15 / +2 │ Background: Urchin      │                                             │
│ CHA:  7 / -2 │ Deity: St. Terragnis    │                                             │
├──────────────┼─────────────────────────┤                                             │
│ HP: 5 / 10   │ Level: 3                │                                             │
│ AC: 14       │ XP: 12                  │                                             │
├──────────────┴─────────────────────────┼─────────────────────────────────────────────┤
│ Attacks / Damage                       │ Gear (7/12)         GP: 20   SP: 8   CP: 20 │
├────────────────────────────────────────┼─────────────────────────────────────────────┤
│ 1. Longsword: 1D8+1 (STR) /            │ 1. Rope (1)           7. Dagger (1)         │
│ 2. Dagger: 1D4                         │ 2. Longsword (1)                            │
│                                        │ 3. Shield (1)                               │
│                                        │ 4. Leather armor (1)                        │
│                                        │ 5. Torch (1) x2                             │
│                                        │ 6. Rations (1-3) x3                         │
└────────────────────────────────────────┴─────────────────────────────────────────────┘
"""


url = 'https://discord.com/api/webhooks/1278930481894789246/fYDqIHFsRMY00NZUvQMDErWrO53k6mqnesywdjjnPMsNWab5URuhSZJrCmWnlkrv9-dk'


char = gen_0_level_char()
abilities_md = '\n'.join([f'{a.name}: {v:>2} / {stat_mod[v]:>2}' for a,v in char.abilities.items()])
gear_md = '\n'.join([f'{idx+1}. {cg.gear}' for idx, cg in enumerate(char.gear)])

body = {
    #'content': f'```{ascii_card_slim}```',
    #'content': '@saskwotch',
    'embeds': [
        {
            "title": f"{char.name}",
            #"description": f'```{ascii_card}```',
            #"description": "@saskwotch",
            "footer": {
                "text":"Hans / @saskwotch"
            },
            "color": 16777215,
            #"thumbnail": {
            #    "url": "https://www.thearcanelibrary.com/cdn/shop/articles/Torchie_1600x.png"
            #},
            "fields": [
                { "name": "`Abilities`", "value": f'```{abilities_md}```', "inline": "true"},
                { "name": "`Status`", "value": f"```Level: {char.level}\nXP: {char.xp}\n\nHP: {char.hp} / {char.hp_max}\nAC: {char.ac}```", "inline": "true"},
                { "name": "`Character`", "value": f"```Ancestry: {char.ancestry.name}\nClass: {char.classes}\nTitle: ???\nAlignment: {char.alignment.value}\nBackground: {char.background.name}\nDeity: <Diety Name>```", "inline": "true"},
                { "name": "`Attacks / Damage`", "value": "```1. <Weapon 1>\n2. <Weapon 2>```"},
                { "name": "`Talents / Spells`", "value": "```1. <Talent 1>\n2. <Talent 2>```"},
                #{ "name": f"`Gear (?/{char.gear_slots})`", "value": "```1. Rope (1)\n2. Longsword (1)\n3. Shield (1)\n4. Leather armor (1)\n5. Torch (1) x2\n6. Rations (1-3) x3```"},
                { "name": f"`Gear (?/{char.gear_slots})`", "value": f"```{gear_md}```"},
            ]
        }
    ]
}

resp = r.post(url, json=body, params={'wait':'true'})
pprint(resp.json())

