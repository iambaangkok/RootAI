import numpy as np

from src.game.Game import Action


class MCTSNode:
    def __init__(self, parent=None, prev_actions=None):
        if prev_actions is None:
            prev_actions = []
        self.n = 0
        self.w = 0
        self.parent = parent
        self.children: list[(Action, MCTSNode)] = []
        self.seq_actions = prev_actions
        self.untried_actions = self.get_legal_actions()

    def get_legal_actions(self): #TODO
        # return get_legal_actions()
        pass

    def is_game_over(self):
        # return is_game_over()
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def add_child(self, action: Action, child):
        self.children.append((action, child))

    def choose_best_child(self, c_param=0.1):
        choices_weights = [(c.w / c.n + c_param * np.sqrt(np.log(self.n) / c.n)) for c in self.children]
        return self.children[np.argmax(choices_weights)]


class MCTS:
    def __init__(self, simulation_no=100):
        self.root = MCTSNode()
        self.simulation_no = simulation_no

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
        node.n += 1
        node.w += reward
        if node.parent:
            self.backpropagation(node.parent, reward)

    def run_mcts(self):
        for i in range(self.simulation_no):
            selected_node = self.selection_and_expansion()
            reward = self.rollout(selected_node)
            self.backpropagation(selected_node, reward)

        return self.root.choose_best_child()
