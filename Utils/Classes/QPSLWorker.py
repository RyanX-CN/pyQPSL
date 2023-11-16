from QPSLClass.Base import *
from ..BaseClass import *


class QPSLWorker(QPSLObjectBase):
    sig_thread_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.m_thread = weakref.ref(QThread(self))
        self.moveToThread(self.m_thread())

    def start_thread(self):
        self.m_thread().start()
        self.sig_thread_started.emit()

    def stop_thread(self):
        self.m_thread().quit()
        self.m_thread().wait()
