from panda3d.core import Vec4
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from toontown.toonbase import TTLocalizer


class SmartBenchGUI(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('SmartBenchGUI')

    def __init__(self):
        DirectFrame.__init__(self, self)
        gui = base.loader.loadModel('phase_3.5/models/gui/chat_input_gui')

        self.uiFrame = DirectFrame(parent=base.aspect2d, image=gui.find('**/Chat_Bx_FNL'), relief=None,
                                     pos=(0.0, 0, 0.45), state=DGG.NORMAL)
        self.sitButton = DirectButton(parent=self.uiFrame, image=(gui.find('**/ChtBx_ChtBtn_UP'),
                                                                    gui.find('**/ChtBx_ChtBtn_DN'),
                                                                    gui.find('**/ChtBx_ChtBtn_RLVR')),
                                       pos=(0.182, 0, -0.088), relief=None,
                                       text=('', TTLocalizer.SmartBenchSit, TTLocalizer.SmartBenchSit),
                                       text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1),
                                       text_pos=(0, -0.09), textMayChange=0, command=None)
        self.cancelButton = DirectButton(parent=self.uiFrame, image=(gui.find('**/CloseBtn_UP'),
                                                                       gui.find('**/CloseBtn_DN'),
                                                                       gui.find('**/CloseBtn_Rllvr')),
                                         pos=(-0.151, 0, -0.088), relief=None, text=('',
                                                                                     TTLocalizer.SmartBenchCancel,
                                                                                     TTLocalizer.SmartBenchCancel),
                                         text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1),
                                         text_pos=(0, -0.09), textMayChange=0, command=self.cancelClicked)
        self.uiFrameLabel = DirectLabel(parent=self.uiFrame, pos=(0.02, 0, 0.125), relief=DGG.FLAT,
                                        frameColor=(0.5, 0.5, 0.5, 1), frameSize=(-0.245, 0.245, -0.17, 0.05),
                                        text=TTLocalizer.SmartBenchGUILabel, text_scale=0.04,
                                        text_fg=Vec4(0, 0, 0, 1), text_wordwrap=10, textMayChange=1)

        self.disable()  # We load on generate, so wait until we're shown.
        self.acceptOnce("approachedSmartBench", self.approachedSmartBench)

    def approachedSmartBench(self):
        self.enable()
        self.acceptOnce("leftSmartBench", self.leftSmartBench)

    def leftSmartBench(self):
        self.disable()
        self.acceptOnce("approachedSmartBench", self.approachedSmartBench)

    def cancelClicked(self):
        self.disable()

    def enable(self):
        if self.uiFrame.is_hidden():
            self.uiFrame.show()

    def disable(self):
        if not self.uiFrame.is_hidden():
            self.uiFrame.hide()
