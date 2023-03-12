import numpy as np

from agent.policy import getPolicy, executePolicy


class AgentQL:  # agent for Q learning
    def __init__(self, ns, na, gama, alpha):
        self._gama = gama
        self._alpha = alpha
        self._q = np.zeros((ns, na))
        self._num_of_action = na
        self._epsilon = 1.0
        self._delta = 1e-3
        self._ref = 1.0
        self._average_r = 0.0

    def setExploration(self, delta):
        self._delta = delta

    def setPolicyRef(self, ref):
        self._ref = ref

    def getGreedAction(self, s, valid_actions):
        Q_select = self._q[s, valid_actions]
        index = np.argmax(Q_select)
        return valid_actions[index]

    @staticmethod
    def getRandomAction(valid_actions):
        num = len(valid_actions)
        index = np.random.randint(0, num)
        return valid_actions[index]

    def getAction(self, s, valid_actions):
        seed = np.random.rand()
        if seed < self._epsilon:
            a = self.getRandomAction(valid_actions)
        else:
            a = self.getGreedAction(s, valid_actions)
        return a

    def getPolicyAction(self, s, valid_actions):
        Q_select = self._q[s, valid_actions]
        policy = getPolicy(Q_select, self._ref)
        a = executePolicy(policy)
        return a

    def updateQ(self, s, a, r, sp):
        self._average_r = 0.99 * self._average_r + 0.01 * r
        self._ref = 0.5/ max(self._average_r, 0.1)
        print('ref=', self._ref)

        q_sp = self._q[sp, range(0, self._num_of_action)]
        target = r + self._gama * max(q_sp)
        self._q[s, a] = self._q[s, a] * (1 - self._alpha) + target * self._alpha
        self._epsilon = max(0, self._epsilon - self._delta)
