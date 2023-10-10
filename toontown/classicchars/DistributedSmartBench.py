from panda3d.core import CollisionSphere, CollisionNode, CollisionRay
from panda3d.core import CollisionHandlerFloor, BitMask32, LVecBase3f
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from otp.otpgui import OTPDialog
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownTimer
from toontown.toontowngui import TTDialog
from toontown.toontowngui import SmartBenchGUI


class DistributedSmartBench(DistributedNode.DistributedNode):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSmartBench')

    def __init__(self, cr):
        DistributedNode.DistributedNode.__init__(self, cr)

        self.bench_model = base.loader.loadModel("phase_13/models/tt_m_ara_prp_bench.bam")
        self.bench_model.reparentTo(self)
        self.bench_gui = SmartBenchGUI.SmartBenchGUI()
        self.bench_timer = ToontownTimer.ToontownTimer()
        self.bench_dialog = None
        # I'm aware this isn't adjusted for dynamic aspect ratios, but it works :P
        self.bench_timer.posBelowTopRightCorner()
        self.bench_timer.hide()

    def generate(self):
        self.notify.debug("Smart Bench generate received!")
        DistributedNode.DistributedNode.generate(self)
        self.reparentTo(base.render)
        self.__initCollisions()
        # SmartBenchGUI fires event, we make the RPC.
        self.accept("requestSmartBenchSit", self.sendUpdate, ["requestToonSit"])
        self.accept("requestSmartBenchMove", self.sendUpdate, ["requestMove"])

    def delete(self):
        self.notify.debug("Smart Bench delete received!")
        self.__deleteCollisions()
        self.bench_gui.delete()
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

    def __handleCollisionEnter(self, collEntry):
        self.notify.debug('Entering Smart Bench proximity collision sphere...')
        base.messenger.send("approachedSmartBench")
        self.acceptOnce('exit' + self.cSphereNode.getName(), self.__handleCollisionExit)

    def __handleCollisionExit(self, collEntry):
        self.notify.debug('Exiting Smart Bench proximity collision sphere...')
        base.messenger.send("leftSmartBench")
        self.acceptOnce('enter' + self.cSphereNode.getName(), self.__handleCollisionEnter)

    def respondToonSit(self, code):
        if code == 2:
            # Bench was moved while we were sitting.
            self.bench_dialog = TTDialog.TTGlobalDialog(message=TTLocalizer.SmartBenchKickedOffDialog,
                                                        style=OTPDialog.Acknowledge, doneEvent="benchDialogAck")
            self.acceptOnce("benchDialogAck", self.bench_dialog.hide)
            return
        elif code == 1:
            # We've been rejected from sitting.
            self.bench_dialog = TTDialog.TTGlobalDialog(message=TTLocalizer.SmartBenchOccupiedDialog,
                                                        style=OTPDialog.Acknowledge, doneEvent="benchDialogAck")
            self.acceptOnce("benchDialogAck", self.bench_dialog.hide)
            return
        elif code == 0:
            # We're now sitting.
            self.bench_gui.disable()
            self.bench_timer.show()
            self.bench_timer.countdown(10, self.__benchTimerDone)
            base.localAvatar.detachCamera()
            # I spent so much time trying out relative vectors until I remembered
            # that the local toon is always at render space origin.
            base.camera.setPos(0, 5, 3)
            base.camera.lookAt(base.localAvatar)
            base.camera.setHpr(base.camera.getHpr() + LVecBase3f(0, 25, 0))
            base.localAvatar.stopUpdateSmartCamera()
            base.localAvatar.disableAvatarControls()
            self.acceptOnce("shift-up", self.hopOffBench)

    def __benchTimerDone(self):
        self.bench_timer.reset()
        self.bench_timer.hide()
        base.localAvatar.attachCamera()
        base.localAvatar.startUpdateSmartCamera()
        base.localAvatar.enableAvatarControls()

    def hopOffBench(self):
        self.__benchTimerDone()
        self.sendUpdate("requestHopOff")
