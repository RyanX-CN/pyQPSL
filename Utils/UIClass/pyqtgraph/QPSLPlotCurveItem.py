from QPSLClass.Base import *
from ...BaseClass import *
from ...Enum import *


class QPSLPlotCurveItem(pyqtgraph.PlotCurveItem, QGraphicsObject,
                        QPSLObjectBase):

    def load_attr(self,
                  x: np.ndarray,
                  y: np.ndarray,
                  pen: Any,
                  antialias: bool = False,
                  skipFiniteCheck: bool = True):
        super().load_attr()
        self.setData(x=x,
                     y=y,
                     pen=pen,
                     antialias=antialias,
                     skipFiniteCheck=skipFiniteCheck)
        return self