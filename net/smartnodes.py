import random

import numpy as np

from agent.deeplearning import AgentDQN
from net.simpletrafficnode import SimpleTrafficNode
from phylayer.environment import Environment
from phylayer.moniter import Sensor
from utils.logger import logout
from utils.types import Msg, MsgName


class SmartNode(SimpleTrafficNode):
    def __init__(self, pos, env):
        SimpleTrafficNode.__init__(self, pos, env)
        self._agent: AgentDQN = None  # learning agent
        self._sensor: Sensor = None  # sensing device
        self._s = None  # sensing state
        self._env: Environment = env  # specify the class of _env
        self._average_r = 0
        self._reward_records = []

    def addAgent(self, agent):
        self._agent = agent

    def addSensor(self, sensor: Sensor):  # add an agent and sensor for learning
        self._sensor: Sensor = sensor
        self._sensor.setPos(self._pos)  # assign pos to the sensor
        self._sensor.setEnablePlot(False)  # plotting will significantly affect the running speed
        # you can activate it if you want see the detail process.

    def work(self, time_stamp):
        SimpleTrafficNode.work(self, time_stamp)

    def doAction(self, port):
        if self._learning is not True:
            return
        logout.info('TS_%d Node%d do action', self._time_stamp, self.id)

        # training
        link = self.getLink(port)
        wf = self._sensor.waterfall  # get the current waterfall
        a = link.rx_dev.param.freq  # get current action
        if link.getReceiveResult():
            r = 1
        else:
            r = -1

        self._average_r = self._average_r * 0.98 + 0.02 * (r + 1) / 2
        print('TS_%s Node(%d,%d),r=%d, average_r=%f' % (self._time_stamp, self._id, link.id, r, self._average_r))
        self.reward_records.append(self._average_r)

        sp = wf.copy().reshape(self._agent.input_shape)  # change the data format
        if self._s is not None:
            self._agent.learning(self._s, a, r, sp)
        self._s = sp

        # make a new decision
        a_new = self._agent.getAction(self._s)
        link.rx_dev.param.setFreq(a_new)
        link.tx_dev.param.setFreq(a_new)

        # inform its partner
        msg = Msg(MsgName.SET_TRX_FREQ, self._time_stamp, link.dst, a_new)
        self._env.msgSwitch(msg)

    @property
    def reward_records(self):
        return self._reward_records
