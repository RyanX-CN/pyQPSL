from QPSLClass.Base import *
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from ...BaseClass import *
from ...Enum import *


class QPSLViewBox(pyqtgraph.ViewBox, QGraphicsWidget, QPSLObjectBase):

    def __init__(self):
        super().__init__()
        self.m_last_right_click_event: MouseClickEvent = None

    def scene(self) -> pyqtgraph.GraphicsScene:
        return super().scene()

    def mouseClickEvent(self, ev: MouseClickEvent):
        if ev.button() == Qt.MouseButton.RightButton and self.menuEnabled():
            ev.accept()
            self.m_last_right_click_event = ev

    def make_context_menu(self):
        menu = self.getMenu(self.m_last_right_click_event)
        if menu is not None:
            self.scene().addParentContextMenus(self, menu,
                                               self.m_last_right_click_event)
        return menu