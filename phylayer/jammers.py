from enum import Enum
from random import random, randint

import numpy as np

from phylayer.device import Device, DevType, DevState
from phylayer.devicebase import DeviceBase
from phylayer.transmitter import Transmitter
from utils.types import SigInfo, Packet, Data
from utils.timer import Timer


class JamMode(Enum):
    RAND = 1
    COMB = 2
    SWEEP = 3


class SimpleJammer(Transmitter):

    def __init__(self, env):
        DeviceBase.__init__(self, DevType.JAM, env)
        self._tx_timer = Timer('Jammer')  # timer for sending signal
        self._radiation = True
        self._packet = None
        self._jamming_mode = JamMode.SWEEP
        self._comb_freq_list = [1, 5, 9]  # should be allowed to set
        self._count = 0
        self._dynamic = True

    def setJammingMode(self, jm):
        self._jamming_mode = jm

    def randomJamming(self):
        freq = randint(0, self._env.num_of_channels - 1)
        self._param.setFreq(freq)
        self.send(self._packet)

    def sweepJamming(self):
        freq = self._param.freq
        freq = (freq + 1) % self._env.num_of_channels
        self._param.setFreq(freq)
        self.send(self._packet)

    def combJamming(self):
        self.send(self._packet)

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self._tx_timer.work()
        if self._tx_timer.timeout:  # catch the timeout event
            self._state = DevState.IDLE
            self._tx_timer.reset()
            self._output_power = 0.0

        if self._state == DevState.IDLE:  #

            if self._dynamic:
                self._count = (self._count + 1) % 20
                if self._count == 0:
                    idx = np.random.randint(1, 3)
                    self.setJammingMode(JamMode(idx))

            if self._jamming_mode == JamMode.RAND:
                self.randomJamming()
                return

            if self._jamming_mode == JamMode.SWEEP:
                self.sweepJamming()
                return

            if self._jamming_mode == JamMode.COMB:
                self.combJamming()

    def setSlotDuration(self, duration):
        data = Data(None, None, duration)
        self._packet = Packet(data, None, None, 0, False)
        # noise signal is regard as the modulation of a special packet

    def send(self, packet):
        if self._packet is None:
            return
        duration = packet.data.duration  # signal duration is determined by the data
        self._tx_timer.setDuration(duration)
        self._tx_timer.start()
        self._output_power = self._param.power  # turn on the transmitter so that all receiver can receive it's signal
        self._state = DevState.SEND
        return

    def getOutputPower(self, freq):
        if freq >= self._env.num_of_channels:  # beyond the number of channel of the environment
            return 0.0

        if self._jamming_mode is not JamMode.COMB:
            df = abs(self._param.freq - freq)
            if df <= self._param.band / 2:
                return self._output_power
            else:
                return 0.0

        # COMB is different
        if freq in self._comb_freq_list:
            return self._output_power
        else:
            return 0.0
