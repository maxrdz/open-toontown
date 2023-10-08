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
        node = paths[randrange(3)]
        self.b_setPosHpr(node[0][0], node[0][1], node[0][2], node[1][0], node[1][1], node[1][2])

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
