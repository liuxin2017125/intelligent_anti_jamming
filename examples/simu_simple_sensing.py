# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.

import math

import numpy as np
from matplotlib import pyplot as plt

from phylayer.environment import Environment
from phylayer.jammers import SimpleJammer, JamMode
from phylayer.moniter import Sensor
from utils.types import Pos, DevParam
from utils.logger import logout

if __name__ == '__main__':

    env = Environment(10)
    # add a jamming device
    jammer1 = SimpleJammer(env)
    jammer1.setParam(DevParam(100, 1, 0))
    jammer1.setPos(Pos(100, 500))
    jammer1.setSlotDuration(1)
    jammer1.setJammingMode(JamMode.SWEEP, False)

    jammer2 = SimpleJammer(env)
    jammer2.setParam(DevParam(100, 1, 0))
    jammer2.setPos(Pos(1000, 1000))
    jammer2.setSlotDuration(10)
    jammer2.setJammingMode(JamMode.COMB, False)

    # add a sensor device
    sensor = Sensor(env)
    sensor.setTWL(100)
    sensor.setPos(Pos(50, 50))
    # sensor.setEnablePlot(False)

    logout.info('start simulation....')
    simu_times = 200
    for t in range(0, simu_times):
        env.work(t)
