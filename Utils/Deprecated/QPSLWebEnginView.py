from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLWebEngineView(QWebEngineView, QPSLWidgetBase):

    def __init__(self, parent: QWidget, object_name: str):
        super().__init__(parent=parent)
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(object_name)

    def set_plugin_enabled(self):
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

    def set_plugin_disabled(self):
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
