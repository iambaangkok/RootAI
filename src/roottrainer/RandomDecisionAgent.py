from random import randint

from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.Agent import Agent


class RandomDecisionAgent(Agent):
    def __init__(self, faction: Faction):
        super().__init__(faction)
        self.agent_type: str = "random"

    def choose_action(self, state: Game) -> Action:
        return state.get_actions()[randint(0, len(state.get_actions()) - 1)]