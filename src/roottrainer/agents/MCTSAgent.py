from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.agents.Agent import Agent
from src.roottrainer.agents.OneDepthMCTS import MCTSOneDepth
from src.roottrainer.agents.mcts import MCTSNode, MCTS


class MCTSAgent(Agent):
    def __init__(self, faction: Faction, mcts_type: str):
        super().__init__(faction)
        self.agent_type: str = "mcts"
        self.mcts_type: str = mcts_type

    def choose_action(self, state: list, actions: list[Action]) -> Action:
        match self.mcts_type:
            case "one-depth":
                mcts = MCTSOneDepth(state, actions, 5)
            case _:
                mcts = MCTS(state, actions)

        mcts.run_mcts()

        return mcts.choose_best_action(actions)

    def run_mcts(self, state: list, actions: list[Action]) -> Action:  # TODO
        pass


