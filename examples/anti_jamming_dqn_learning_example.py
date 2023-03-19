# add a jamming device
import numpy as np
from matplotlib import pyplot as plt

from agent.deeplearning import AgentDQN
from linklayer.linklayer_tdd import LinkLayerTDD, SlotScheme, LinkDirection
from net.simpletrafficnode import SimpleTrafficNode
from net.smartnodes import SmartNode
from phylayer.device import Device
from phylayer.environment import Environment
from phylayer.jammers import SimpleJammer, JamMode
from phylayer.moniter import Sensor
from phylayer.receiver import Receiver
from phylayer.transmitter import Transmitter
from utils.logger import logout
from utils.types import DevParam, Pos
from net.node import connect


def addTDDNode(pos: Pos, scheme, envi: Environment):
    tx = Transmitter(envi)
    rx = Receiver(envi)
    link = LinkLayerTDD(tx, rx, envi)  # for physic simulation only
    link.setSlotScheme(scheme)
    node = SmartNode(pos, envi)
    node.addLink(link)
    return node


def addJammer(env):
    jammer1 = SimpleJammer(env)
    jammer1.setParam(DevParam(100, 1, 0))
    jammer1.setPos(Pos(500, 500))
    jammer1.setSlotDuration(1)
    jammer1.setJammingMode(JamMode.SWEEP, False)


def createScenario(env):
    # allocate slot scheme
    ul_scheme = SlotScheme(10, [0, 3], LinkDirection.UPLINK)
    dl_scheme = SlotScheme(10, [5, 8], LinkDirection.DOWNLINK)

    node0 = addTDDNode(Pos(0, 0), ul_scheme, env)
    node1 = addTDDNode(Pos(1000, 1000), dl_scheme, env)

    node0.setTrafficMode(SimpleTrafficNode.CONT, ul_scheme.duration)
    node1.setTrafficMode(SimpleTrafficNode.CONT, dl_scheme.duration)

    power = 100
    freq = 1
    node0.setParam(DevParam(power, freq, 1), DevParam(0, freq, 1), 0)
    node1.setParam(DevParam(power, freq, 1), DevParam(0, freq, 1), 0)

    # connect nodes
    connect(node0, 0, node1, 0)

    addJammer(env)

    sensor = Sensor(env)
    sensor.setTWL(100)
    node0.addSensor(sensor)
    node0.enableLearning()  # node0 is the master
    node0.showInfo()
    node1.showInfo()

    shape = [100, env.num_of_channels, 1]  # tell agent the input shape

    return [node0, node1, shape]


if __name__ == '__main__':
    scenario_index = 2

    env = Environment(10)
    [node0, node1, shape] = createScenario(env)  # create anti-jamming scenario

    # add a sensor and an agent
    agent = AgentDQN(shape, env.num_of_channels, 0.8, 0.5)
    node0.addAgent(agent)

    # start the engine
    simu_times = 20000
    r = np.zeros([simu_times])
    logout.info('start simulation....')
    for t in range(0, simu_times):
        env.work(t)

    plt.plot(node0.reward_records, '.-')
    plt.show()
