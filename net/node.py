# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

from abc import abstractmethod
from linklayer.linklayer import LinkLayer
from utils.types import Pos, Packet, Addr, DevParam, Data, DataStyle, Msg, MsgName
from utils.logger import logout


# base class of node
class Node:
    def __init__(self, pos: Pos, env):
        self._time_stamp = -1
        self._pos = pos
        self._env = env
        self._id = env.registerNode(self)
        self._msg_list: list[Msg] = []
        self._link_list: list[LinkLayer] = []  # a node may contain several links, i.e., switcher, router
        self._reward = 0.0  # reward of communication
        self._learning = False

    def enableLearning(self):
        self._learning = True

    def addLink(self, link: LinkLayer):
        port = len(self._link_list)
        link.setSrc(Addr(self._id, port))
        link.setDevicePos(self._pos)
        link.setNode(self)
        self._link_list.append(link)

    def getLink(self, port: int):
        if 0 <= port < len(self._link_list):
            return self._link_list[port]
        else:
            return None

    def showInfo(self):
        print('Node_%d Pos%s' % (self._id, self._pos.toStr()))
        for i in range(0, len(self._link_list)):
            print('  ', self._link_list[i].toStr())

    def sendTo(self, data: Data, dst: Addr, port):
        if port >= len(self._link_list):
            logout.error('Failed as node_%d does not have port_%d', self._id, port)
            return
        link = self._link_list[port]
        link.addSendPacket(data, dst)

    def setParam(self, tx_param: DevParam, rx_param: DevParam, port):
        if port >= len(self._link_list):
            logout.error('Failed as node_%d does not have port_%d', self._id, port)
            return
        if tx_param is not None:
            self._link_list[port].tx_dev.setParam(tx_param)

        if rx_param is not None:
            self._link_list[port].rx_dev.setParam(rx_param)

    def addMsg(self, msg: Msg):
        self._msg_list.append(msg)

    def copeMsg(self, msg: Msg):
        if msg.name == MsgName.SET_TRX_FREQ:  # TDD
            freq = int(msg.content)
            port = msg.dst.port
            self.getLink(port).rx_dev.param.setFreq(freq)
            self.getLink(port).tx_dev.param.setFreq(freq)

    def doAction(self, port):
        pass

    def copingMsgLoop(self):
        if len(self._msg_list) == 0:
            return
        msg = self._msg_list[0]
        self.copeMsg(msg)
        self._msg_list.pop(0)  # delete after coping

    @abstractmethod
    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self.copingMsgLoop()  # cope msg first and then drive its links
        for i in range(0, len(self._link_list)):
            self._link_list[i].work(time_stamp)

    @abstractmethod
    def recv(self, data: Data):
        pass

    @property
    def id(self):
        return self._id

    @property
    def pos(self):
        return self._pos


def connect(node1: Node, port1, node2: Node, port2):
    link1 = node1.getLink(port1)
    link2 = node2.getLink(port2)

    link1.setDst(Addr(node2.id, port2))
    link2.setDst(Addr(node1.id, port1))
