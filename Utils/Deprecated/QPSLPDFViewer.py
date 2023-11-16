from QPSLClass.Base import *
from QPSLClass.QPSLWebEnginPage import QPSLWebEnginePage
from QPSLClass.QPSLWebEnginView import QPSLWebEngineView


class QPSLPDFViewer(QPSLWebEngineView):

    def __init__(self, parent: QWidget, object_name: str):
        super().__init__(parent=parent, object_name=object_name)
        self.setPage(
            QPSLWebEnginePage(self, object_name="page", console_output=False))
        self.set_plugin_enabled()

    def set_doc(self, path: str):
        self.setUrl(QUrl.fromLocalFile(path))
