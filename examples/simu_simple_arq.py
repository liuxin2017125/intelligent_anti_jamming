# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

import math

import numpy as np
from matplotlib import pyplot as plt

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


def addTxRxNode(pos: Pos, envi: Environment):
    tx = Transmitter(envi)
    rx = Receiver(envi)
    link = LinkLayerARQ(tx, rx, env)  # for physic simulation only
    link.setAckWay(True)
    node = SimpleTrafficNode(pos, env)
    node.addLink(link)
    return node


if __name__ == '__main__':

    env = Environment(10)
    node0: SimpleTrafficNode = addTxRxNode(Pos(0, 0), env)
    node1: SimpleTrafficNode = addTxRxNode(Pos(100, 100), env)
    node0.setTrafficMode(SimpleTrafficNode.CONT, 20)
    node1.setTrafficMode(SimpleTrafficNode.NONE, 20)
    power = 100
    ul_freq = 1
    dl_freq = 2  # if ul_freq is equal to the dl_freq, the duplex mode is TDD ,otherwise, it is FDD.
    node0.setParam(DevParam(power, ul_freq, 1), DevParam(0, dl_freq, 1), 0)
    node1.setParam(DevParam(power, dl_freq, 1), DevParam(0, ul_freq, 1), 0)

    # connect nodes
    connect(node0, 0, node1, 0)

    # add a jamming device
    jammer = SimpleJammer(env)
    jammer.setParam(DevParam(100, 1, 0))
    jammer.setPos(Pos(50, 50))
    jammer.setSlotDuration(5)

    # add a sensor device
    sensor = Sensor(env)
    sensor.setTWL(100)
    sensor.setPos(Pos(50,50))

    # show info
    node0.showInfo()
    node1.showInfo()

    # start the engine
    logout.info('start simulation....')
    simu_times = 200
    r0 = np.zeros([simu_times])
    r1 = np.zeros([simu_times])
    for t in range(0, simu_times):
        env.work(t)
        r0[t] = 10*math.log10(env.sense(Pos(50, 50), dl_freq, []))  # sensing one channel
        r1[t] = 10*math.log10(env.sense(Pos(50, 50), ul_freq, [])) # sensing one channel

    fig, axs = plt.subplots(2)
    fig.suptitle('sensing results of uplink and downlink channels')
    axs[0].plot(r0, '.-')
    axs[1].plot(r1, '.-')
    plt.show()
