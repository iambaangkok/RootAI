from __future__ import annotations

import logging

import numpy as np

from src.game.Game import Action

LOGGER = logging.getLogger('mcts_logger')


class MCTSNode:
    def __init__(self, depth: int = 0, parent: MCTSNode = None, prev_actions: list[Action] = None):
        if prev_actions is None:
            prev_actions = []

        self.depth: int = depth
        self.tries: int = 0
        self.wins: int = 0
        self.parent = parent
        self.children: list[(Action, MCTSNode)] = []
        self.seq_actions: list[Action] = prev_actions if prev_actions else []
        self.untried_actions = self.get_legal_actions()

    def get_legal_actions(self):  # TODO
        # return get_legal_actions()
        pass

    def is_game_over(self):
        # return is_game_over()
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def add_child(self, action: Action, child: MCTSNode):
        self.children.append((action, child))
        child.seq_actions = self.seq_actions + [action]
        # NOTE: seq_actions: action closer to leaf is added at the BACK of the list

    def choose_best_child(self, c_param=0.1) -> (Action, MCTSNode):
        choices_weights: list[float] = [(c.wins / c.tries + c_param * np.sqrt(np.log(self.tries) / c.tries)) for a, c in self.children]
        LOGGER.info("choose_best_child: choices_weights {}".format(str(choices_weights)))
        return self.children[np.argmax(choices_weights)]


class MCTS:
    def __init__(self, state: list, actions: list[Action], simulation_no: int = 100):
        self.root: MCTSNode = MCTSNode(0)
        self.simulation_no: int = simulation_no

    def selection_and_expansion(self):
        current_node: MCTSNode = self.root
        while not current_node.is_game_over():
            if not current_node.is_fully_expanded():
                return self.expansion(current_node)
            else:
                current_node = current_node.choose_best_child()
        return current_node

    def expansion(self, node):
        action = node.untried_actions.pop()
        child = MCTSNode(node, node.seq_actions + [action])
        node.add_child(action, child)
        return child

    def rollout(self, node):
        # run simulation by sampling states from seq_actions in node
        # sample_state = Game.sample_state(node.seq_actions)
        # reward = Game.playout(sample_state)
        reward = len(node.seq_actions) % 2
        return reward

    def backpropagation(self, node, reward):
        node.tries += 1
        node.wins += reward
        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        for i in range(self.simulation_no):
            selected_node = self.selection_and_expansion()
            reward = self.rollout(selected_node)
            self.backpropagation(selected_node, reward)

        return self.root.choose_best_child()