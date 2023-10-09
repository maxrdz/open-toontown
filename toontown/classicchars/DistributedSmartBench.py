from panda3d.core import CollisionSphere, CollisionNode, CollisionRay
from panda3d.core import CollisionHandlerFloor, BitMask32
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toonbase import ToontownGlobals


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
        self.__initCollisions()

    def delete(self):
        self.notify.info("Smart Bench delete received!")
        self.__deleteCollisions()
        self.reparentTo(base.hidden)
        DistributedNode.DistributedNode.delete(self)

    def __initCollisions(self):
        self.cSphere = CollisionSphere(0.0, 0.0, 0.0, 4.0)
        self.cSphere.setTangible(0)  # Should not push back player
        self.cSphereNode = CollisionNode(self.getName() + 'ProximitySphere')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.acceptOnce('enter' + self.cSphereNode.getName(), self.__handleCollisionEnter)
        self.cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        self.cRayNode = CollisionNode(self.getName() + 'cRay')
        self.cRayNode.addSolid(self.cRay)
        self.cRayNodePath = self.attachNewNode(self.cRayNode)
        self.cRayNodePath.hide()
        self.cRayBitMask = ToontownGlobals.FloorBitmask
        self.cRayNode.setFromCollideMask(self.cRayBitMask)
        self.cRayNode.setIntoCollideMask(BitMask32.allOff())
        self.lifter = CollisionHandlerFloor()
        self.lifter.setOffset(ToontownGlobals.FloorOffset)
        self.lifter.setReach(10.0)
        self.lifter.setMaxVelocity(0.0)
        self.lifter.addCollider(self.cRayNodePath, self)
        self.cTrav = base.localAvatar.cTrav

    def __deleteCollisions(self):
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.lifter = None
        self.cTrav = None
        return

    def __handleCollisionEnter(self, collEntry):
        self.notify.info('Entering Smart Bench proximity collision sphere...')
        self.acceptOnce('exit' + self.cSphereNode.getName(), self.__handleCollisionExit)

    def __handleCollisionExit(self, collEntry):
        self.notify.info('Exiting Smart Bench proximity collision sphere...')
        self.acceptOnce('enter' + self.cSphereNode.getName(), self.__handleCollisionEnter)

    def enterAvailable(self):
        pass

    def exitAvailable(self):
        pass

    def enterOccupied(self):
        pass

    def exitOccupied(self):
        pass
