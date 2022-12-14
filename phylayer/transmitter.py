from phylayer.device import Device, DevType, DevState
from phylayer.devicebase import DeviceBase
from utils.types import SigInfo
from utils.timer import Timer


class Transmitter(DeviceBase):
    def __init__(self, env):
        DeviceBase.__init__(self, DevType['TX'], env)
        self._tx_timer = Timer('Tran')  # timer for sending signal
        self._radiation = True

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self._tx_timer.work()
        if self._tx_timer.timeout:  # catch the timeout event
            self._state = DevState.IDLE
            self._tx_timer.reset()
            self._output_power = 0.0

    def send(self, packet):
        duration = packet.data.duration  # signal duration is determined by the data
        self._tx_timer.setDuration(duration)
        self._tx_timer.start()
        self._output_power = self._param.power  # turn on the transmitter so that all receiver can receive it's signal
        # according to the channel model.
        self._state = DevState.SEND

        sig = SigInfo(self._param, packet)  # packet the signal info to inform the receiver
        self._env.sigSwitch(sig)  # very important!!!! in this way, the receiver can get the content of this
        # transmission  without a simulation of an actual demodulation.
        return
