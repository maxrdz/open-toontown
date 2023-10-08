from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.fsm import ClassicFSM
from direct.fsm import State


class DistributedSmartBench(DistributedNode.DistributedNode):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBench')

    def __init__(self, cr):
        DistributedNode.DistributedNode.__init__(self, cr)

        self.fsm = ClassicFSM.ClassicFSM(self.getName(), [
            State.State("Available", self.enterAvailable, self.exitAvailable, ["Occupied"]),
            State.State("Occupied", self.enterOccupied, self.exitOccupied, ["Available"])
        ], "Available", "Available")
        self.fsm.enterInitialState()

        self.bench_model = base.loader.loadModel("phase_13/models/tt_m_ara_prp_bench.bam")
        self.bench_model.reparentTo(self)

    def generate(self):
        self.notify.info("Smart Bench generate received!")
        DistributedNode.DistributedNode.generate(self)
        self.reparentTo(base.render)

    def delete(self):
        self.notify.info("Smart Bench delete received!")
        self.reparentTo(base.hidden)
        DistributedNode.DistributedNode.delete(self)

    def enterAvailable(self):
        pass

    def exitAvailable(self):
        pass

    def enterOccupied(self):
        pass

    def exitOccupied(self):
        pass
