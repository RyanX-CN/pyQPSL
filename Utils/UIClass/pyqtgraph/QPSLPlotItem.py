from QPSLClass.Base import *
from ...BaseClass import *
from ...Enum import *
from .QPSLViewBox import QPSLViewBox


class QPSLPlotItem(pyqtgraph.PlotItem, QGraphicsWidget, QPSLObjectBase):

    def __init__(self):
        super().__init__(viewBox=QPSLViewBox().load_attr())

    def viewbox(self) -> QPSLViewBox:
        return super().getViewBox()