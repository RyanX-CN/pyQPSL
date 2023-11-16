from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLEventLoop(QEventLoop, QPSLObjectBase):

    def __init__(self, parent: QWidget, object_name: str):
        super(QPSLEventLoop, self).__init__(parent=parent)
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(object_name)
