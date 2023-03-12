# add a jamming device
from linklayer.linklayer_tdd import LinkLayerTDD, SlotScheme, LinkDirection
from net.simpletrafficnode import SimpleTrafficNode
from net.smartnodes import SmartNode
from phylayer.device import Device
from phylayer.environment import Environment
from phylayer.jammers import SimpleJammer, JamMode
from phylayer.moniter import Sensor
from phylayer.receiver import Receiver
from phylayer.transmitter import Transmitter
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
    jammer1.setParam(DevParam(0, 1, 0))
    jammer1.setPos(Pos(500, 500))
    jammer1.setSlotDuration(10)
    jammer1.setJammingMode(JamMode.RAND, False)

    jammer2 = SimpleJammer(env)
    jammer2.setParam(DevParam(100, 1, 0))
    jammer2.setPos(Pos(500, 500))
    jammer2.setSlotDuration(1)
    jammer2.setJammingMode(JamMode.SWEEP, False)
    return [jammer1, jammer2]


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

    # add a jamming device
    addJammer(env)

    sensor = Sensor(env)
    sensor.setTWL(100)
    excluded_dev_list: list[Device] = [node0.getLink(0).tx_dev, node1.getLink(0).tx_dev]
    sensor.setExcludedDevList(excluded_dev_list)

    node0.addSensor(sensor)
    sensor.setEnablePlot(False)

    node0.enableLearning()  # node0 is the master
    node0.showInfo()
    node1.showInfo()

    shape = [100, env.num_of_channels, 1]  # tell agent the input shape

    return [node0, node1, shape]
