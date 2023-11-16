from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLProgressBar(QProgressBar, QPSLWidgetBase):

    def __init__(self, parent: QWidget, object_name: str, format=""):
        super().__init__(parent=parent)
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(object_name)
        if format:
            self.setFormat(format)
