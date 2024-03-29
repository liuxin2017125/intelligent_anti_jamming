# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

from abc import abstractmethod
from enum import Enum

from phylayer.device import Device
from utils.types import Data, Packet, Pos, Addr


# possible state of all link.
class LinkState(Enum):
    IDLE = 0
    WAIT = 1  # waiting for ack
    RECV = 2  # the receiving state
    SENS = 3  # the sensing state
    DELY = 4  # the delay after sending an ack
    SEND = 5  # the sending state
    BKOF = 6  # the state of backing off


# an abstract link class for unifying the function interface and avoiding circular importing
class LinkLayer:
    def __init__(self, tx_dev: Device, rx_dev: Device, env):
        self._rx_dev = rx_dev
        self._tx_dev = tx_dev
        self._env = env
        self._src = Addr(0, 0)  # self addr
        self._dst = Addr(0, 0)  # if connected, there is a dst addr
        self._time_stamp = 0  # time stamp
        self._info_str = ' '
        self._id = -1
        if rx_dev is not None:
            self._rx_dev.setLink(self)
        if tx_dev is not None:
            self._tx_dev.setLink(self)

    # get the info str of a link
    def toStr(self):
        tx_str = 'None'
        rx_str = 'None'
        if self._rx_dev is not None:
            rx_str = self._rx_dev.toStr()

        if self._tx_dev is not None:
            tx_str = self._tx_dev.toStr()

        return '%s  T: %s;  R: %s.' % (self._info_str, tx_str, rx_str)

    # rx and tx device need to be set a pos for channel simulation, but the link doesn't need
    def setDevicePos(self, pos: Pos):
        if self._tx_dev is not None:
            self._tx_dev.setPos(pos)
        if self._rx_dev is not None:
            self._rx_dev.setPos(pos)

    def setSrc(self, src):
        self._src = src

    def setDst(self, dst):
        self._dst = dst

    @abstractmethod
    def getReceiveResult(self):
        pass

    @abstractmethod
    def setNode(self, node):
        pass

    @abstractmethod
    def allowSending(self):
        pass

    @abstractmethod
    def addSendPacket(self, data: Data, dst: Addr):  # send it directly, the real link-layer put it into a buffer first
        pass

    @abstractmethod
    def send(self, packet):
        pass

    @abstractmethod
    def recv(self, packet: Packet):  # receive from the
        pass

    @abstractmethod
    def work(self, time_stamp):
        pass

    @property
    def rx_dev(self):
        return self._rx_dev

    @property
    def tx_dev(self):
        return self._tx_dev

    @property
    def src(self):
        return self._src

    @property
    def dst(self):
        return self._dst

    @property
    def id(self):
        return self._src.port
