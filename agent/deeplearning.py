import numpy as np
import tensorflow as tf


def Create_CNN(shape, out_dim):
    inputs = tf.keras.Input(shape=shape)

    cn = tf.keras.layers.Conv2D(filters=16, kernel_size=(10, 4), strides=2,
                                padding='same', activation='tanh')(inputs)

    fl = tf.keras.layers.Flatten()(cn)
    fl = tf.keras.layers.Dense(512, activation='sigmoid')(fl)
    outputs = tf.keras.layers.Dense(out_dim, activation='linear')(fl)
    model = tf.keras.models.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam',
                  loss='mse')  # categorical_cross entropy
    return model


class DqnAgent:
    Batch_Size = 128
    Max_Record_Size = 4000

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

    def setExploration(self, delta):
        self._delta = delta

    def get_greed_action(self, s):
        q_sa = self._model.predict(s.reshape([1] + self._input_shape))
        a = np.argmax(q_sa)
        return a

    def get_random_action(self):
        a = np.random.randint(0, self._num_of_actions)
        return a

    def get_action(self, s):
        seed = np.random.rand()
        if seed < self._epsilon:
            a = self.get_random_action()
        else:
            a = self.get_greed_action(s)
        return a

    def update_DNN(self):
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

        return loss

    def learning(self, s, a, r, sp):  #
        exp = [s, a, r, sp]
        loss = 0
        self._records.append(exp)
        if self.get_record_size() > self.Max_Record_Size:
            self._records.pop(0)

        if self.get_record_size() >= self.Batch_Size:
            if self._count == 0:
                loss = self.update_DNN()
            self._count = (self._count + 1) % self._update_interval

        self._epsilon = max(0, self._epsilon - self._delta)
        return loss

    def get_record_size(self):
        return len(self._records)

    @property
    def input_shape(self):
        return self._input_shape
