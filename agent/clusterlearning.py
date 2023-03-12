import numpy as np
import tensorflow as tf

from agent.simplelearning import AgentQL


class AgentCL:
    def __init__(self, name, na, gama, alpha):
        self._model = tf.keras.models.load_model(name)
        shape = self._model.input_shape
        self._input_shape = [shape[1], shape[2], shape[3]]
        self._num_of_states = self._model.output_shape[1]
        self._ql = AgentQL(self._num_of_states, na, gama, alpha)
        self._num_of_actions = na
        self._state_map = []

    def setExploration(self, delta):
        self._ql.setExploration(delta)

    def stateQuantization(self, s):
        sn = self.findInMap(s)
        if sn >= 0:
            return sn

        pred = self._model.predict(s.reshape([1] + self._input_shape))
        sn = np.argmax(pred)
        self._state_map.append([s, sn])
        if (len(self._state_map)) >= 4:
            self._state_map.pop(0)
        return sn

    def findInMap(self, s):
        N = len(self._state_map)
        for n in range(0, N):
            [state, index] = self._state_map[n]
            error = sum(sum(abs(state - s)))
            if error < 0.001:
                return index
        return -1

    def getAction(self, s):
        sn = self.stateQuantization(s)
        valid_actions = range(0, self._num_of_actions)
        a = self._ql.getAction(sn, valid_actions)
        return a

    def learning(self, s, a, r, sp):
        sn = self.stateQuantization(s)
        spn = self.stateQuantization(sp)
        self._ql.updateQ(sn, a, r, spn)

    @property
    def input_shape(self):
        return self._input_shape


class AgentASL:
    # all channel states learning.
    # In fact, it can describe all channel states when there are only occupation and vacant states of channels.
    def __init__(self, shape, na, gama, alpha):
        self._input_shape = shape
        self._num_of_states = 2 ** shape[1]  # the number of states
        self._ql = AgentQL(self._num_of_states, na, gama, alpha)
        self._num_of_actions = na

    def setExploration(self, delta):
        self._ql.setExploration(delta)

    def stateQuantization(self, s):
        b = 1
        sn = 0
        for n in range(0, self._num_of_actions):
            if s[0, n] > -70:
                sn = sn + b
            b = b * 2
        return sn

    def getAction(self, s):
        sn = self.stateQuantization(s)
        valid_actions = range(0, self._num_of_actions)
        a = self._ql.getPolicyAction(sn, valid_actions)
        return a

    def learning(self, s, a, r, sp):
        sn = self.stateQuantization(s)
        spn = self.stateQuantization(sp)
        self._ql.updateQ(sn, a, r, spn)

    @property
    def input_shape(self):
        return self._input_shape
