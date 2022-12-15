# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.
import math

import numpy as np
from matplotlib import pyplot as plt

from agent.deeplearning import AgentDQN
from linklayer.linklayer_tdd import LinkLayerTDD, SlotScheme, LinkDirection

from net.smartnodes import SmartNode
from phylayer.environment import Environment
from phylayer.jammers import SimpleJammer
from phylayer.moniter import Sensor
from phylayer.receiver import Receiver
from phylayer.transmitter import Transmitter
from linklayer.linklayer_arq import LinkLayerARQ
from net.node import connect
from net.simpletrafficnode import SimpleTrafficNode
from utils.types import Pos, DevParam
from utils.logger import logout


def addTDDNode(pos: Pos, scheme, envi: Environment):
    tx = Transmitter(envi)
    rx = Receiver(envi)
    link = LinkLayerTDD(tx, rx, env)  # for physic simulation only
    link.setSlotScheme(scheme)
    node = SmartNode(pos, env)
    node.addLink(link)
    return node


if __name__ == '__main__':

    env = Environment(10)

    # allocate slot scheme
    ul_scheme = SlotScheme(10, [0, 3], LinkDirection.UPLINK)
    dl_scheme = SlotScheme(10, [5, 8], LinkDirection.UPLINK)

    node0 = addTDDNode(Pos(0, 0), ul_scheme, env)
    node1 = addTDDNode(Pos(100, 100), dl_scheme, env)

    node0.setTrafficMode(SimpleTrafficNode.CONT, ul_scheme.duration)
    node1.setTrafficMode(SimpleTrafficNode.CONT, dl_scheme.duration)

    power = 100
    freq = 1
    node0.setParam(DevParam(power, freq, 1), DevParam(0, freq, 1), 0)
    node1.setParam(DevParam(power, freq, 1), DevParam(0, freq, 1), 0)

    # connect nodes
    connect(node0, 0, node1, 0)

    # add a jamming device
    jammer = SimpleJammer(env)
    jammer.setParam(DevParam(100, 1, 0))
    jammer.setPos(Pos(50, 50))
    jammer.setSlotDuration(10)

    # add a sensor and an agent
    sensor = Sensor(env)
    sensor.setTWL(100)
    shape = [100, env.num_of_channels, 1]
    agent = AgentDQN(shape, env.num_of_channels, 0.8, 0.5)

    node0.addAgentAndSensor(agent, sensor)
    node0.enableLearning()
    # show info
    node0.showInfo()
    node1.showInfo()

    # start the engine
    logout.info('start simulation....')
    simu_times = 8000
    agent.setExploration(11/simu_times)
    r = np.zeros([simu_times])
    for t in range(0, simu_times):
        env.work(t)

    fig, axs = plt.subplots(2)
    fig.suptitle('learning results (1) loss, (2) average reward')
    axs[0].plot(agent.loss_records, '.-')
    axs[1].plot(node0.reward_records, '.-')
    plt.show()
