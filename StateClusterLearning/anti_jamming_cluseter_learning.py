# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.
import math

import numpy as np
from matplotlib import pyplot as plt

from StateClusterLearning.init_anti_jamming_scenario import  createScenario
from agent.clusterlearning import AgentCL
from phylayer.environment import Environment
from phylayer.moniter import Sensor
from utils.logger import logout
import scipy.io as scio

if __name__ == '__main__':
    scenario_index = 1
    number_of_states = 5
    env = Environment(10)
    [node0, node1, jammer1,shape] = createScenario(env, scenario_index)

    # add a sensor and an agent
    cl_model_file = '.\\records\\model_cluster_s%d_n%d.h5' % (scenario_index, number_of_states)
    agent = AgentCL(cl_model_file, env.num_of_channels, 0.8, 0.5)
    node0.addAgent(agent)

    watcher = Sensor(env)  # add an observer
    watcher.setTWL(100)
    watcher.setEnablePlot(False)
    # start the engine
    logout.info('start simulation....')
    simu_times = 20000
    watchPoints = [100, round(simu_times * 0.4), round(simu_times * 0.8)]
    waterfallList = []
    agent.setExploration(20 / simu_times)
    r = np.zeros([simu_times])
    for t in range(0, simu_times):
        env.work(t)
        if t in watchPoints:
            waterfallList.append(watcher.waterfall.copy())

    filename = '.\\records\\cluster_learning_s%d_n%d.mat' % (scenario_index, number_of_states)
    scio.savemat(filename, mdict={'rewards': np.asarray(node0.reward_records), 'waterfall': np.asarray(waterfallList),
                                  'watchPoints': watchPoints})

    plt.plot(node0.reward_records, '.-')
    plt.show()
