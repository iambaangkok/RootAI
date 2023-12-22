from __future__ import annotations

import logging
from random import randint

import numpy as np

from src.game.Game import Action, Game
from src.roottrainer.agents.mcts import MCTSNode

LOGGER = logging.getLogger('mcts_logger')


class MCTSOneDepth:
    def __init__(self, state: list, actions: list[Action], roll_out_no: int = 1):
        self.root: MCTSNode = MCTSNode(0)
        self.root_state: list = state
        self.rollout_no: int = roll_out_no

    def rollout(self, node: MCTSNode) -> int:
        def execute_random_action(game: Game):
            actions = game.get_legal_actions()

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

        def reward_function(game: Game) -> int:
            root_game = Game()
            root_game.set_state_from_num_array(self.root_state)
            winning_faction, \
                winning_condition, \
                turns_played, \
                turn_player, \
                vp_marquise, \
                vp_eyrie, \
                winning_dominance = game.get_end_game_data()

            return 1 if root_game.turn_player == winning_faction else 0

        def exec_seq_actions(game: Game):
            LOGGER.debug(
                "rollout:exec_seq_actions: len(seq_actions) {}, seq_actions {}".format(len(node.seq_actions), [a.name for a in node.seq_actions]))

            for seq_action in node.seq_actions:
                actions: list[Action] = game.get_legal_actions()
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
                else:  # TODO for non-one-depth
                    LOGGER.warning("rollout:exec_seq_actions: no matching legal action for {}".format(seq_action.name))
                    # raise RuntimeError
                    break

        game = Game()
        game.set_state_from_num_array(self.root_state)

        exec_seq_actions(game)

        while game.running:
            execute_random_action(game)

        return reward_function(game)

    def backpropagation(self, node: MCTSNode, reward: int):

        node.tries += 1
        node.wins += reward  # TODO for non-one-depth: reward only same turn player as root

        LOGGER.info("backpropagation: reward {}, wins/tries {}/{}".format(reward, node.wins, node.tries))

        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        LOGGER.info("run_mcts".format())

        game: Game = Game()
        game.set_state_from_num_array(self.root_state)
        legal_actions: list[Action] = game.get_legal_actions()

        for action in legal_actions:
            node = MCTSNode(1, self.root, self.root.seq_actions[:])
            self.root.add_child(action, node)

            for i in range(self.rollout_no):
                LOGGER.info("run_mcts: node {}, rollout_no {}/{}".format(action.name, i + 1, self.rollout_no))
                reward = self.rollout(node)
                self.backpropagation(node, reward)

            LOGGER.debug("run_mcts: node {}, len(seq_actions) {}".format(action.name, len(node.seq_actions)))

        # return self.root.choose_best_child()

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

        LOGGER.info("choose_best_action: best_action_sim {}, best_action {}".format(best_action_sim.name, best_action.name))

        return best_action if best_action else None
