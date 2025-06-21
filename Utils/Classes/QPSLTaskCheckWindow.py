from QPSLClass.Base import *
from ..BaseClass import *
from Utils.UIClass.QPSLFrameList import QPSLVFrameList
from Utils.UIClass.QPSLLabel import QPSLLabel
from Utils.UIClass.QPSLPushButton import QPSLPushButton

class QPSLTaskCheckWindow(QPSLVFrameList):

    sig_check_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.m_mutex = QMutex()
        self.setWindowTitle("Please Check the parameters before start")
        self.setWindowIcon(QIcon("./resources/warning.jpg"))
        self.resize(800, 450)


    def load_attr(self, *args, **kwargs):
        super().load_attr()
        self.message = "<br>".join(
        f'<span style="color:black">{k}: </span> <span style="color:blue">{v}</span>'
        for k, v in kwargs.items()
    )
        self.setup_ui()
        self.setup_logic()
        self.set_contents_margins(10, 10, 10, 10)
        return self

    def setup_ui(self):
        self.label_info = self.add_widget(widget=QPSLLabel().load_attr(
            text=self.message, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop))
        self.label_info.setFont(QFont("Arial", 12))
        self.btn_check_done = self.add_widget(widget=QPSLPushButton().load_attr(
            text="OK"))
        self.set_stretch(sizes=(1, 0))

    def setup_logic(self):
        connect_direct(self.btn_check_done.sig_clicked, self.on_check_done)

    def on_check_done(self):
        self.sig_check_done.emit()
        self.close()
