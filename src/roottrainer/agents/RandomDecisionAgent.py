from random import randint

from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.agents.Agent import Agent


class RandomDecisionAgent(Agent):
    def __init__(self, faction: Faction):
        super().__init__(faction)
        self.agent_type: str = "random"

    def choose_action(self, state: list, actions: list[Action]) -> Action:
        return actions[randint(0, len(actions) - 1)]
