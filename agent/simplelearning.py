import numpy as np


class AgentQL:  # agent for Q learning
    def __init__(self, ns, na, gama, alpha):
        self._gama = gama
        self._alpha = alpha
        self._q = np.zeros((ns, na))
        self._num_of_action = na

    def get_greed_action(self, s, valid_actions):
        Q_select = self._q[s, valid_actions]
        index = np.argmax(Q_select)
        return valid_actions[index]

    @staticmethod
    def get_random_action(valid_actions):
        num = len(valid_actions)
        index = np.random.randint(0, num)
        return valid_actions[index]

    def get_action(self, s, epsilon, valid_actions):
        seed = np.random.rand()
        if seed < epsilon:
            a = self.get_random_action(s, valid_actions)
        else:
            a = self.get_greed_action(s, valid_actions)
        return a

    def update_q(self, s, a, sp, r):
        q_sp = self._q[sp, range(0, self._num_of_action)]
        target = r + self._gama * max(q_sp)
        self._q[s, a] = self._q[s, a] * (1 - self._alpha) + target * self._alpha
