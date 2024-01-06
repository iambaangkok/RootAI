import logging

from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.agents.Agent import Agent
from src.roottrainer.agents.MCTS import MCTS
from src.roottrainer.agents.OneDepthMCTS import MCTSOneDepth

LOGGER = logging.getLogger('mcts_logger')


class MCTSAgent(Agent):
    def __init__(self, faction: Faction, mcts_type: str, reward_function: str, rollout_no: int, time_limit: float):
        super().__init__(faction)
        self.agent_type: str = "mcts"
        self.mcts_type: str = mcts_type
        self.reward_function: str = reward_function
        self.rollout_no: int = rollout_no
        self.time_limit: float = time_limit
        LOGGER.info("MCTSAgent:__init__: type {}, reward_function {}, rollout_no {}, time_limit {}"
                    .format(mcts_type, reward_function, rollout_no, time_limit))

    def choose_action(self, state: list, actions: list[Action]) -> Action:
        match self.mcts_type:
            case "one-depth":
                mcts = MCTSOneDepth(state, actions,
                                    self.reward_function, self.rollout_no, self.time_limit)
            case _:
                mcts = MCTS(state, actions, self.reward_function, self.rollout_no, self.time_limit)

        mcts.run_mcts()

        return mcts.choose_best_action(actions)

    def run_mcts(self, state: list, actions: list[Action]) -> Action:  # TODO
        pass
