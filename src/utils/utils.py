from __future__ import annotations

import ntpath
import os

from game.Building import Building
from game.Card import Card
from game.Faction import Faction
from game.Token import Token
from game.Warrior import Warrior


def perform(function: any, *args):
    return lambda: function(*args)


def get_filename_from_path(path: str, extension: bool = False) -> str:
    head, tail = ntpath.split(path)
    if extension:
        return tail or ntpath.basename(head)
    return os.path.splitext(tail)[0] or os.path.splitext(ntpath.basename(head))[0]


def get_card(card_id: int, cards: list[Card]):
    for card in cards:
        if card.card_id == card_id:
            target: Card = card
            return target
    return None


FACTION_TO_WARRIOR: {Faction: Warrior} = {
    Faction.MARQUISE: Warrior.MARQUISE,
    Faction.EYRIE: Warrior.EYRIE
}

FACTION_TO_TOKENS: {Faction: list[Token]} = {
    Faction.MARQUISE: [Token.WOOD, Token.CASTLE],
    Faction.EYRIE: []
}

FACTION_TO_BUILDINGS: {Faction: list[Building]} = {
    Faction.MARQUISE: [Building.SAWMILL, Building.RECRUITER, Building.WORKSHOP],
    Faction.EYRIE: [Building.ROOST]
}

WARRIOR_TO_FACTION: {Warrior: Faction} = {
    Faction.MARQUISE: Warrior.MARQUISE,
    Faction.EYRIE: Warrior.EYRIE
}


def faction_to_warrior(faction: Faction) -> Warrior:
    return FACTION_TO_WARRIOR[faction]


def faction_to_tokens(faction: Faction) -> list[Token]:
    return FACTION_TO_TOKENS[faction]


def faction_to_buildings(faction: Faction) -> list[Building]:
    return FACTION_TO_BUILDINGS[faction]
