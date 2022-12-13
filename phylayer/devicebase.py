from linklayer.linklayer import LinkLayer
from net.node import Node
from phylayer.device import Device, DevType, DevState
from phylayer.environment import Environment
from utils.types import SigInfo, DevParam, Pos, Msg
from utils.timer import Timer


# base class of device
class DeviceBase(Device):
    def __init__(self, dtype: DevType, env):  # unspecified type of env is for avoiding circular reference.
        Device.__init__(self, dtype, env)
        self._link: LinkLayer = None
        self._node: Node = None
        self._env: Environment = self._env

    def setLink(self, link: LinkLayer):  # unspecified type of link is for avoiding circular reference.
        self._link = link

    def setNode(self, node):
        self._node: Node = node

    def sendMsgToNode(self, msg: Msg):
        if self._node is not None:
            self._node.addMsg(msg)
