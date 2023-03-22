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
    jammer = SimpleJammer(env)
    jammer.setParam(DevParam(100, 1, 0))
    jammer.setPos(Pos(500, 500))
    jammer.setSlotDuration(1)
    jammer.setJammingMode(JamMode.SWEEP, False)

    # add a sensor device
    sensor = Sensor(env)
    sensor.setTWL(100)
    sensor.setPos(Pos(50, 50))

    logout.info('start simulation....')
    simu_times = 200
    for t in range(0, simu_times):
        env.work(t)
