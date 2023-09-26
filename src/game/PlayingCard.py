from enum import StrEnum

from src.game.Item import Item
from src.game.Suit import Suit


class PlayingCardName(StrEnum):
    AMBUSH = "Ambush"

    BIRDY_HANDLE = "Birdy Handle"
    ARMORERS = "Armorers"
    WOODLAND_RUNNERS = "Woodland Runners"
    ARMS_TRADER = "Arms Trader"
    CROSSBOW = "Crossbow"
    SAPPERS = "Sappers"
    BRUTAL_TACTICS = "Brutal Tactics"
    ROYAL_CLAIM = "Royal Claim"

    GENTLY_USED_KNAPSACK = "Gently Used Knapsack"
    ROOT_TEA = "Root Tea"
    TRAVEL_GEAR = "Travel Gear"
    PROTECTION_RACKET = "Protection Racket"
    FOXFOLK_STEEL = "Foxfolk Steel"
    ANVIL = "Anvil"
    STAND_AND_DELIVER = "Stand and Deliver"
    TAX_COLLECTOR = "Tax Collector"
    FAVOR_OF_THE_FOXES = "Favor of the Foxes"

    SMUGGLERS_TRAIL = "Smuggler's Trail"
    A_VISIT_TO_FRIENDS = "A Visit to Friends"
    BAKE_SALE = "Bake Sale"
    COMMAND_WARREN = "Command Warren"
    BETTER_BURROW_BANK = "Better Burrow Bank"
    COBBLER = "Cobbler"
    FAVOR_OF_THE_RABBITS = "Favor of the Rabbits"

    MOUSE_IN_A_SACK = "Mouse-in-a-Sack"
    INVESTMENTS = "Investments"
    SWORD = "Sword"
    SCOUTING_PARTY = "Scouting Party"
    CODEBREAKERS = "Codebreakers"
    FAVOR_OF_THE_MICE = "Favor of the Mice"

    DOMINANCE_BIRD = "Dominance (Bird)"
    DOMINANCE_FOX = "Dominance (Fox)"
    DOMINANCE_RABBIT = "Dominance (Rabbit)"
    DOMINANCE_MOUSE = "Dominance (Mouse)"

    ROYAL_VIZIER = "Royal Vizier"


class PlayingCardPhase(StrEnum):
    IMMEDIATE = "IMMEDIATE"
    BATTLE = "BATTLE"
    BIRDSONG = "BIRDSONG"
    DAYLIGHT = "DAYLIGHT"
    EVENING = "EVENING"


class PlayingCard:
    DOMINANCE_CARD_NAMES = [PlayingCardName.DOMINANCE_BIRD, PlayingCardName.DOMINANCE_FOX, PlayingCardName.DOMINANCE_RABBIT, PlayingCardName.DOMINANCE_MOUSE]

    def __init__(self, card_id: int, name: PlayingCardName | str, suit: Suit, phase: PlayingCardPhase, craft_requirement: {Suit: int} = None,
                 reward_vp: int = 0, reward_item: Item | None = None):
        self.card_id: int = card_id
        self.name: PlayingCardName | str = name
        self.suit: Suit = suit
        self.craft_requirement: {Suit: int} = craft_requirement
        self.reward_vp: int = reward_vp
        self.reward_item: Item = reward_item
        self.phase: PlayingCardPhase = phase
