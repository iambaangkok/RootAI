from __future__ import annotations

import logging
import sys
from random import randint

import pygame
import yaml

from src.game.Faction import Faction
from src.game.GameLogic import Action, GameLogic
from src.roottrainer.agents.MCTSNode import MCTSNode

config_path: str = str(sys.argv[1])
config = yaml.safe_load(open(config_path))

LOGGER = logging.getLogger('mcts_logger')


class MCTSOneDepth:
    def __init__(self, state: list, actions: list[Action], reward_function: str, roll_out_no: int, time_limit: float):
        self.root: MCTSNode = MCTSNode(0)
        self.root_state: list = state
        self.rollout_no: int = roll_out_no
        self.reward_function: str = reward_function
        self.time_limit: float = time_limit

    def rollout(self, node: MCTSNode) -> int:
        def execute_random_action(game_state: GameLogic):
            actions = game_state.get_legal_actions()

            LOGGER.debug("rollout:execute_random_action: actions {} {}".format(len(actions), [a.name for a in actions]))

            if len(actions) > 1:
                rand = randint(0, len(actions) - 1)
            elif len(actions) == 1:
                rand = 0
            else:
                rand = 0
                LOGGER.error("rollout:execute_random_action: len(actions) == {}".format(len(actions)))

            LOGGER.debug("rollout:execute_random_action: exec {}".format(actions[rand].name))
            actions[rand].function()

        def exec_seq_actions(game_state: GameLogic):
            LOGGER.debug(
                "rollout:exec_seq_actions: len(seq_actions) {}, seq_actions {}".format(len(node.seq_actions), [a.name for a in node.seq_actions]))

            for seq_action in node.seq_actions:
                actions: list[Action] = game_state.get_legal_actions()
                LOGGER.debug("rollout:exec_seq_actions: seq_action {}".format(seq_action.name))
                LOGGER.debug(
                    "rollout:exec_seq_actions: len(actions) {}, actions {}".format(len(actions), [a.name for a in actions]))

                legal_action: Action | None = None

                for action in actions:
                    if seq_action == action:
                        legal_action = action
                        break

                if legal_action:
                    LOGGER.debug("rollout:exec_seq_actions: exec {}".format(legal_action.name))
                    legal_action.function()
                else:
                    LOGGER.warning("rollout:exec_seq_actions: no matching legal action for {}".format(seq_action.name))
                    break

        def reward_function(game_state: GameLogic) -> int:
            root_game = GameLogic()
            root_game.set_state_from_num_array(self.root_state)
            current_player = root_game.turn_player

            winning_faction, \
                winning_condition, \
                turns_played, \
                turn_player, \
                vp_marquise, \
                vp_eyrie, \
                winning_dominance = game_state.get_end_game_data()
            match self.reward_function:
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

        game = GameLogic()
        game.set_state_from_num_array(self.root_state)

        exec_seq_actions(game)

        acc_time: float = 0
        clock = pygame.time.Clock()
        while game.running:
            delta_time = clock.tick()
            acc_time += delta_time
            if self.time_limit > 0:
                if acc_time >= self.time_limit:
                    break
            execute_random_action(game)

        return reward_function(game)

    def backpropagation(self, node: MCTSNode, reward: int):

        node.tries += 1
        node.score += reward

        LOGGER.debug("backpropagation: reward {}, wins/tries {}/{}".format(reward, node.score, node.tries))

        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        LOGGER.info("run_mcts, rollout_no {}".format(self.rollout_no))

        game: GameLogic = GameLogic()
        game.set_state_from_num_array(self.root_state)
        legal_actions: list[Action] = game.get_legal_actions()

        clock = pygame.time.Clock()
        clock.tick()
        for action in legal_actions:
            node = MCTSNode(1, self.root, self.root.seq_actions[:])
            self.root.add_child(action, node)

            for i in range(self.rollout_no):
                LOGGER.debug("run_mcts: node {}, rollout_no {}/{}".format(action.name, i + 1, self.rollout_no))
                reward = self.rollout(node)
                self.backpropagation(node, reward)

            LOGGER.debug("run_mcts: node {}, len(seq_actions) {}".format(action.name, len(node.seq_actions)))

        total_rollout_time = clock.tick()
        LOGGER.info("run_mcts: total_rollout_time {} seconds".format(total_rollout_time/1000.0))

    def choose_best_action(self, actions: list[Action]) -> Action:
        best_action_sim, best_node = self.root.choose_best_child()
        LOGGER.debug("best_action_sim: action {}".format(best_action_sim.name))
        best_action: Action | None = None

        LOGGER.debug("choose_best_action: actions {} {}".format(len(actions), [a.name for a in actions]))

        for action in actions:
            if best_action_sim == action:
                best_action = action
                break

        LOGGER.info("choose_best_action: best_action_sim {}, best_action {}".format(best_action_sim.name, best_action.name))

        return best_action if best_action else None
