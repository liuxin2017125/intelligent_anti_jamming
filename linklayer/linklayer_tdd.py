from enum import Enum

from linklayer.linklayerbase import LinkLayerBase
from phylayer.device import Device
from utils.types import Packet
from utils.logger import logout


# the uplink drives the downlink
class LinkDirection(Enum):
    UPLINK = 0
    DOWNLINK = 1


class SlotScheme:
    def __init__(self, period, range, direction: LinkDirection):
        self._period = period  # the total time of an uplink slot and downlink slot
        self._range = range  # the start time of sending
        self._direction = direction  # link direction
        self._duration = range[1] - range[0] + 1  # duration of slot

    @property
    def period(self):
        return self._period

    @property
    def start_time(self):
        return self._range[0]

    @property
    def duration(self):
        return self._duration

    @property
    def direction(self):
        return self._direction


# TDD
class LinkLayerTDD(LinkLayerBase):
    MAX_BUF_LEN = 10

    def __init__(self, tx_dev: Device, rx_dev: Device, env):
        LinkLayerBase.__init__(self, tx_dev, rx_dev, env)
        self._tx_buffer = []  # sending buffer
        self._rx_buffer = []  # receiving buffer
        self._cur_rx_packet = None

        self._slot_scheme: SlotScheme = None

        self._receive_succeed = False
        self._seq = 0

    def getReceiveResult(self):
        return self._receive_succeed

    def allowSending(self):
        return len(self._tx_buffer) <= self.MAX_BUF_LEN

    def setSlotScheme(self, slot_scheme: SlotScheme):
        self._slot_scheme = slot_scheme

    def addSendPacket(self, data, dst):
        if data.duration > self._slot_scheme.duration:
            logout.warning('The packet length exceeds the time slot length')
            return
        packet = Packet(data, self._src, dst, self._seq, False)
        self._seq = (self._seq + 1) % 256
        self._tx_buffer.append(packet)  #

    def recv(self, packet: Packet):
        logout.info('TS_%d %s recv %s', self._time_stamp, self._info_str, packet.toStr())
        # show the receiving results
        self._receive_succeed = True

    def send(self, packet: Packet):
        logout.info('TS_%d %s send %s', self._time_stamp, self._info_str, packet.toStr())
        self.tx_dev.send(packet)  # hand over to the device

    def sendLoop(self):
        if len(self._tx_buffer) == 0:
            return

        if self._slot_scheme is None:
            logout.warning('%s,slot scheme is not allocated', self._info_str)
            return

        time_in_slot = self._time_stamp % self._slot_scheme.period

        if time_in_slot == 0:  # start of the whole slot
            self._receive_succeed = False  # reset the receiving sign
            self._node.doAction(self.src.port)

        if time_in_slot == self._slot_scheme.start_time:  # the start of sending time
            if self._slot_scheme.direction == LinkDirection.UPLINK:  # uplink can initiate a transmission
                sendingEnabled = True
            else:  # downlink can only send packet after receive an uplink packet
                if self._receive_succeed:
                    sendingEnabled = True
                else:
                    sendingEnabled = False
            if sendingEnabled:
                packet = self._tx_buffer[0]
                self.send(packet)
                self._tx_buffer.pop(0)

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self.sendLoop()
        return
