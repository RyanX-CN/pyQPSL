from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLTimer(QTimer, QPSLObjectBase):
    sig_timer_started = pyqtSignal()
    sig_timer_stopped = pyqtSignal()

    def __init__(self, parent: QWidget, object_name: str, interval: int = 30):
        super().__init__(parent=parent)
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(object_name)
        self.setInterval(interval)

    def start_timer(self):
        if not self.isActive():
            self.sig_timer_started.emit()
            self.start()

    def stop_timer(self):
        if self.isActive():
            self.stop()
            self.sig_timer_stopped.emit()