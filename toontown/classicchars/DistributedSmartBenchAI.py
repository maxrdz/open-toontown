from random import randrange
from typing import List
from panda3d.core import NodePath, Point3
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNodeAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toonbase import ToontownTimer
from toontown.toonbase import TTLocalizer
from . import CCharPaths


class DistributedSmartBenchAI(DistributedNodeAI.DistributedNodeAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBenchAI')

    def __init__(self, air):
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)

        self.fsm: ClassicFSM = ClassicFSM.ClassicFSM(self.getName(), [
            State.State("Available", self.enterAvailable, self.exitAvailable, ["Occupied"]),
            State.State("Occupied", self.enterOccupied, self.exitOccupied, ["Available"])
        ], "Available", "Available")
        self.fsm.enterInitialState()

        self.sittingAvatar: DistributedToonAI | None = None
        self.benchNode: List[Point3] = [Point3(0, 0, 0), Point3(0, 0, 0)]
        self.benchSeat: Point3 = Point3(1.5, 0, 0.3)  # used relative to bench's coordinate system
        self.timer: ToontownTimer = ToontownTimer.ToontownTimer(useImage=False, highlightNearEnd=False)

    def generate(self):
        self.notify.debug("Smart Bench AI generate received!")
        DistributedNodeAI.DistributedNodeAI.generate(self)
        self.chooseNewBenchPosition()

    def delete(self):
        self.notify.debug("Smart Bench AI delete received!")
        DistributedNodeAI.DistributedNodeAI.delete(self)

    def requestToonSit(self):
        avid = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avid, None)

        if self.fsm.getCurrentState().getName() == "Occupied":
            self.sendUpdateToAvatarId(avid, "respondToonSit", [1])
            return

        if av and isinstance(av, DistributedToonAI):
            self.sittingAvatar = av
            av.b_setAnimState("Sit", 1)
            np = self.attachNewNode("ex")
            render_np = self.attachNewNode("rp")
            render_np.setPos(0, 0, 0)
            np.setPos(self.benchNode[0])
            np.setHpr(self.benchNode[1])
            np.setPos(render_np.getRelativePoint(np, self.benchSeat))
            av.b_setPosHpr(np.getX(), np.getY(), np.getZ(), self.benchNode[1].getX(), 0, 0)

            self.sendUpdateToAvatarId(avid, "respondToonSit", [0])
            self.fsm.request("Occupied")
            self.timer.countdown(10, self.__toonSittingTimerDone)
            self.acceptOnce(self.air.getAvatarExitEvent(avid), self.requestHopOff)
        else:
            self.notify.warning("Sender avId distributed object was not found!")

    def requestHopOff(self):
        if self.fsm.getCurrentState().getName() == "Available":
            self.notify.warning("Tried to request hop off when no toon is sitting.")
        self.timer.reset()
        self.__toonSittingTimerDone()

    def requestMove(self):
        if self.sittingAvatar:
            self.sendUpdateToAvatarId(self.sittingAvatar.doId, "respondToonSit", [2])
            self.fsm.request("Available")
        self.chooseNewBenchPosition()

    def __toonSittingTimerDone(self):
        if self.sittingAvatar and isinstance(self.sittingAvatar, DistributedToonAI):
            self.sittingAvatar.b_setAnimState("neutral", 1)
            self.sittingAvatar = None
            if not self.fsm.request("Available"):
                self.notify.warning("No transition exists for requested state.")
        else:
            # probably called by avatar exit event, force available
            self.fsm.forceTransition("Available")

    def chooseNewBenchPosition(self):
        paths = CCharPaths.getPaths(TTLocalizer.SmartBench)
        oldNode = self.benchNode
        node: Point3 = self.benchNode
        while node == oldNode:
            node = paths[randrange(len(paths))]
        self.d_setPos(node[0].getX(), node[0].getY(), node[0].getZ())
        self.d_setHpr(node[1].getX(), node[1].getY(), node[1].getZ())
        self.benchNode = node

    def enterAvailable(self):
        pass

    def exitAvailable(self):
        pass

    def enterOccupied(self):
        pass

    def exitOccupied(self):
        pass
