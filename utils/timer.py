# Author liuxin
# email liuxin2017125@glut.edu.cn
# Copyright (c) 2022 liuxin. All rights reserved.


# in fact, as we don't use the multi-thread way to simulate the process of different devices,
# all devices are working in the same thread. Timer objet is a simple counter that just count the
# elapsed time in unit timescale.

class Timer:
    def __init__(self, name):
        self._name = name  # just for debug
        self._duration = 0
        self._count = 0
        self._started = False
        self._timeout = False
        self._param = None  # a variable for telling the catcher what should be done after a timeout

    def reset(self):
        self._count = 0
        self._started = False
        self._timeout = False
        self._param = None

    def setDuration(self, duration):
        self._duration = duration

    def start(self):
        self._count = 0
        self._timeout = False
        self._started = True

    def setParam(self, param):
        self._param = param

    def work(self):
        if not self._started:
            return
        if self._count < self._duration:
            self._count = self._count + 1
        else:
            self._timeout = True

    @property
    def param(self):
        return self._param

    @property
    def timeout(self):
        return self._timeout

