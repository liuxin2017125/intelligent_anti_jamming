# It doesn't have any sending and receiving buffer and the coping process of link-layer, hence it is always used by
# non-communication nodes, such as jamming node, as a bridge for tx and rx devices.
from linklayer.linklayer import LinkLayer
from net.node import Node
from phylayer.device import DevState,Device
from utils.types import Addr, Data, Packet
from utils.logger import logout


class LinkLayerBase(LinkLayer):
    def __init__(self, tx_dev: Device, rx_dev: Device, env):
        LinkLayer.__init__(self, tx_dev, rx_dev, env)
        self._node: Node = None

    def allowSending(self):
        if self._tx_dev is None:
            return False
        else:
            return self._tx_dev.state == DevState.IDLE

    def addSendPacket(self, data: Data, dst: Addr):  # send it directly, the real link-layer put it into a buffer first
        packet = Packet(data, self._src, dst, 0, False)
        self.send(packet)
        return

    def send(self, packet):
        logout.info('Send %s', packet.toStr())
        self._tx_dev.send(packet)  # hand over to the physic device

    def recv(self, packet):  # receive from the
        logout.info('TS_%d Link%d Recv %s', self._time_stamp, self._id, packet.toStr())
        # show the receiving results

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        if self._tx_dev is not None:
            self._tx_dev.work(time_stamp)
        if self._rx_dev is not None:
            self._rx_dev.work(time_stamp)

    def setNode(self, node: Node):
        self._node = node
        if self._tx_dev is not None:
            self._tx_dev.setNode(node)
        if self._rx_dev  is not None:
            self._rx_dev.setNode(node)

