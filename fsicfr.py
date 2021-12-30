import random
import numpy as np
from numpy.core.numeric import full


class Node:
    all_nodes = []
    def __init__(self, card, hist):
        Node.all_nodes.append(self)
        self.card = card
        self.hist = hist
        self.player = len(hist) % 2
        self.opp = 1 - self.player
        self.regret = np.zeros((2,), dtype=np.float64)
        self.strat = np.zeros((2,), dtype=np.float64)
        self.strat_sum = np.zeros((2,), dtype=np.float64)
        self.p0 = 0
        self.p1 = 0
        self.iter_visits = 0
        self.total_visits = 0
        self.util = 0
        self.is_terminal = len(hist) > 1 and (hist[-1] == "p" or hist[-2:] == "bb")

    @classmethod
    def construct_graph(cls):
        cache = {(card, ""): Node(card, "") for card in range(3)}
        roots = list(cache.values())
        for node in roots:
            node.make_children(cache)

        return roots



    def make_children(self, cache):

        if self.is_terminal:
            self.children = ()
            return
        
        self.children = [[], []]
        action_space = "pb"
        for a in (0, 1):
            for c in range(3):
                new_hist = self.hist + action_space[a]
                if (c, new_hist) in cache:
                    self.children[a].append(cache[c, new_hist])
                else:
                    node = Node(c, new_hist)
                    node.make_children(cache)
                    cache[c, new_hist] = node
                    self.children[a].append(node)
    
    def get_child(self, action, cards):
        return self.children[action][cards[self.opp]]

    def bfs(self, cards):
        """needs to be bfs"""
        idx = 0
        queue = [self]

        while idx < len(queue):
            node = queue[idx]
            valid_children = [c[cards[node.opp]] for c in node.children]
            queue.extend(valid_children)
            idx += 1

        return queue


    def compute_strategy(self):
        floored_regrets = np.maximum(self.regret, np.zeros_like(self.regret))
        norm_sum = np.sum(floored_regrets)

        if norm_sum > 0:
            self.strat = floored_regrets/np.sum(floored_regrets)
        else:
            self.strat = np.array([0.5, 0.5])

        p = self.p0 if self.player == 0 else self.p1
        self.strat_sum += self.strat * p
    
    def compute_util(self, deck):
        if self.hist == "pp":
            self.util = 1 if deck[self.player] > deck[self.opp] else -1

        if self.hist[-1] == "p":
            self.util = 1

        if self.hist[-2:] == "bb":
            self.util = 2 if deck[self.player] > deck[self.opp] else -2

    def avg_strategy(self):
        assert np.sum(self.strat_sum) > 0, (self, self.strat_sum)
        return [round(n, 2) for n in self.strat_sum/np.sum(self.strat_sum)]

    def reset(self):
        self.p0 = 0
        self.p1 = 0
        self.iter_visits = 0

    def __repr__(self):
        return f"Node<{self.card=}, {self.hist=}, {self.player=}, {self.strat_sum=}>"


class FSICFR:
    def __init__(self):
        self.deck = [0, 1, 2]

    def train(self, i, roots):
        random.shuffle(self.deck)
        root = roots[self.deck[0]]
        
        nodes = root.bfs(self.deck)
        for n in nodes:
            if n.is_terminal:
                continue
            if n is root:
                n.iter_visits = 1
                n.p0 = 1
                n.p1 = 1


            n.compute_strategy()

            for a in (0, 1):
                c = n.get_child(a, self.deck)
                c.iter_visits += n.iter_visits

                if n.player == 0:
                    c.p0 += n.strat[a] * n.p0
                    c.p1 += n.p1
                else:
                    c.p0 += n.p0
                    c.p1 += n.strat[a] * n.p1


        for n in reversed(nodes):
            if n.is_terminal:
                n.compute_util(self.deck)

            else:
                n.util = 0
                # compute utility
                for a in (0, 1):
                    c = n.get_child(a, self.deck)
                    n.util += n.strat[a] * -c.util
                for a in (0, 1):
                    c = n.get_child(a, self.deck)
                    cfp = n.p0 if n.player == 1 else n.p1
                    coef = 1 / (n.iter_visits + n.total_visits)
                    cfv = -c.util - n.util
                    n.regret[a] = coef * (n.total_visits * n.regret[a] + n.iter_visits * cfp * cfv)

                n.total_visits += n.iter_visits

            n.reset()




if __name__ == "__main__":
    cfr = FSICFR()
    roots = Node.construct_graph()

    for i in range(100000):
        cfr.train(i, roots)


    
    for node in sorted(Node.all_nodes, key=lambda n: (n.card, n.hist)):
        if not node.is_terminal:
            print(node, node.strat, node.avg_strategy())





