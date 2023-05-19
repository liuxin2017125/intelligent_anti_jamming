# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

from abc import abstractmethod
from enum import Enum
from utils.types import DevParam, Pos


# type of physical device
class DevType(Enum):
    TX = 1  # simple transmitter
    RX = 2  # simple receiver
    JAM = 3  # random jammer
    SEN = 4  # sensor
    MON = 5  # monitor device which can demodulate dst signal
    MRX = 6  # multi-channel receiver


# _state of device
class DevState(Enum):
    IDLE = 0
    SEND = 1
    RECV = 2
    TRAK = 3  #
    LOST = 4  # lost the objective device


# abstract class of device
class Device:
    def __init__(self, dtype: DevType, env):  # unspecified type of env is for avoiding circular reference.

        self._type = dtype
        self._output_power = 0
        self._recv_power = 0
        self._state = DevState.IDLE
        self._env = env
        self._id = env.registerDevice(self)
        self._param = DevParam(0, 0, 0)
        self._pos = Pos(0, 0)  # it will be updated after allocated to a link
        self._time_stamp = 0
        self._node = None
        self._radiation = False
        self._freq_list = None

    @abstractmethod
    def setLink(self, link):  # unspecified type of link is for avoiding circular reference.
        pass

    @abstractmethod
    def setNode(self, node):  # unspecified type of link is for avoiding circular reference.
        pass

    def setPos(self, pos):
        self._pos = pos

    def getOutputPower(self, freq):
        if freq >= self._env.num_of_channels:  # beyond the number of channel of the environment
            return 0.0

        df = abs(self._param.freq - freq)
        if df <= self._param.band / 2:
            return self._output_power
        else:
            return 0.0

    def setParam(self, param):
        self._param = param

    def toStr(self):  # show some key info
        return 'Dev_%d (%s)' % (self._id, self._type.name)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def state(self):
        return self._state

    @property
    def param(self):
        return self._param

    @property
    def pos(self):
        return self._pos

    @property
    def node(self):
        return self._node

    @property
    def radiation(self):
        return self._radiation
    @property
    def freq_list(self):
        return self._freq_list