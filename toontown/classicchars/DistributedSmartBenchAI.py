from random import randrange
from panda3d.core import Point3
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

        self.sitting_avatar: DistributedToonAI | None = None
        self.bench_node: Point3 = Point3(0, 0, 0)
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
            self.sitting_avatar = av
            av.b_setAnimState("Sit", 1)
            self.sendUpdateToAvatarId(avid, "respondToonSit", [0])
            self.fsm.request("Occupied")
            self.timer.countdown(10, self.__toonSittingTimerDone)
            self.acceptOnce(self.air.getAvatarExitEvent(avid), self.requestHopOff)
        else:
            self.notify.warning("Sender avId distributed object was not found!")

    def requestHopOff(self):
        if self.fsm.getCurrentState().getName() == "Available":
            self.notify.warning("Tried to request hop off when no toon is sitting.")
            return
        self.timer.reset()
        self.__toonSittingTimerDone()

    def requestMove(self):
        if self.sitting_avatar:
            self.sendUpdateToAvatarId(self.sitting_avatar.doId, "respondToonSit", [2])
            self.fsm.request("Available")
        self.chooseNewBenchPosition()

    def __toonSittingTimerDone(self):
        if self.sitting_avatar and isinstance(self.sitting_avatar, DistributedToonAI):
            self.sitting_avatar.b_setAnimState("neutral", 1)
            self.sitting_avatar = None
            if not self.fsm.request("Available"):
                self.notify.warning("No transition exists for requested state.")
        else:
            # probably called by avatar exit event, force available
            self.fsm.forceTransition("Available")

    def chooseNewBenchPosition(self):
        paths = CCharPaths.getPaths(TTLocalizer.SmartBench)
        old_node = self.bench_node
        node: Point3 = self.bench_node
        while node == old_node:
            node = paths[randrange(len(paths))]
        self.d_setPos(node[0].getX(), node[0].getY(), node[0].getZ())
        self.d_setHpr(node[1].getX(), node[1].getY(), node[1].getZ())

    def enterAvailable(self):
        pass

    def exitAvailable(self):
        pass

    def enterOccupied(self):
        pass

    def exitOccupied(self):
        pass
