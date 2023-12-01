from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.Agent import Agent


class MCTSAgent(Agent):
    def __init__(self, faction: Faction):
        super().__init__(faction)
        self.agent_type: str = "mcts"

    def choose_action(self, state: Game, actions: list[Action]) -> Action:
        return self.choose_best_actions(state, actions)

    def choose_best_actions(self, state: Game, actions: list[Action]) -> Action:  # TODO
        pass


