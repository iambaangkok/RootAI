import logging
from multiprocessing import Process, Manager
from random import randint
from threading import Thread

import pygame

from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.roottrainer.agents.MCTSNode import MCTSNode

LOGGER = logging.getLogger('mcts_logger')


def execute_random_action(game: Game):
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


def reward_function(game: Game, root_state: list, reward_function_type: str) -> int:
    root_game = Game()
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


def exec_random_actions(process_id: int, game: Game, reward_function_type: str,
                        time_limit: float, action_count_limit: int, rewards: dict[int]):
    acc_time: float = 0
    clock = pygame.time.Clock()
    action_count: int = 0

    while game.running:
        delta_time = clock.tick()
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

    clock.tick()
    rewards[process_id] = reward_function(game, reward_function_type)


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

    def expand_and_select_node(self, round):
        current: MCTSNode = self.root
        while not current.terminal_flag:
            # LOGGER.info(current.is_fully_expanded())
            if not current.is_fully_expanded():
                LOGGER.info("{}:expand_and_select_node:expand {}".format(round, [a.name for a in
                                                                                 current.seq_actions]))
                if current.untried_actions is None:
                    game: Game = Game()
                    game.set_state_from_num_array(self.root_state)
                    self.exec_seq_actions(current, game)
                    current.untried_actions = game.get_legal_actions()
                return current.expand()
            else:
                (_, best_child) = current.choose_best_child()
                LOGGER.info("{}:expand_and_select_node:select best child {}".format(round, [a.name for a in
                                                                                            best_child.seq_actions]))
                current = best_child
        return current

    def exec_seq_actions(self, node: MCTSNode, game: Game):
        LOGGER.debug(
            "expand_and_select_node:execute_actions: len(seq_actions) {}, seq_actions {}".format(len(node.seq_actions),
                                                                                                 [a.name for a in
                                                                                                  node.seq_actions]))
        for seq_action in node.seq_actions:
            actions: list[Action] = game.get_legal_actions()
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

    def rollout(self, node: MCTSNode) -> int:

        game = Game()
        game.set_state_from_num_array(self.root_state)

        self.exec_seq_actions(node, game)

        processes: list[Process] = []
        rewards: dict = Manager().dict()
        for proc_id in range(self.rollout_no):
            g = Game()
            g.set_state_from_num_array(game.get_state_as_num_array())
            processes.append(
                Process(target=exec_random_actions, args=(proc_id, game, self.reward_function_type,
                                                          self.time_limit, self.action_count_limit, rewards))
            )
        for process in processes:
            process.start()
        for process in processes:
            process.join()

        return sum(rewards)

    def backpropagation(self, node: MCTSNode, reward: int):

        node.tries += 1
        node.score += reward  # TODO for non-one-depth: reward only same turn player as root

        LOGGER.debug("backpropagation: reward {}, wins/tries {}/{}".format(reward, node.score, node.tries))

        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        LOGGER.info("run_mcts, rollout_no {}".format(self.rollout_no))

        game: Game = Game()
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
