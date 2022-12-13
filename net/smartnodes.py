import random

import numpy as np

from agent.deeplearning import DqnAgent
from net.simpletrafficnode import SimpleTrafficNode
from phylayer.environment import Environment
from phylayer.moniter import Sensor
from utils.logger import logout
from utils.types import Msg, MsgName


class SmartNode(SimpleTrafficNode):
    def __init__(self, pos, env):
        SimpleTrafficNode.__init__(self, pos, env)
        self._agent: DqnAgent = None  # learning agent
        self._sensor: Sensor = None  # sensing device
        self._s = None  # sensing state

    def addAgentAndSensor(self, agent, sensor: Sensor):  # add an agent and sensor for learning
        self._agent = agent
        self._sensor: Sensor = sensor
        self._sensor.setPos(self._pos)  # assign pos to the sensor
        self._sensor.setEnablePlot(True)  # plotting will significantly affect the running speed
        # you can activate it if you want see the detail process.

    def work(self, time_stamp):
        SimpleTrafficNode.work(self, time_stamp)
        if self._sensor is not None:
            self._sensor.work(time_stamp)  # drive the sensor

    def doAction(self, port):
        logout.info('TS_%d Node%d do action',self._time_stamp, self.id)
        freq = np.random.randint(0, self._env.num_of_channels - 1)
        link = self.getLink(port)
        link.rx_dev.param.setFreq(freq)
        link.tx_dev.param.setFreq(freq)

        dst = link.dst
        msg = Msg(MsgName.SET_TRX_FREQ, self._time_stamp, dst, freq)
        env: Environment = self._env
        env.msgSwitch(msg)

        # training


"""        link = self.getLink(port)
        wf = self._sensor.waterfall  # get the current waterfall
        a = link.rx_dev.param.freq  # get current action
        r = self._reward
        sp = wf.copy().reshape(self._agent.input_shape)  # change the data format
        if self._s is not None:
            self._agent.learning(self._s, a, r, sp)
        self._s = sp

        # make a new decision
        a_new = self._agent.get_action(self._s)"""

# change dev param and inform the correspondent node
