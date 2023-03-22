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
        self._freq_list = [1]
        self._count = 0
        self._speed = 1
        self._offset = 0
        self._dynamic = False

    def setOffset(self, offset):
        self._offset = offset

    def setJammingMode(self, jm, dynamic):
        self._dynamic = dynamic
        self._jamming_mode = jm

    def randomJamming(self):
        num = randint(1, 4)
        self._freq_list = np.random.choice(4, num, replace=False) + self._offset
        self.send()

    def sweepJamming(self):
        freq = self._freq_list[0]
        freq = (freq + self._speed)
        if freq == self._env.num_of_channels - 1:
            self._speed = -1
        if freq == 0:
            self._speed = 1

        self._param.setFreq(freq)
        self.send()
        self._freq_list[0] = freq

    def combJamming(self):
        self._freq_list = [2, 5, 8]
        self.send()

    def work(self, time_stamp):
        self._time_stamp = time_stamp
        self._tx_timer.work()
        if self._tx_timer.timeout:  # catch the timeout event
            self._state = DevState.IDLE
            self._tx_timer.reset()
            self._output_power = 0.0

        if self._state == DevState.IDLE:  #

            if self._dynamic:
                self._count = (self._count + 1) % 4
                # if self._count == 0:
                # self._offset = (1 - self._offset / 5) * 5

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

    def send(self):
        if self._packet is None:
            return
        duration = self._packet.data.duration  # signal duration is determined by the data
        self._tx_timer.setDuration(duration)
        self._tx_timer.start()
        self._output_power = self._param.power  # turn on the transmitter so that all receiver can receive it's signal
        self._state = DevState.SEND
        return

    def getOutputPower(self, freq):
        if freq >= self._env.num_of_channels:  # beyond the number of channel of the environment
            return 0.0

        if freq in self._freq_list:
            return self._output_power
        else:
            return 0.0
