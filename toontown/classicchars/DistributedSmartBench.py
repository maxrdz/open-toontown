from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.fsm import ClassicFSM
from direct.fsm import State


class DistributedSmartBench(DistributedNode.DistributedNode):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBench')

    def __init__(self, cr):
        DistributedNode.DistributedNode.__init__(self, cr)

        self.fsm = ClassicFSM.ClassicFSM(self.getName(), [
            State.State("Empty", self.enterEmpty, self.exitEmpty, ["Boarded"]),
            State.State("Boarded", self.enterBoarded, self.exitBoarded, ["Empty", "Full"]),
            State.State("Full", self.enterFull, self.exitFull, ["Boarded"])
        ], "Empty", "Empty")
        self.fsm.enterInitialState()

        self.bench_model = base.loader.loadModel("phase_13/models/tt_m_ara_prp_bench.bam")

    def generate(self):
        self.notify.info("Smart Bench generate received!")
        DistributedNode.DistributedNode.generate(self)
        self.bench_model.reparentTo(self)

    def enterEmpty(self):
        pass

    def exitEmpty(self):
        pass

    def enterBoarded(self):
        pass

    def exitBoarded(self):
        pass

    def enterFull(self):
        pass

    def exitFull(self):
        pass
