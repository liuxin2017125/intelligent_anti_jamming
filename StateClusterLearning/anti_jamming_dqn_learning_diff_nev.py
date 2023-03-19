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
    [node0, node1, jammer, shape] = createScenario(env, scenario_index)  # create anti-jamming scenario

    # add a sensor and an agent
    agent = AgentDQN(shape, env.num_of_channels, 0.8, 0.5)

    node0.addAgent(agent)

    watcher = Sensor(env)  # add an observer
    watcher.setTWL(100)
    watcher.setEnablePlot(False)

    # start the engine

    simu_times = 400000

    watchPoints = [100, round(simu_times * 0.4), round(simu_times * 0.85), round(simu_times * 0.95)]
    waterfallList = []
    agent.setExploration(20 / simu_times)
    r = np.zeros([simu_times])

    logout.info('start simulation....')
    for t in range(0, simu_times):
        env.work(t)
        if t in watchPoints:
            waterfallList.append(watcher.waterfall.copy())
            pass
        if t == watchPoints[2]:
            jammer.setOffset(6)  # change the jammer parameter

    filename = '.\\records\\dqn_learning_diff_env_s%d.mat' % scenario_index
    scio.savemat(filename, mdict={'rewards': np.asarray(node0.reward_records), 'waterfall': np.asarray(waterfallList),
                                  'watchPoints': watchPoints})

    plt.plot(node0.reward_records, '.-')
    plt.show()
