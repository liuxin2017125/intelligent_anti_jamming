import numpy as np
from numpy import mean

from phylayer.device import Device, DevType, DevState
from phylayer.devicebase import DeviceBase
from utils.logger import logout
from utils.timer import Timer

# receiver
from utils.types import CLMsg, MsgName


class Receiver(DeviceBase):
    def __init__(self, env):
        DeviceBase.__init__(self, DevType.RX, env)
        self._rx_timer = Timer('Recv')  # timer for record the snr during the duration of a packet.
        self._cur_sig = []
        self._snr_list = []  #
        self._record = []
        self._average_r = 0
        self._snr_th = 6  # the snr requirement that can be changed according to your scenario
        self._req_valid_rate = 0.7  # the required rate that snr is larger than the snr_th

    def demodSucceed(self):  #
        valid_times = 0
        for n in range(0, len(self._snr_list)):
            if self._snr_list[n] > self._snr_th:  #
                valid_times = valid_times + 1
        if valid_times / self._cur_sig.packet.data.duration >= self._req_valid_rate:  # 70%的数据正确就能解码成功
            return True
        else:
            return False

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self._rx_timer.work()
        if self._rx_timer.timeout:
            self._state = DevState.IDLE
            self._rx_timer.reset()
            if self.demodSucceed():
                msg = CLMsg(MsgName.PHY_DEMOD_SUCCESS, None)
                logout.info('TS_%d Dev%d demod(mean_snr=%2.2f) is OK', self._time_stamp, self._id, mean(self._snr_list))
                if self._link is not None:
                    self._link.recv(self._cur_sig.packet)

                    # inform the upper level to cope the packet. Call the function directly for quick response,
                    # but it will increase the call depth, which is need to be avoided.
            else:
                msg = CLMsg(MsgName.PHY_DEMOD_FAILED, None)
                logout.info('TS_%d Dev%d demod(mean_snr=%2.2f) is FAILED', self._time_stamp, self._id, mean(self._snr_list))

            self.sendMsgToNode(msg)

            self._snr_list = []  # clear snr list

        if self._state == DevState.RECV:  # continuously calculate the snr during the receiving procedure
            snr = self._env.getRxSnr(self, self._cur_sig)
            snr_db = 10 * np.log10(snr)
            self._snr_list.append(snr_db)

    def recv(self, sig):  # this function is loaded by env
        self._state = DevState.RECV
        duration = sig.packet.data.duration
        self._cur_sig = sig
        self._rx_timer.setDuration(duration)
        self._rx_timer.start()
