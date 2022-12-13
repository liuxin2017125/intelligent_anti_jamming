# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.
import math
import logging
from phylayer.device import Device, DevType
from linklayer.linklayer import LinkLayer
from net.node import Node
from utils.types import Addr, Pos, SigInfo, Msg
from utils.logger import logout


def square_distance(a: Pos, b: Pos):
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def distance(a: Pos, b: Pos):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


def channelSimulation(a: Pos, b: Pos):
    d2 = square_distance(a, b)
    if d2 > 1:
        L = 1.0 / d2  # the simplest channel simulation  model, you can change it based on your scenario
    else:
        L = 1.0  # avoid overflow
    return L


class Environment:
    INFINITESIMAL = 1e-100

    def __init__(self, num_of_channels):
        # node contains links, link  contains tx and rx
        self._device_list: list[Device] = []  # record all device
        self._monitor_list: list[Device] = []  # which can demodulate all kings of signal if snr is enough
        self._link_list: list[LinkLayer] = []  # record all links
        self._node_list: list[Node] = []  # record all nodes

        self._noise = 1e-8  # noise power spectral density -80dbm, it can be changed based on your scenario
        self._device_num = 0
        self._num_of_channels = num_of_channels

    def registerDevice(self, device: Device):
        self._device_list.append(device)
        if device.type == DevType.MON:
            self._monitor_list.append(device)
        return len(self._device_list) - 1  # device ID

    def registerLink(self, link: LinkLayer):
        self._link_list.append(link)
        return len(self._link_list) - 1  # link ID

    def registerNode(self, node: Node):
        self._node_list.append(node)
        return len(self._node_list) - 1  # node ID

    def getDstReceiver(self, dst: Addr):
        receiver = None
        node_index = dst.node
        link_index = dst.port
        if 0 <= node_index < len(self._node_list):
            node = self._node_list[node_index]
            link = node.getLink(link_index)
            if link is not None:
                receiver = link.rx_dev
        return receiver

    def getScrTransmitter(self, src: Addr):
        transmitter = None
        node_index = src.node
        link_index = src.port
        if 0 <= node_index < len(self._node_list):
            node = self._node_list[node_index]
            link = node.getLink(link_index)
            if link is not None:
                transmitter = link.tx_dev
        return transmitter

    # a supper link for node to node transmission of msg
    # this kind of transmission will be instead by a real transmission in the future.
    def msgSwitch(self, msg: Msg):
        nid = msg.dst.node
        self._node_list[nid].copeMsg(msg)

    # a virtual link for device to device transmission of sig information
    # this is necessary as we won't simulate the synchronization of phy-layer
    # the receiver can only get the content of the sig when snr meets the requirement
    def sigSwitch(self, sig):
        # logout.info('Switch %s', sig.packet.toStr())
        receiver: Device = self.getDstReceiver(sig.packet.dst)  # legitimate receiver
        if receiver is not None:
            receiver.recv(sig)
        else:
            logging.warning('Wrong addr which can not be switched')
            return
        # monitoring equipment can receive all signals without considering the link relationship
        if len(self._monitor_list) > 0:
            for i in range(0, len(self._monitor_list)):
                receiver: Device = self._monitor_list[i]
                receiver.recv(sig)

    def getRxSnr(self, rx: Device, sig: SigInfo):
        freq = sig.param.freq  # the freq of the signal
        if rx.param.freq != freq:  # the receiver's freq is not the same as the signal
            return self.INFINITESIMAL  # return a infinitesimal value to avoid error as calculate dB

        tx = self.getScrTransmitter(sig.packet.src)
        if tx is None:  # it is a wrong _state, just add it for possible bug.
            logout.error('no transmitter during calculate snr for a sig')
            return self.INFINITESIMAL  # return a infinitesimal value to avoid error as calculate dB

        L = channelSimulation(tx.pos, rx.pos)
        P = tx.getOutputPower(freq)  # get the power of the tx on this freq
        rs = P * L
        ri = self._noise  # the init value of interference
        for i in range(0, len(self._device_list)):
            dev = self._device_list[i]
            if dev.type is not DevType.TX or dev.type is not DevType.JAM:  # receiver won't make any interference
                continue
            if dev.id == tx.id:  # exclude self
                continue
            P = dev.getOutputPower(freq)
            if P > 0.0:
                L = channelSimulation(rx.pos, dev.pos)
                ri = ri + P * L

        if ri > 0:
            snr = rs / ri
        else:
            snr = 1000  # no interference, set a bigger value for avoiding infinite
        return snr

    def work(self, time_stamp):
        for i in range(0, len(self._node_list)):
            self._node_list[i].work(time_stamp)

    def sense(self, pos, freq):
        r = self._noise  # -80dbm
        for i in range(0, len(self._device_list)):
            dev = self._device_list[i]
            if dev.type == DevType.RX or dev.type == DevType.SEN:  # receivers
                continue
            P = dev.getOutputPower(freq)  #
            if P > 0.0:
                L = channelSimulation(dev.pos, pos)  # pos is the position of the sensing point
                r = r + P * L
        return r

    @property
    def num_of_channels(self):
        return self._num_of_channels

    @property
    def noise(self):
        return self._noise
