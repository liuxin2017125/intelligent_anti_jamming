# Node which can generate traffic data
import numpy as np

from net.node import Node
from utils.types import Pos, Data, DataStyle
from utils.logger import logout


class SimpleTrafficNode(Node):
    RAND = 0  # random
    CONT = 1  # continuous
    NONE = 2  # no traffic data

    def __init__(self, pos: Pos, env):
        Node.__init__(self, pos, env)
        self._traffic_mod = SimpleTrafficNode.CONT
        self._traffic_len = 10
        self._rate = 0.01

    def recv(self, data: Data):
        logout.info('Node rec')

    def setTrafficMode(self, tf_mode, tf_len):
        self._traffic_mod = tf_mode
        self._traffic_len = tf_len

    def work(self, time_stamp):
        self.generateTraffic(0)  # just simulate one port auto-traffic
        Node.work(self, time_stamp)

    def generateTraffic(self, port):
        if self._traffic_mod == SimpleTrafficNode.NONE:
            return

        link = self.getLink(port)
        if link is None:
            return

        if self._traffic_mod == SimpleTrafficNode.CONT:
            if link.allowSending() is True:
                data = Data(DataStyle.PLD, None, self._traffic_len)
                link.addSendPacket(data, link.dst)

        if self._traffic_mod == SimpleTrafficNode.RAND:
            seed = np.random.rand()
            if seed<self._rate and link.allowSending():
                data = Data(DataStyle.PLD, None, self._traffic_len)
                link.addSendPacket(data, link.dst)
