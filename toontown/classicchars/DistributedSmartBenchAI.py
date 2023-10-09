from panda3d.core import Point3
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNodeAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toonbase import TTLocalizer
from . import CCharPaths
from random import randrange


class DistributedSmartBenchAI(DistributedNodeAI.DistributedNodeAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBenchAI')

    def __init__(self, air):
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM(self.getName(), [
            State.State("Available", self.enterAvailable, self.exitAvailable, ["Occupied"]),
            State.State("Occupied", self.enterOccupied, self.exitOccupied, ["Available"])
        ], "Available", "Available")
        self.fsm.enterInitialState()

    def generate(self):
        self.notify.info("Smart Bench AI generate received!")
        DistributedNodeAI.DistributedNodeAI.generate(self)

        paths = CCharPaths.getPaths(TTLocalizer.SmartBench)
        node = paths[randrange(len(paths))]  # randrange is exclusive
        self.d_setPos(node[0].getX(), node[0].getY(), node[0].getZ())
        self.d_setHpr(node[1].getX(), node[1].getY(), node[1].getZ())

    def delete(self):
        self.notify.info("Smart Bench AI delete received!")
        DistributedNodeAI.DistributedNodeAI.delete(self)

    def enterAvailable(self):
        pass

    def exitAvailable(self):
        pass

    def enterOccupied(self):
        pass

    def exitOccupied(self):
        pass
