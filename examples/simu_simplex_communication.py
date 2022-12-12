# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.
import numpy as np
from matplotlib import pyplot as plt

from phylayer.receiver import Receiver
from phylayer.transmitter import Transmitter
from phylayer.environment import Environment
from linklayer.linklayerbase import LinkLayerBase
from net.node import connect
from net.simpletrafficnode import SimpleTrafficNode
from utils.types import Pos, DevParam, Data, DataStyle
from utils.logger import logout


def addTxNode(pos: Pos, envi: Environment):
    tx = Transmitter(envi)
    link = LinkLayerBase(tx, None, env)  # for physic simulation only
    node = SimpleTrafficNode(pos, env)
    node.addLink(link)
    return node


def addRxNode(pos: Pos, envi: Environment):
    rx = Receiver(envi)
    link = LinkLayerBase(None, rx, env)  # for physic simulation only
    node = SimpleTrafficNode(pos, env)
    node.addLink(link)
    return node


if __name__ == '__main__':

    env = Environment(10)
    tx_node = addTxNode(Pos(0, 0), env)
    rx_node = addRxNode(Pos(100, 100), env)

    # set parameters
    txParam = DevParam(100, 2, 1)
    rxParam = DevParam(0, 2, 1)
    tx_node.setParam(txParam, None, 0)
    rx_node.setParam(None, rxParam, 0)

    # connect nodes
    connect(tx_node, 0, rx_node, 0)

    # show info
    tx_node.showInfo()
    rx_node.showInfo()

    # create a data frame
    data = Data(DataStyle.PLD, 'hello', 10)

    # start the engine
    logout.info('start simulation....')
    simu_times = 100
    r = np.zeros([simu_times])
    for t in range(0, simu_times):
        env.work(1000 + t)
        r[t] = env.sense(Pos(300, 300), txParam.freq)  # sensing one channel

    plt.plot(r, '.-')
    plt.show()
