from QPSLClass.Base import *
from ...BaseClass import *
from ...Enum import *
import pyqtgraph.opengl.GLViewWidget


class QPSLOpenGLWidget(pyqtgraph.opengl.GLViewWidget, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()

    def load_attr(self,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)


    def setup_logic(self):
        pass
