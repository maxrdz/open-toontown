from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNodeAI


class DistributedSmartBenchAI(DistributedNodeAI.DistributedNodeAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBenchAI')

    def __init__(self, air):
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)

    def generate(self):
        self.notify.info("Smart Bench AI generate received!")
        DistributedNodeAI.DistributedNodeAI.generate(self)
        self.b_setPosHpr(98, 0, 4.1, 90, 0, 0)

    def delete(self):
        self.notify.info("Smart Bench AI delete received!")
        DistributedNodeAI.DistributedNodeAI.delete(self)
