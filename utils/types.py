# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

from enum import Enum
import math


class DataStyle(Enum):
    PLD = 0  # data frame
    CTL = 1  # control frame
    ACK = 2  #
    NCK = 3  #
    RTS = 4
    CTS = 5


# user-layer
class Data:
    def __init__(self, style: DataStyle, content, duration):  #
        self._style = style
        self._duration: int = duration
        self._content = content  # for future extension, i.e., ip simulation

    @property
    def duration(self):
        return self._duration

    @property
    def style(self):
        return self._style

    @property
    def content(self):
        return self._content


# link-address
class Addr:
    def __init__(self, node: int, port: int):
        self._node: int = node  # node ID
        self._port: int = port  # index of the link in node

    def set(self, node: int, port: int):
        self._node = node
        self._port = port

    def toStr(self):
        return '(%d,%d)' % (self._node, self.port)

    @property
    def node(self):
        return self._node

    @property
    def port(self):
        return self._port


# link-layer
class Packet:
    def __init__(self, data: Data, src: Addr, dst: Addr, seq, need_ack):  # 类型  持续时间  包序号
        self._data = data
        self._src = src
        self._dst = dst
        self._seq = seq  # 包序号
        self._need_ack = need_ack  # 是否需要ACK确认
        self._send_times = 0  # 发送次数

    def addSendTimes(self):
        self._send_times = self._send_times + 1

    def setAckWay(self, need_ack):
        self._need_ack = need_ack

    def toStr(self):
        style = self._data.style
        duration = self._data.duration
        src = self._src.node
        dst = self._dst.node
        return 'Packet<node%d_%d==>node%d_%d (%s) L=%d seq=%d>' % (
            self._src.node, self._src.port,self._dst.node, self._dst.port, style.name, duration, self._seq)

    @property
    def data(self):
        return self._data

    @property
    def dst(self):
        return self._dst

    @property
    def src(self):
        return self._src

    @property
    def send_times(self):
        return self._send_times

    @property
    def need_ack(self):
        return self._need_ack

    @property
    def seq(self):
        return self._seq


# communication parameter
class DevParam:
    def __init__(self, power, freq, band):
        self._power = float(power)
        self._freq = int(freq)
        self._band = int(band)

    def setFreq(self, freq):
        self._freq = freq

    def toStr(self):
        return '(%d,%d,%d)' % (self._power, self._freq, self._band)

    @property
    def power(self):
        return self._power

    @property
    def freq(self):
        return self._freq

    @property
    def band(self):
        return self._band


# physic-layer
class SigInfo:
    def __init__(self, param: DevParam, packet: Packet):  # 频率，功率和方向
        self._param = param
        self._packet = packet

    @property
    def param(self):
        return self._param

    @property
    def packet(self):
        return self._packet


class Pos:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def toStr(self):
        return '(%d, %d)' % (self.x, self.y)


class MsgName(Enum):
    PHY_DEMOD_FAILED = 0
    PHY_DEMOD_SUCCESS = 1


# for cross-layer communication
class CLMsg:
    def __init__(self, name: MsgName, content):
        self._name = name
        self._content = content

    @property
    def name(self):
        return self._name

    @property
    def content(self):
        return self._content
