from random import randint

from game.Faction import Faction
from game.GameLogic import Action, GameLogic
from roottrainer.agents.Agent import Agent


class RandomDecisionAgent(Agent):
    def __init__(self, faction: Faction):
        super().__init__(faction)
        self.agent_type: str = "random"

    def choose_action(self, state: list, actions: list[Action]) -> Action:
        return actions[randint(0, len(actions) - 1)]
