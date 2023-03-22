# simulate the basic csma ca procedure
import numpy as np

from linklayer.linklayer import LinkState
from linklayer.linklayer_arq import LinkLayerARQ
from phylayer.device import Device
from phylayer.environment import Environment
from utils.types import DataStyle


class LinkLayerCSMA(LinkLayerARQ):
    SLOT = 2  # assume one unit time is 10us
    SIFS = 1  # 10us
    DIFS = SIFS + SLOT * 2  # 50us

    def __init__(self, tx_dev: Device, rx_dev: Device, env: Environment):
        LinkLayerARQ.__init__(self, tx_dev, rx_dev, env)
        self._back_off_time = 0
        self._back_off_index = 1

    def channelBusy(self):
        pos = self._node.pos
        freq = self._rx_dev.param.freq
        r = 10*np.log10(self._env.sense(pos, freq, []))
        return r > -77  # 大于底噪(-80） 3个dB 表示有信号存在

    def enterState(self, state):
        self._state = state
        self._tx_timer.reset()  # 每次进入新状态，都要将定时器复位一次
        print('TS %d: link_%s ==>' % (self._time_stamp, self._id), self._state)
        if self._state == LinkState.BKOF:  # 有些状态需要做一些特定处理
            self.startBackOff()

    def startBackOff(self):
        # 初始化退避的参数，有两种情况进入退避，一个是ACK超时，一个是发送前感知为忙
        back_off_base = (2 ** self._back_off_index + 2)
        back_off_slot = np.random.randint(0, back_off_base)
        self._back_off_time = back_off_slot * self.SLOT  # 得到退避时间
        print('TS %d: link_%d i=%d bt=%d' % (self._time_stamp, self._id, self._back_off_index, self._back_off_time))

        self._back_off_index = self._back_off_index + 1  # 每进入一次，退避窗都要增加
        if self._back_off_index > 6:  # 超出了最大退避的极限
            self._tx_buffer.pop(0)  # 放弃这个包
            self.enterState(LinkState.IDLE)

    def sendLoop(self):
        # 首先处理Time out 事件
        if self._tx_timer.timeout:  # 计数器超时，需要了解一下计数器任务，根据任务来确定下一步的状态切
            print('TS %d: link_%d time out' % (self._time_stamp, self._id), self._tx_timer.param)
            self.enterState(self._tx_timer.param)
            self._tx_timer.reset()

        # 其次判断是否有数据发送
        have_data = (len(self._tx_buffer) > 0)  # 检查队列是否有数据
        if not have_data:
            return  # 没有发送数据，什么都不用处理

        # 最后才是 CSMA-CA状态机
        if self._state == LinkState.IDLE:  # 空闲状态
            self._back_off_index = 1  # 退避窗从最小开始
            packet = self._tx_buffer[0]  # 取过第一包
            if packet.data.style == DataStyle.PLD:
                duration = self.DIFS  # 负载需要等DIFS时间
                # 所有计时器的启动都应该在配置状态之后
                self.enterState(LinkState.SENS)  # 注意此时会理解切换到 SENS状态
                self._tx_timer.setDuration(duration - 1)  # 设置一个等待计时器，
                self._tx_timer.setParam(LinkState.SEND)  # 超时后应该进入的状态
                self._tx_timer.start()

            else:
                duration = self.SIFS  # ACK 需要等 SIFS时间, 实际上由于接收切换到发送，还会暂用一个周期，这里就先不处理了
                # 所有计时器的启动都应该在配置状态之后
                self.enterState(LinkState.DELY)  # 注意此时会理解切换到 SENS状态
                self._tx_timer.setDuration(duration - 1)  # 设置一个等待计时器，
                self._tx_timer.setParam(LinkState.SEND)  # 超时后应该进入的状态
                self._tx_timer.start()

        if self._state == LinkState.SENS:
            if self.channelBusy():
                self.enterState(LinkState.BKOF)  # 遇到忙就要进入退避状态

        if self._state == LinkState.BKOF:  # 退避的计时通过自身完成
            if not self.channelBusy():  # 空闲时才计时，如果忙就不退避
                self._back_off_time = self._back_off_time - 1
                if self._back_off_time <= 0:
                    self.enterState(LinkState.SENS)  # back off 时间到了，就要重新感知信道，准备发送
                    self._tx_timer.setDuration(self.DIFS - 1)  # 设置一个等待计时器，
                    self._tx_timer.setParam(LinkState.SEND)  # 超时后应该进入的状态
                    self._tx_timer.start()

        if self._state == LinkState.SEND:
            print('TS %d: link_%d enter SEND ' % (self._time_stamp, self._id))
            packet = self._tx_buffer[0]  # 取过第一包
            self.send(packet)  # 发送该包
            if packet.need_ack:
                wait_time = packet.data.duration + self.SIFS + self.ACK_DURATION + self.WAIT_ACK_TIME
                self.enterState(LinkState.WAIT)
                self._tx_timer.setDuration(wait_time)  # 包的长度加一个保护时间等待ACK, -2是启动占一个周期，检测到time out 占据了一个周期
                self._tx_timer.setParam(LinkState.BKOF)  # 超时没有收到ACK，说明数据包冲突，进入到退避状态
                self._tx_timer.start()
            else:
                self.enterState(LinkState.IDLE)
                self._tx_buffer.pop(0)