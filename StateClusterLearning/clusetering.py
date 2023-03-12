from typing import List, Any

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import scipy.io as scio


def vector_distance(x, y):
    z = (x - y)
    z2 = z * z
    d = sum(z2)
    return d


def vector_means(x, N):
    y = np.zeros([1, 10])
    for n in range(0, N):
        y = y + x[n]
    y = y / N
    return y


def kmeans_clustering(data, N, M, L):
    index = np.random.choice(N, L, replace=False)
    q = np.zeros([L, M])  # quantization level

    elements: list[list[Any]] = []
    for l in range(0, L):
        q[l] = data[index[l]]
        elements.append([])

    for i in range(0, 10):  # iter times
        for l in range(0, L):
            elements[l].clear()
        acc_err = 0
        for n in range(0, N):
            d = np.zeros([L])
            for m in range(0, L):
                d[m] = vector_distance(q[m], data[n])
            l = np.argmin(d)
            elements[l].append(n)
            acc_err = acc_err + d[l]
        print(acc_err / N / M)

        for l in range(0, L):
            elements_number = len(elements[l])
            if elements_number > 0:
                q[l] = vector_means(data[elements[l]], elements_number)

    label = np.zeros([N, L])

    for l in range(0, L):
        label[elements[l], l] = 1

    return [label, elements]


def Create_CNN(shape, out_dim):
    inputs = tf.keras.Input(shape=shape)

    cn = tf.keras.layers.Conv2D(filters=16, kernel_size=(10, 4), strides=2,
                                padding='same', activation='tanh')(inputs)

    fl = tf.keras.layers.Flatten()(cn)
    fl = tf.keras.layers.Dense(512, activation='sigmoid')(fl)
    outputs = tf.keras.layers.Dense(out_dim, activation='sigmoid')(fl)  # for q learning, linear is very important
    model = tf.keras.models.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam',
                  loss='mse')  # categorical_cross entropy
    return model


if __name__ == '__main__':
    scenario_index = 2
    number_of_states = 20

    states_filename = '.\\records\\states_of_scenario_%d.npz' % scenario_index
    record = np.load(states_filename)
    model_filename = '.\\records\\model_dqn_s%d.h5' % scenario_index

    dqn = tf.keras.models.load_model(model_filename)

    s_batch = record['s']
    N = record['N']
    M = record['M']
    pred = dqn.predict(s_batch)

    [label, elements] = kmeans_clustering(pred, N, M, number_of_states)

    shape = [100, M, 1]
    model = Create_CNN(shape, number_of_states)

    hist = model.fit(s_batch, label, batch_size=256, epochs=100, verbose=0)
    loss = hist.history['loss']

    cluster_model_filename = '.\\records\\model_cluster_s%d_n%d.h5' % (scenario_index, number_of_states)

    model.save(cluster_model_filename)

    filename = '.\\records\\cluster_results_s%d_n%d.mat' % (scenario_index, number_of_states)
    scio.savemat(filename, mdict={'label': label, 'states': s_batch})

    print(loss)
    plt.plot(loss)
    plt.show()
