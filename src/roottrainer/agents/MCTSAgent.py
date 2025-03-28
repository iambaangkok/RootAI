import logging

from game.Faction import Faction
from game.GameLogic import Action
from roottrainer.agents.Agent import Agent
from roottrainer.agents.MCTS import MCTS
from roottrainer.agents.OneDepthMCTS import MCTSOneDepth

LOGGER = logging.getLogger('mcts_logger')


class MCTSAgent(Agent):
    def __init__(self, faction: Faction, mcts_type: str, reward_function: str, expand_count: int, rollout_no: int,
                 time_limit: float, action_count_limit: int, best_action_policy: str):
        super().__init__(faction)
        self.agent_type: str = "mcts"
        self.mcts_type: str = mcts_type
        self.reward_function: str = reward_function
        self.expand_count: int = expand_count
        self.rollout_no: int = rollout_no
        self.time_limit: float = time_limit
        self.action_count_limit: int = action_count_limit
        self.best_action_policy: str = best_action_policy
        LOGGER.info(
            "MCTSAgent:__init__: type {}, reward_function {}, expand_count {}, rollout_no {}, time_limit {}, action_count_limit {}, best action policy {}"
            .format(mcts_type, reward_function, expand_count, rollout_no, time_limit, action_count_limit,
                    best_action_policy))

    def choose_action(self, state: list, actions: list[Action]) -> Action:
        match self.mcts_type:
            case "one-depth":
                mcts = MCTSOneDepth(state, actions,
                                    self.reward_function, self.rollout_no, self.time_limit)
            case _:
                mcts = MCTS(state, actions, self.reward_function, self.expand_count, self.rollout_no, self.time_limit,
                            self.action_count_limit, self.best_action_policy)

        mcts.run_mcts()

        return mcts.choose_best_action(actions)

    def run_mcts(self, state: list, actions: list[Action]) -> Action:  # TODO
        pass
