from enum import Enum

from linklayer.linklayer import LinkState
from linklayer.linklayerbase import LinkLayerBase
from phylayer.device import Device, DevState
from utils.types import Data, Packet, DataStyle
from utils.logger import logout
from utils.timer import Timer


class LinkLayerARQ(LinkLayerBase):
    WAIT_ACK_TIME = 10
    MAX_SEND_TIMES = 5  # the maximum times of resending
    ACK_DURATION = 2  # the time duration of ack packet
    MAX_BUF_LEN = 10  # the size of sending and receiving buffer

    def getReceiveResult(self):
        pass

    def __init__(self, tx_dev: Device, rx_dev: Device, env):
        LinkLayerBase.__init__(self, tx_dev, rx_dev, env)

        self._tx_buffer = []  # sending buffer
        self._rx_buffer = []  # receiving buffer

        self._state = LinkState.IDLE
        self._tx_counter = 0
        self._rx_counter = 0

        self._tx_timer = Timer('Link%d' % self._id)  # counter for link-layer process

        self._cur_rx_packet = []
        self._seq = 0

        self._need_ack = False
        self._guard_time = 2

    def setAckWay(self, need_ack):
        self._need_ack = need_ack

    def allowSending(self):
        return len(self._tx_buffer) <= self.MAX_BUF_LEN - 5  # 5 is the guard length

    def addSendPacket(self, data, dst):
        need_ack = self._need_ack
        if data.style != DataStyle.PLD:  # only needs to send ACK back for payload data
            need_ack = False
        packet = Packet(data, self._src, dst, self._seq, need_ack)

        if data.style == DataStyle.ACK:  # ACK has the highest priority
            self._tx_buffer.insert(0, packet)  # fix me!!!! this is not safe when it can't be sent immediately.
        else:
            self._tx_buffer.append(packet)  # whereas, other packets are added in order.

        self._seq = self._seq + 1
        if self._seq == 256:
            self._seq = 0

    def enterState(self, state):
        logout.info('TS_%d %s enter LinkState %s', self._time_stamp, self._info_str, state.name)
        self._state = state
        self._tx_timer.reset()  # timer need to be reset during enter a new state.

    def recv(self, packet: Packet):
        logout.info('TS_%d %s recv %s', self._time_stamp, self._info_str, packet.toStr())
        # show the receiving results

        if packet.data.style == DataStyle.PLD:
            if self._need_ack:
                seq = packet.seq
                data = Data(DataStyle.ACK, seq, self.ACK_DURATION)  # ACK packet
                self.addSendPacket(data, packet.src)  # push into sending buffer

            # notice the upper level to cope recv event
            # only the receiving of PLD is considered by upper level

        if packet.data.style == DataStyle.ACK:  # if ACK is received
            seq = packet.data.content  # get the packet seq
            buf_len = len(self._tx_buffer)
            for n in range(0, buf_len):
                if self._tx_buffer[n].seq == seq:
                    self._tx_buffer.pop(n)  # deleted the acknowledged packet
                    break
        self.enterState(LinkState.IDLE)  # change state to IDLE after finishing coping a received packet.

    def send(self, packet: Packet):
        packet.addSendTimes()  # increase the sending time counts
        logout.info('TS_%d %s send %s', self._time_stamp, self._info_str, packet.toStr())
        self.tx_dev.send(packet)  # hand over to the device

    def sendLoop(self):  # the key process
        # cope the timeout events first
        if self._tx_timer.timeout:
            logout.info('TS_%d %s time out' % (self._time_stamp, self._info_str))
            self.enterState(self._tx_timer.param)

        vacant = (len(self._tx_buffer) == 0)  # determine whether buffer is not vacant
        if vacant:
            return  # do nothing

        if self._tx_dev.state is not DevState.IDLE or self._state is not LinkState.IDLE:
            return  # link and tx_dev should be IDLE

        # now we can seed data
        packet = self._tx_buffer[0]
        self.send(packet)  # get the first packet and send

        # the simplest ARQ process, in which new packet can only be sent after the acknowledgement of its previous
        # packet.
        if packet.need_ack:
            duration = packet.data.duration + self.WAIT_ACK_TIME + self.ACK_DURATION
            self.enterState(LinkState.WAIT)  # enter wait state
            self._tx_timer.setDuration(duration - 1)
            self._tx_timer.setParam(LinkState.IDLE)  # enter IDLE state if time out.
            self._tx_timer.start()

            # delete the packets that exceed the maximum number of retries.
            if packet.send_times >= self.MAX_SEND_TIMES:
                self._tx_buffer.pop(0)

        else:
            self._tx_buffer.pop(0)  # delete after sending
            duration = packet.data.duration + self._guard_time  # the safe interval between two times of sending.
            self.enterState(LinkState.WAIT)  # waiting for finishing transmission
            self._tx_timer.setDuration(duration - 1)
            self._tx_timer.setParam(LinkState.IDLE)  # state should be IDLE after timeout
            self._tx_timer.start()  #

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self.sendLoop()
        self._tx_timer.work()
        return
