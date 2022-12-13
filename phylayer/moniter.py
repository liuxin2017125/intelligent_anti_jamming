import numpy as np
from matplotlib import pyplot as plt
from numpy import log10, double
from phylayer.device import DevType
from phylayer.devicebase import DeviceBase


class Sensor(DeviceBase):
    def __init__(self, env):
        DeviceBase.__init__(self, DevType.SEN, env)
        self._twl = 100  # time window length
        self._waterfall = []
        self._spec_list = []
        self._enable_plot = True
        self._fig_index = 1
        self._aspect = 1  # coordinate the  image width and height

    def setEnablePlot(self, en_plot):
        self._enable_plot = en_plot

    def setTWL(self, twl):
        self._twl = twl
        for n in range(0, self._twl):
            spec = np.ones([self._env.num_of_channels]) * self._env.noise
            self._spec_list.append(spec)

        self._waterfall = np.ones([self._twl, self._env.num_of_channels])
        self._aspect = double(self._env.num_of_channels) / double(self._twl)

    def work(self, time_stamp):
        spec = np.zeros([self._env.num_of_channels])
        for ch in range(0, self._env.num_of_channels):
            spec[ch] = self._env.sense(self._pos, ch)  # spectrum sensing

        self._spec_list.pop(0)
        self._spec_list.append(spec)
        for n in range(0, self._twl):
            self._waterfall[n, :] = 10 * log10(self._spec_list[self._twl - n - 1])

        # self.waterfall=self.waterfall-np.mean(self.waterfall)
        self.showWaterfall()

    def showWaterfall(self):
        if self._enable_plot:
            plt.figure(self._fig_index)
            plt.cla()
            plt.imshow(self._waterfall, aspect=self._aspect)
            plt.title('spectrum waterfall')
            plt.draw()
            plt.pause(0.001)
