from QPSLClass.Base import *
from Utils.BaseClass import *
from Utils.Deprecated.QPSLTimer import QPSLTimer


class QPSLClock(QObject, QPSLObjectBase):
    sig_timer_started = pyqtSignal()
    sig_timer_stopped = pyqtSignal()
    sig_time_out = pyqtSignal()

    def __init__(self, parent: QObject, qpsl_name: str, interval: int = 30):
        super(QPSLClock, self).__init__(parent=None)
        self.set_QPSL_parent(qpsl_parent=parent)
        self.setObjectName(name=qpsl_name)
        self.m_interval = interval
        self.m_timer: QPSLTimer = None
        self.m_thread = weakref.ref(QThread(self))
        self.moveToThread(self.m_thread())

    def __del__(self):
        if self.m_thread().isRunning():
            self.stop_thread()

    def start_thread(self):
        self.m_thread().start()

    def stop_thread(self):
        self.m_thread().quit()
        self.m_thread().wait()

    def set_interval(self, interval: int):
        self.m_interval = interval
        if self.m_timer:
            self.m_timer.set_interval(interval=interval)

    def start_timer(self):
        if not self.m_timer:
            self.m_timer = QPSLTimer(self,
                                     object_name="timer",
                                     interval=self.m_interval)
            connect_direct(self.m_timer.sig_timer_started,
                           self.sig_timer_started)
            connect_direct(self.m_timer.sig_timer_stopped,
                           self.sig_timer_stopped)
            connect_direct(self.m_timer.timeout, self.sig_time_out)
            self.m_timer.start_timer()

    def stop_timer(self):
        if self.m_timer:
            self.m_timer.stop_timer()
            self.m_timer = None
