from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLLocalSocket(QLocalSocket, QPSLObjectBase):

    def __init__(self, parent: QWidget):
        super(QPSLLocalSocket, self).__init__(parent=parent)
        connect_direct(self.connected, self.on_connected)
        connect_direct(self.disconnected, self.on_disconnected)
        connect_direct(self.readyRead, self.read_data)

    def connect_to_server(self, listen_name: str):
        self.m_listen_name = listen_name
        QLocalSocket.connectToServer(self, listen_name)

    def read_data(self):
        data = QLocalSocket.readAll(self)
        self.report_status_with_level(status="%s Socket received data:%s" %
                                      (data),
                                      level=logging.Debug)

    def on_connected(self):
        self.report_status_with_level(status="connected to '%s'" %
                                      self.m_listen_name,
                                      level=logging.Warning)

    def on_disconnected(self):
        self.report_status_with_level(status="disconnected to '%s'" %
                                      self.m_listen_name,
                                      level=logging.Warning)