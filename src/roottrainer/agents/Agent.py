from game.Faction import Faction
from game.GameLogic import Action


class Agent:
    def __init__(self, faction: Faction):
        self.agent_type: str = "interface"
        self.faction: Faction = faction

    def choose_action(self, state: list, actions: list[Action]) -> Action | None:
        """
        Chooses an action to execute from all legal actions in the current `state`.

        :param actions: list of all legal actions
        :param state: the current state of the game
        :return: an action to be executed
        """
        pass
