from QPSLClass.Base import *
from Utils.Deprecated.QPSLTimer import QPSLTimer


class QPSLCountDown(QPSLTimer):
    sig_to_value = pyqtSignal(int)
    sig_to_zero = pyqtSignal()

    def __init__(self,
                 parent: QObject,
                 object_name: str,
                 interval=30,
                 init_number=100):
        super().__init__(parent=parent,
                         object_name=object_name,
                         interval=interval)
        self.m_value = init_number
        connect_direct(self.timeout, self.count_down)
        connect_direct(self.sig_to_zero, self.stop_timer)

    def set_value(self, value: int):
        self.m_value = value

    def count_down(self):
        self.m_value -= 1
        if self.m_value < 0:
            self.m_value = 0
        self.sig_to_value.emit(self.m_value)
        if self.m_value == 0:
            self.sig_to_zero.emit()

    def count_down_by(self, inc):
        self.m_value -= inc
        if self.m_value < 0:
            self.m_value = 0
        self.sig_to_value.emit(self.m_value)
        if self.m_value == 0:
            self.sig_to_zero.emit()
