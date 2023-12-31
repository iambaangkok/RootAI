from __future__ import annotations

import logging

import numpy as np

from src.game.Game import Action

LOGGER = logging.getLogger('mcts_logger')


class MCTSNode:
    def __init__(self, depth: int = 0, parent: MCTSNode = None, prev_actions: list[Action] = None,
                 untried_actions: list[Action] = None):
        if prev_actions is None:
            prev_actions = []

        self.depth: int = depth
        self.tries: int = 0
        self.score: int = 0
        self.parent = parent
        self.children: list[(Action, MCTSNode)] = []
        self.seq_actions: list[Action] = prev_actions if prev_actions else []
        self.untried_actions = untried_actions
        self.terminal_flag = False

    def add_child(self, action: Action, child: MCTSNode):
        self.children.append((action, child))
        child.seq_actions = self.seq_actions + [action]
        # NOTE: seq_actions: action closer to leaf is added at the BACK of the list

    def choose_best_child(self, c_param=0.1) -> (Action, MCTSNode):
        choices_weights: list[float] = [(c.score / c.tries + c_param * np.sqrt(np.log(self.tries) / c.tries)) for a, c in
                                        self.children]
        LOGGER.info(
            "choose_best_child: child actions {} {}".format(len(self.children), [a.name for a, c in self.children]))
        LOGGER.info("choose_best_child: choices_weights {}".format(str(choices_weights)))
        return self.children[np.argmax(choices_weights)]

    def is_fully_expanded(self):
        if self.untried_actions is None:
            return False
        return len(self.untried_actions) == 0

    def expand(self):

        # LOGGER.info("untried_actions: {}".format([n.name for n in self.untried_actions]))

        action = self.untried_actions.pop()
        # LOGGER.info("action: {}".format(action.name))

        # LOGGER.info("pre-add-children: {}".format([(n[0].name,n[1]) for n in self.children]))
        child = MCTSNode(self.depth + 1, self, self.seq_actions + [action], None)
        self.add_child(action, child)
        # LOGGER.info("post-add-children: {}".format([(n[0].name,n[1]) for n in self.children]))
        LOGGER.info("add child: {}".format([n.name for n in self.seq_actions + [action]]))

        return child
