# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.
import math

import numpy as np
from matplotlib import pyplot as plt

from StateClusterLearning.init_anti_jamming_scenario import createScenario
from agent.deeplearning import AgentDQN
from phylayer.environment import Environment
from phylayer.moniter import Sensor
from utils.logger import logout
import scipy.io as scio

if __name__ == '__main__':
    scenario_index = 2

    env = Environment(10)
    [node0, node1, shape] = createScenario(env, scenario_index)  # create anti-jamming scenario

    # add a sensor and an agent
    agent = AgentDQN(shape, env.num_of_channels, 0.8, 0.5)
    node0.addAgent(agent)

    watcher = Sensor(env)  # add an observer
    watcher.setTWL(100)
    watcher.setEnablePlot(False)

    # start the engine

    if scenario_index == 1:
        simu_times = 10000
    else:
        simu_times = 300000

    watchPoints = [100, round(simu_times * 0.4), round(simu_times * 0.9)]
    waterfallList = []
    agent.setExploration(20 / simu_times)
    r = np.zeros([simu_times])

    logout.info('start simulation....')
    for t in range(0, simu_times):
        env.work(t)
        if t in watchPoints:
            waterfallList.append(watcher.waterfall.copy())
            pass

    filename = '.\\records\\dqn_learning_s%d.mat' % scenario_index
    scio.savemat(filename, mdict={'rewards': np.asarray(node0.reward_records), 'waterfall': np.asarray(waterfallList)})

    filename = '.\\records\\states_of_scenario_%d.npz' % scenario_index
    agent.saveRecord(filename)

    filename = '.\\records\\model_dqn_s%d.h5' % scenario_index
    agent.saveModel(filename)

    plt.plot(node0.reward_records, '.-')
    plt.show()
