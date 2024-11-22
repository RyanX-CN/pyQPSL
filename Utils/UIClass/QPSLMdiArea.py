from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow

from QPSLClass.Base import *
from ..BaseClass import *


class QPSLMdiArea(QMdiArea,QPSLWidgetBase):

    def __init__(self):
        super().__init__()
        return self

class QPSLSubWindow(QMdiSubWindow,QPSLWidgetBase):

    def __init__(self):
        super().__init__()
