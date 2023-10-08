from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI


class DistributedSmartBenchAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBenchAI')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)

    def generate(self):
        self.notify.info("Smart Bench AI generate received!")
        DistributedObjectAI.DistributedObjectAI.generate(self)
