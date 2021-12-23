import random
from collections import defaultdict

class Node:
    def __init__(self, info_set):
        self.info_set = info_set
        self.strategy = [0, 0]
        self.strategy_sum = [0, 0]
        self.regret_sum = [0, 0]

    def recompute_strategy(self, rw):
        norm_sum = 0

        for a in (0, 1):
            self.strategy[a] = max(self.regret_sum[a], 0)
            norm_sum += self.strategy[a]

        if norm_sum:
            self.strategy = [s/norm_sum for s in self.strategy]
        else:
            self.strategy = [1/2 for _ in self.strategy]

        self.strategy_sum = [rw * (n + s) for n, s in zip(self.strategy, self.strategy_sum)]
        return self.strategy

    def avg_strategy(self, digits=4): # only valid after node has been reached in training
        norm_sum = sum(self.strategy_sum)
        if not norm_sum: return [1/2, 1/2]
        return [round(s/norm_sum, digits) for s in self.strategy_sum]



class CFR:
    def __init__(self):
        self.node_map = {}
        self.util = 0


    def cfr(self, cards, hist, p0, p1):
        plays = len(hist)
        player = plays % 2
        opp = 1 - player

        if plays > 1: # check if we are in terminal state, then return appropriate value
            if hist[-1] == "p":
                if hist == "pp":
                    return 1 if cards[player] > cards[opp] else -1
                else:
                    return 1
            elif hist[-2:] == "bb":
                return 2 if cards[player] > cards[opp] else -2

        # get node or create it
        info_set = cards[player], hist
        if info_set in self.node_map:
            node = self.node_map[info_set]
        else:
            node = Node(info_set)
            self.node_map[info_set] = node

        
        # call cfr on other strategies

        strategy = node.recompute_strategy(p0 if player == 0 else p1)
        util = [0, 0]
        node_util = 0

        for a in (0, 1):
            new_hist = hist + ("b" if a else "p")
            if player == 0:
                util[a] = -self.cfr(cards, new_hist, p0*strategy[a], p1)
            else:
                util[a] = -self.cfr(cards, new_hist, p0, strategy[a]*p1)

            node_util += strategy[a] * util[a]

        for a in (0, 1):
            regret = util[a] - node_util
            node.regret_sum[a] += (p1 if player == 0 else p0) * regret

        return node_util

    def train(self):
        deck = [1, 2, 3]
        random.shuffle(deck)
        self.util += self.cfr(deck, "", 1, 1)

if __name__ == "__main__":
    cfr = CFR()

    for i in range(200000):
        cfr.train()

    for node in sorted(cfr.node_map.values(), key=lambda n: n.info_set):
        print(node.info_set, node.avg_strategy())






