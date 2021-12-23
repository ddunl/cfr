from enum import IntEnum
import random

def sample_strategy(pdf):
    r = random.random()
    total = 0
    for i, p in enumerate(pdf):
        total += p
        if total > r:
            return i


class RPS(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


class RegretMatcher:
    def __init__(self, opp_strategy=(1/2, 1/4, 1/4)):
        self.opp_strategy = opp_strategy
        self.strategy = [1/3, 1/3, 1/3]
        self.regret_sum = [0, 0, 0]
        self.strategy_sum = [0, 0, 0]

    def recompute_strategy(self):
        norm_sum = 0
        for a in RPS: # get current regrets to compute the strategy for this iteration
            self.strategy[a] = max(self.regret_sum[a], 0)
            norm_sum += self.strategy[a]

        if norm_sum: # if we have regrets, adjust the strategy to match them
            self.strategy = [s/norm_sum for s in self.strategy]
        else: # otherwise we play a random strategy to generate regrets
            self.strategy = [1/3 for _ in self.strategy]

        # update strategy_sum
        self.strategy_sum = [s + n for s, n in zip(self.strategy, self.strategy_sum)]

    def avg_strategy(self):
        norm_sum = sum(self.strategy_sum)
        return [s/norm_sum for s in self.strategy_sum]

    def train(self):
        self.recompute_strategy()
        action = sample_strategy(self.strategy)
        opp_action = sample_strategy(self.opp_strategy)
        util = self.compute_utility(opp_action)

        for a in RPS:
            self.regret_sum[a] += util[a] - util[action]
    
    @classmethod
    def compute_utility(cls, opp_action):
        if opp_action == RPS.ROCK:
            return [0, 1, -1]
        if opp_action == RPS.PAPER:
            return [-1, 0, 1]
        if opp_action == RPS.SCISSORS:
            return [1, -1, 0]

    
if __name__ == "__main__":
    rm = RegretMatcher()

    for i in range(10000):
        rm.train()
    
    print(rm.avg_strategy())













