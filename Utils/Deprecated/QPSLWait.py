from QPSLClass.Base import *
from Utils.Deprecated.QPSLEventLoop import QPSLEventLoop


class QPSLWait(QPSLEventLoop):

    def __init__(self, parent: QWidget, qpsl_name: str,
                 wait_signal: pyqtSignal):
        super(QPSLWait, self).__init__(parent=parent, object_name=qpsl_name)
        self.m_result = False
        connect_direct(wait_signal, self.on_signal_arrive)

    def start_wait(self, msec: int = 1000):
        self.m_timer = QTimer(None)
        QTimer.setSingleShot(self.m_timer, True)
        connect_direct(self.m_timer.timeout, self.quit)
        QTimer.start(self.m_timer, msec)
        QEventLoop.exec(self)

    def on_signal_arrive(self):
        self.m_result = True
        QEventLoop.quit(self)
