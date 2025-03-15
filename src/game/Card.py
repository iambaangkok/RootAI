from enum import StrEnum

from game.Item import Item
from game.Suit import Suit


class CardName(StrEnum):
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


class CardPhase(StrEnum):
    IMMEDIATE = "IMMEDIATE"
    BATTLE = "BATTLE"
    BIRDSONG = "BIRDSONG"
    DAYLIGHT = "DAYLIGHT"
    EVENING = "EVENING"


class Card:
    DOMINANCE_CARD_NAMES = [CardName.DOMINANCE_BIRD, CardName.DOMINANCE_FOX, CardName.DOMINANCE_RABBIT,
                            CardName.DOMINANCE_MOUSE]

    def __init__(self, card_id: int, name: CardName | str, suit: Suit, phase: CardPhase,
                 craft_requirement: {Suit: int} = None,
                 reward_vp: int = 0, reward_item: Item | None = None):
        self.card_id: int = card_id
        self.name: CardName | str = name
        self.suit: Suit = suit
        self.craft_requirement: {Suit: int} = craft_requirement
        self.reward_vp: int = reward_vp
        self.reward_item: Item = reward_item
        self.phase: CardPhase = phase


def build_card(card_id: int) -> Card:
    match card_id:
        case 0 | 1:
            return Card(card_id, CardName.AMBUSH, Suit.BIRD, CardPhase.BATTLE)
        case 2:
            return Card(card_id, CardName.BIRDY_HANDLE, Suit.BIRD, CardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1,
                        Item.BAG)
        case 3 | 4:
            return Card(card_id, CardName.ARMORERS, Suit.BIRD, CardPhase.BATTLE, {Suit.FOX: 1})
        case 5:
            return Card(card_id, CardName.WOODLAND_RUNNERS, Suit.BIRD, CardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS)
        case 6:
            return Card(card_id, CardName.ARMS_TRADER, Suit.BIRD, CardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE)
        case 7:
            return Card(card_id, CardName.CROSSBOW, Suit.BIRD, CardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW)
        case 8 | 9:
            return Card(card_id, CardName.SAPPERS, Suit.BIRD, CardPhase.BATTLE, {Suit.MOUSE: 1})
        case 10 | 11:
            return Card(card_id, CardName.BRUTAL_TACTICS, Suit.BIRD, CardPhase.BATTLE, {Suit.FOX: 2})
        case 12:
            return Card(card_id, CardName.ROYAL_CLAIM, Suit.BIRD, CardPhase.BIRDSONG, {Suit.BIRD: 4})
        case 13:
            return Card(card_id, CardName.AMBUSH, Suit.FOX, CardPhase.BATTLE)
        case 14:
            return Card(card_id, CardName.GENTLY_USED_KNAPSACK, Suit.FOX, CardPhase.IMMEDIATE, {Suit.MOUSE: 1},
                        1, Item.BAG)
        case 15:
            return Card(card_id, CardName.ROOT_TEA, Suit.FOX, CardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG)
        case 16:
            return Card(card_id, CardName.TRAVEL_GEAR, Suit.FOX, CardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS)
        case 17:
            return Card(card_id, CardName.PROTECTION_RACKET, Suit.FOX, CardPhase.IMMEDIATE, {Suit.RABBIT: 2},
                        3, Item.COIN)
        case 18:
            return Card(card_id, CardName.FOXFOLK_STEEL, Suit.FOX, CardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE)
        case 19:
            return Card(card_id, CardName.ANVIL, Suit.FOX, CardPhase.IMMEDIATE, {Suit.FOX: 1}, 2, Item.HAMMER)
        case 20 | 21:
            return Card(card_id, CardName.STAND_AND_DELIVER, Suit.FOX, CardPhase.BIRDSONG, {Suit.MOUSE: 3})
        case 22 | 23 | 24:
            return Card(card_id, CardName.TAX_COLLECTOR, Suit.FOX, CardPhase.DAYLIGHT,
                        {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1})
        case 25:
            return Card(card_id, CardName.FAVOR_OF_THE_FOXES, Suit.FOX, CardPhase.IMMEDIATE, {Suit.FOX: 3})
        case 26:
            return Card(card_id, CardName.AMBUSH, Suit.RABBIT, CardPhase.BATTLE)
        case 27:
            return Card(card_id, CardName.SMUGGLERS_TRAIL, Suit.RABBIT, CardPhase.IMMEDIATE, {Suit.MOUSE: 1},
                        1, Item.BAG)
        case 28:
            return Card(card_id, CardName.ROOT_TEA, Suit.RABBIT, CardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG)
        case 29:
            return Card(card_id, CardName.A_VISIT_TO_FRIENDS, Suit.RABBIT, CardPhase.IMMEDIATE,
                        {Suit.RABBIT: 1}, 1, Item.BOOTS)
        case 30:
            return Card(card_id, CardName.BAKE_SALE, Suit.RABBIT, CardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3,
                        Item.COIN)
        case 31 | 32:
            return Card(card_id, CardName.COMMAND_WARREN, Suit.RABBIT, CardPhase.DAYLIGHT, {Suit.RABBIT: 2})
        case 33 | 34:
            return Card(card_id, CardName.BETTER_BURROW_BANK, Suit.RABBIT, CardPhase.BIRDSONG,
                        {Suit.RABBIT: 2})
        case 35 | 36:
            return Card(card_id, CardName.COBBLER, Suit.RABBIT, CardPhase.EVENING, {Suit.RABBIT: 2})
        case 37:
            return Card(card_id, CardName.FAVOR_OF_THE_RABBITS, Suit.RABBIT, CardPhase.IMMEDIATE,
                        {Suit.RABBIT: 3})
        case 38:
            return Card(card_id, CardName.AMBUSH, Suit.MOUSE, CardPhase.BATTLE)
        case 39:
            return Card(card_id, CardName.MOUSE_IN_A_SACK, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1,
                        Item.BAG)
        case 40:
            return Card(card_id, CardName.ROOT_TEA, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG)
        case 41:
            return Card(card_id, CardName.TRAVEL_GEAR, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS)
        case 42:
            return Card(card_id, CardName.INVESTMENTS, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3,
                        Item.COIN)
        case 43:
            return Card(card_id, CardName.SWORD, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE)
        case 44:
            return Card(card_id, CardName.CROSSBOW, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW)
        case 45 | 46:
            return Card(card_id, CardName.SCOUTING_PARTY, Suit.MOUSE, CardPhase.BATTLE, {Suit.MOUSE: 2})
        case 47 | 48:
            return Card(card_id, CardName.CODEBREAKERS, Suit.MOUSE, CardPhase.DAYLIGHT, {Suit.MOUSE: 1})
        case 49:
            return Card(card_id, CardName.FAVOR_OF_THE_MICE, Suit.MOUSE, CardPhase.IMMEDIATE, {Suit.MOUSE: 3})
        case 50:
            return Card(card_id, CardName.DOMINANCE_RABBIT, Suit.RABBIT, CardPhase.DAYLIGHT)
        case 51:
            return Card(card_id, CardName.DOMINANCE_MOUSE, Suit.MOUSE, CardPhase.DAYLIGHT)
        case 52:
            return Card(card_id, CardName.DOMINANCE_BIRD, Suit.BIRD, CardPhase.DAYLIGHT)
        case 53:
            return Card(card_id, CardName.DOMINANCE_FOX, Suit.FOX, CardPhase.DAYLIGHT)
