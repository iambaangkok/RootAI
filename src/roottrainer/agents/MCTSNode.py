from __future__ import annotations

import logging
from typing import Union

import numpy as np
import scipy.stats as st

from src.game.GameLogic import Action

LOGGER = logging.getLogger('mcts_logger')


def map_dice_roll_to_child(d1, d2):
    f = [0, 1, 3, 6]
    g = [0, 1, 2, 3]

    return f[max(d1, d2)] + g[min(d1, d2)]


class MCTSNode:
    def __init__(self, depth: int = 0, parent: MCTSNode = None, prev_actions: list[Action] = None,
                 untried_actions: list[Action] = None, roll_dice_state=False, attacker_roll=-1, defender_roll=-1):
        if prev_actions is None:
            prev_actions = []

        self.depth: int = depth
        self.tries: int = 0
        self.score: int = 0
        self.score_list: list[int] = []
        self.parent = parent
        self.children: list[(Action, MCTSNode)] = []
        self.seq_actions: list[Union[Action, (int, int, Action)]] = prev_actions if prev_actions else []
        self.untried_actions = untried_actions
        self.terminal_flag = False

        self.roll_dice_state = roll_dice_state
        self.attacker_roll = attacker_roll
        self.defender_roll = defender_roll

    def add_child(self, action: Action, child: MCTSNode):
        self.children.append((action, child))
        if child.roll_dice_state:
            child.seq_actions = self.seq_actions + [(child.attacker_roll, child.defender_roll, action)]
        else:
            child.seq_actions = self.seq_actions + [action]
        # NOTE: seq_actions: action closer to leaf is added at the BACK of the list

    def choose_best_child(self, criteria='max', c_param=2) -> (Action, MCTSNode):

        if criteria == 'max':
            choices_reward = [c.score for _, c in self.children]

            LOGGER.info(
                "choose_best_child: child actions {} {}".format(len(self.children), [a.name for a, c in self.children]))
            LOGGER.info("choose_best_child: choices_reward {}".format(str(choices_reward)))
            LOGGER.info("choose_best_child: params <score, tries> {}".format(str(
                ["<{}, {}>".format(c.score, c.tries) for a, c in
                 self.children] + ["<{}, {}>".format(self.score, self.tries)]
            )
            ))

            return self.children[np.argmax(choices_reward)]
        elif criteria == 'robust':
            choices_most_visited = [c.tries for _, c in self.children]

            LOGGER.info(
                "choose_best_child: child actions {} {}".format(len(self.children), [a.name for a, c in self.children]))
            LOGGER.info("choose_best_child: choices_most_visited {}".format(str(choices_most_visited)))
            LOGGER.info("choose_best_child: params <score, tries> {}".format(str(
                ["<{}, {}>".format(c.score, c.tries) for a, c in
                 self.children] + ["<{}, {}>".format(self.score, self.tries)]
            )
            ))

            return self.children[np.argmax(choices_most_visited)]
        elif criteria == 'UCB':
            choices_weights: list[float] = [
                (c.score / c.tries + c_param * np.sqrt(np.log(self.tries) / c.tries)) if c.tries != 0 else float('-inf')
                for
                a, c in
                self.children]
            LOGGER.info(
                "choose_best_child: child actions {} {}".format(len(self.children), [a.name for a, c in self.children]))
            LOGGER.info("choose_best_child: choices_weights {}".format(str(choices_weights)))
            LOGGER.info("choose_best_child: params <score, tries> {}".format(str(
                ["<{}, {}>".format(c.score, c.tries) for a, c in
                 self.children] + ["<{}, {}>".format(self.score, self.tries)]
            )
            ))
            return self.children[np.argmax(choices_weights)]
        elif criteria == 'secure':
            rewards = [self.mean_confidence_interval(c.score_list) for _, c in self.children]
            rewards_lower_bound = [r[1] for r in rewards]

            LOGGER.info(
                "choose_best_child: child actions {} {}".format(len(self.children), [a.name for a, c in self.children]))
            LOGGER.info("choose_best_child: rewards_lower_bound {}".format(str(rewards_lower_bound)))
            LOGGER.info("choose_best_child: params <score, tries> {}".format(str(
                ["<{}, {}>".format(c.score, c.tries) for a, c in
                 self.children] + ["<{}, {}>".format(self.score, self.tries)]
            )
            ))
            return self.children[np.argmax(rewards_lower_bound)]

    def mean_confidence_interval(self, data, confidence=0.95):
        if len(data) == 1:  # approximation error
            m = data[0]
            h = (1 - confidence) * m
            return m, m - h, m + h
        else:  # confidence interval
            a = 1.0 * np.array(data)
            n = len(a)
            m, se = np.mean(a), st.sem(a)
            h = se * st.t.ppf((1 + confidence) / 2., n - 1)
            return m, m - h, m + h

    def is_fully_expanded(self):
        if self.untried_actions is None:
            return False
        return len(self.untried_actions) == 0

    def roll_dice_state_child(self, attacker_roll, defender_roll):
        return self.children[map_dice_roll_to_child(attacker_roll, defender_roll)]

    def expand(self, roll_dice_state=False, attacker_roll=-1, defender_roll=-1):

        # LOGGER.info("untried_actions: {}".format([n.name for n in self.untried_actions]))
        action = self.untried_actions.pop()

        # LOGGER.info("action: {}".format(action.name))

        if roll_dice_state:
            for i in range(0, 4):
                for j in range(i, 4):
                    child = MCTSNode(self.depth + 1, self, self.seq_actions + [action], None, True, j, i)
                    self.add_child(action, child)

            return self.roll_dice_state_child(attacker_roll, defender_roll)[1]

        else:
            # LOGGER.info("pre-add-children: {}".format([(n[0].name,n[1]) for n in self.children]))
            child = MCTSNode(self.depth + 1, self, self.seq_actions + [action], None)
            self.add_child(action, child)
            # LOGGER.info("post-add-children: {}".format([(n[0].name,n[1]) for n in self.children]))
            LOGGER.debug("add child: {}".format([n for n in self.seq_actions + [action]]))

            return child
