import logging
import time
from multiprocessing.pool import MapResult
from random import randint
from threading import Thread

import pathos.pools
import yaml
from pathos.pools import ParallelPool, ProcessPool
from pathos.serial import SerialPool

# from pathos.multiprocessing import ProcessingPool

from src.game.Faction import Faction
from src.game.GameLogic import Action, GameLogic
from src.roottrainer.agents.MCTSNode import MCTSNode

config = yaml.safe_load(open("config/config.yml"))

LOGGER = logging.getLogger('mcts_logger')


def exec_seq_actions(node: MCTSNode, game_logic: GameLogic):
    LOGGER.debug(
        "expand_and_select_node:execute_actions: len(seq_actions) {}, seq_actions {}".format(len(node.seq_actions),
                                                                                             [a.name for a in
                                                                                              node.seq_actions]))
    for seq_action in node.seq_actions:
        actions: list[Action] = game_logic.get_legal_actions()
        LOGGER.debug("expand_and_select_node:execute_actions: seq_action {}".format(seq_action.name))
        LOGGER.debug(
            "expand_and_select_node:execute_actions: len(actions) {}, actions {}".format(len(actions),
                                                                                         [a.name for a in actions]))

        legal_action: Action | None = None

        for action in actions:
            if seq_action == action:
                legal_action = action
                break

        if legal_action:
            LOGGER.debug("expand_and_select_node:execute_actions: exec {}".format(legal_action.name))
            legal_action.function()
        else:  # TODO for non-one-depth
            LOGGER.warning(
                "expand_and_select_node:execute_actions: no matching legal action for {}".format(seq_action.name))
            # raise RuntimeError
            break


def execute_random_action(game: GameLogic):
    actions = game.get_legal_actions()
    # LOGGER.debug("rollout:execute_random_action: actions {} {}".format(len(actions), [a.name for a in actions]))
    if len(actions) > 1:
        rand = randint(0, len(actions) - 1)
    elif len(actions) == 1:
        rand = 0
    else:
        rand = 0
        LOGGER.error("execute_random_action: len(actions) == {}".format(len(actions)))
    # LOGGER.debug("rollout:execute_random_action: exec {}".format(actions[rand].name))
    actions[rand].function()


def reward_function(game: GameLogic, root_state: list, reward_function_type: str) -> int:
    root_game = GameLogic()
    root_game.set_state_from_num_array(root_state)
    current_player = root_game.turn_player

    winning_faction, \
        winning_condition, \
        turns_played, \
        turn_player, \
        vp_marquise, \
        vp_eyrie, \
        winning_dominance = game.get_end_game_data()
    match reward_function_type:
        case "win":
            return 1 if current_player == winning_faction else 0
        case "vp-difference":
            if current_player == Faction.MARQUISE:
                return vp_marquise - vp_eyrie
            if current_player == Faction.EYRIE:
                return vp_eyrie - vp_marquise
        case _:
            LOGGER.error("rollout:reward_function: unknown function, reward set to 0")
            return 0


def exec_random_actions(process_id: int, game: GameLogic, reward_function_type: str, root_state: list,
                        time_limit: float, action_count_limit: int, rewards: dict[int] = None):
    acc_time: float = 0
    time_0 = time.time()
    action_count: int = 0

    while game.running:
        time_1 = time.time()
        delta_time = time_0 - time_1
        acc_time += delta_time
        if time_limit > 0:
            if acc_time >= time_limit:
                LOGGER.debug("rollout: BREAK time limit")
                break

        if action_count_limit > 0:
            if action_count >= action_count_limit:
                LOGGER.debug("rollout: BREAK action count limit")
                break

        execute_random_action(game)
        action_count += 1
        time_0 = time_1

    # rewards[process_id] = reward_function(game, root_state, reward_function_type)
    return reward_function(game, root_state, reward_function_type)


class MCTS:
    def __init__(self, state: list, actions: list[Action], reward_function: str,
                 expand_count: int, rollout_no: int,
                 time_limit: float, action_count_limit: int, depth_limit: int = 1):
        self.root: MCTSNode = MCTSNode(0, None, None, None)
        self.root_state: list = state
        self.reward_function_type = reward_function
        self.expand_count: int = expand_count
        self.rollout_no: int = rollout_no
        self.time_limit: float = time_limit
        self.depth_limit: int = depth_limit
        self.action_count_limit: int = action_count_limit

    def get_game_logic_at_root_state(self) -> GameLogic:
        game_logic: GameLogic = GameLogic()
        game_logic.set_state_from_num_array(self.root_state)
        return game_logic

    def get_game_logic_at_node(self, node: MCTSNode) -> GameLogic:
        game_logic: GameLogic = self.get_game_logic_at_root_state()
        exec_seq_actions(node, game_logic)
        return game_logic

    def expand_and_select_node(self, round):
        current: MCTSNode = self.root
        while not current.terminal_flag:
            # LOGGER.info(current.is_fully_expanded())
            if not current.is_fully_expanded():
                LOGGER.info("{}:expand_and_select_node:expand {}".format(round, [a.name for a in
                                                                                 current.seq_actions]))
                if current.untried_actions is None:
                    game: GameLogic = GameLogic()
                    game.set_state_from_num_array(self.root_state)
                    exec_seq_actions(current, game)
                    current.untried_actions = game.get_legal_actions()
                return current.expand()
            else:
                (_, best_child) = current.choose_best_child()
                LOGGER.info("{}:expand_and_select_node:select best child {}".format(round, [a.name for a in
                                                                                            best_child.seq_actions]))
                current = best_child
        return current

    def rollout(self, node: MCTSNode) -> int:

        game_logic = GameLogic()
        game_logic.set_state_from_num_array(self.root_state)

        exec_seq_actions(node, game_logic)

        ## Multicore / Single core Simulation
        if config['simulation']['multiprocessing']['enable']:
            start_time = time.time()

            core_count: int = config['simulation']['multiprocessing']['core']
            LOGGER.info("rollout: multiprocessing with {} cores".format(core_count))

            pool: ProcessPool = ProcessPool(core_count)
            rewards: MapResult = pool.amap(
                exec_random_actions, [i for i in range(self.rollout_no)],
                [game_logic] * self.rollout_no,
                [self.reward_function_type] * self.rollout_no,
                [self.root_state] * self.rollout_no,
                [self.time_limit] * self.rollout_no,
                [self.action_count_limit] * self.rollout_no)
            while not rewards.ready():
                time.sleep(1)
            end_time = time.time()
            LOGGER.info("rollout: multiprocessing with {} cores: finished in {} s"
                        .format(core_count, end_time - start_time))
            return sum(rewards.get(1))
        else:
            start_time = time.time()

            LOGGER.info("rollout: running on single process")

            rewards: dict = {}
            for i in range(self.rollout_no):
                rewards[i] = exec_random_actions(i, game_logic, self.reward_function_type, self.root_state,
                                                 self.time_limit, self.action_count_limit)
            end_time = time.time()
            LOGGER.info("rollout: running on single process: finished in {} s"
                        .format(end_time - start_time))
            return sum(rewards)

    def backpropagation(self, node: MCTSNode, reward: int):

        node.tries += self.rollout_no

        actual_reward: int = reward

        game_logic_root: GameLogic = self.get_game_logic_at_root_state()
        game_logic: GameLogic = self.get_game_logic_at_node(node)

        if game_logic_root.turn_player != game_logic.turn_player:
            actual_reward = -reward

        node.score += actual_reward

        LOGGER.debug("backpropagation: actual_reward {}, wins/tries {}/{}".format(actual_reward, node.score, node.tries))

        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        LOGGER.info("run_mcts, rollout_no {}".format(self.rollout_no))

        game: GameLogic = GameLogic()
        game.set_state_from_num_array(self.root_state)

        for i in range(self.expand_count):
            # Selection & Expansion
            LOGGER.info("{}:run_mcts: expand_and_select_node".format(i))
            selected_node = self.expand_and_select_node(i)
            # Rollout
            LOGGER.info("{}:rollout".format(i))
            reward = self.rollout(selected_node)
            # Backpropagation
            LOGGER.info("{}:backpropagation".format(i))
            self.backpropagation(selected_node, reward)

    def choose_best_action(self, actions: list[Action]) -> Action:
        best_action_sim, best_node = self.root.choose_best_child()
        LOGGER.debug("best_action_sim: action {}".format(best_action_sim.name))
        # best_action_sim: Action = best_node.seq_actions[0]
        best_action: Action | None = None

        LOGGER.debug("choose_best_action: actions {} {}".format(len(actions), [a.name for a in actions]))

        for action in actions:
            if best_action_sim == action:
                best_action = action
                break

        LOGGER.info(
            "choose_best_action: best_action_sim {}, best_action {}".format(best_action_sim.name, best_action.name))

        return best_action if best_action else None
