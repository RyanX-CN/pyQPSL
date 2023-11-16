from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLWebEnginePage(QWebEnginePage, QPSLObjectBase):

    def __init__(self, parent: QObject, object_name: str,
                 console_output: bool):
        super().__init__(parent=parent)
        self.m_console_output = console_output
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(object_name)

    def javaScriptConsoleMessage(
            self, level: QWebEnginePage.JavaScriptConsoleMessageLevel,
            message: str, lineNumber: int, sourceID: str):
        if self.m_console_output:
            return super().javaScriptConsoleMessage(level, message, lineNumber,
                                                    sourceID)
