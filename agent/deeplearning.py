import numpy as np
import tensorflow as tf

from agent.policy import getPolicy, executePolicy


def Create_CNN(shape, out_dim):
    inputs = tf.keras.Input(shape=shape)

    cn = tf.keras.layers.Conv2D(filters=16, kernel_size=(10, 4), strides=2,
                                padding='same', activation='tanh')(inputs)

    fl = tf.keras.layers.Flatten()(cn)
    fl = tf.keras.layers.Dense(512, activation='sigmoid')(fl)
    outputs = tf.keras.layers.Dense(out_dim, activation='linear')(fl)  # for q learning, linear is very important
    model = tf.keras.models.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam',
                  loss='mse')  # categorical_cross entropy
    return model


class AgentDQN:
    Batch_Size = 128
    Max_Record_Size = 5000

    def __init__(self, shape, na, gama, alpha):
        self._input_shape = shape
        self._num_of_actions = na
        self._gama = gama
        self._alpha = alpha
        self._records = []
        self._input_shape = shape
        self._model = Create_CNN(self._input_shape, self._num_of_actions)
        self._count = 0
        self._update_interval = 10
        self._epsilon = 1.0
        self._delta = 1e-3
        self._loss_records = []
        self._ref = 1.0
        self._average_r = 0.0

    def setExploration(self, delta):
        self._delta = delta

    def get_greed_action(self, s):
        q_sa = self._model.predict(s.reshape([1] + self._input_shape))
        print('q=', q_sa)
        a = np.argmax(q_sa)
        return a

    def getRandomAction(self):
        a = np.random.randint(0, self._num_of_actions)
        return a

    def getAction(self, s):
        seed = np.random.rand()
        if seed < self._epsilon:
            a = self.getRandomAction()
        else:
            a = self.get_greed_action(s)
        return a

    def getPolicyAction(self, s):
        q_sa = self._model.predict(s.reshape([1] + self._input_shape))
        policy = getPolicy(q_sa, self._ref)
        print('Q=', q_sa)
        print('P=', policy)
        a = executePolicy(policy)
        return a

    def updateDNN(self):
        record_size = len(self._records)

        s_batch = np.zeros(([self.Batch_Size] + self._input_shape))
        a_batch = np.zeros((self.Batch_Size, 1), dtype='int32')
        r_batch = np.zeros((self.Batch_Size, 1))
        sp_batch = np.zeros(([self.Batch_Size] + self._input_shape))

        # select samples randomly
        index = np.random.choice(record_size, self.Batch_Size, replace=False)
        for n in range(0, self.Batch_Size):
            [s, a, r, sp] = self._records[index[n]]
            s_batch[n] = s
            a_batch[n] = a
            r_batch[n] = r
            sp_batch[n] = sp

        # calculate target values
        pred = self._model.predict(sp_batch)
        target = self._model.predict(s_batch)

        for n in range(0, self.Batch_Size):
            pred_n = pred[n]
            Q_sp = np.max(pred_n)
            a = a_batch[n]
            target[n, a] = target[n, a] * (1 - self._alpha) + (r_batch[n] + self._gama * Q_sp) * self._alpha

        hist = self._model.fit(s_batch, target, batch_size=32, epochs=10, verbose=0)
        loss = hist.history['loss'][-1]

        self._loss_records.append(loss)

        return loss

    def learning(self, s, a, r, sp):  #
        exp = [s, a, r, sp]
        self._average_r = 0.99 * self._average_r + 0.01 * r
        self._ref = 0.5/ max(self._average_r, 0.1)
        print('ref=', self._ref)

        loss = 0
        self._records.append(exp)
        if self.getRecordSize() > self.Max_Record_Size:
            self._records.pop(0)

        if self.getRecordSize() >= self.Batch_Size:
            if self._count == 0:
                loss = self.updateDNN()
            self._count = (self._count + 1) % self._update_interval

        self._epsilon = max(0, self._epsilon - self._delta)
        return loss

    def getRecordSize(self):
        return len(self._records)

    def saveModel(self, name):
        self._model.save(name)

    def loadModel(self, name):
        self._model = tf.keras.models.load_model(name)

    def saveRecord(self, name):
        N = self.getRecordSize()
        s_batch = np.zeros(([N] + self._input_shape))
        # a_batch = np.zeros([N, 1])
        # r_batch = np.zeros([N, 1])
        # sp_batch = np.zeros(([N] + self._input_shape))
        for n in range(0, N):
            [s, a, r, sp] = self._records[n]
            s_batch[n] = s
            # a_batch[n] = a
            # r_batch[n] = r
            # sp_batch[n] = sp
        np.savez(name, N=N, M=self._num_of_actions, s=s_batch)

    @property
    def input_shape(self):
        return self._input_shape

    @property
    def loss_records(self):
        return self._loss_records
