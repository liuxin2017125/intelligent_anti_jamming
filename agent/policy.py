import numpy as np


def getPolicy(value, ref):
    exp_value = np.exp(value / ref)
    scale = sum(exp_value)
    policy = exp_value / scale
    return policy


def executePolicy(policy):
    N = len(policy)
    x = np.random.rand()
    for n in range(0, N):
        x = x - policy[n]
        if x <= 0:
            a = n
            break

    return a
