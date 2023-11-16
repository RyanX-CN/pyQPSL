from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLLocalServer(QLocalServer, QPSLObjectBase):
    sig_new_connection = pyqtSignal()
    sig_read_data = pyqtSignal(QByteArray)

    def __init__(self, parent: QWidget):
        super(QPSLLocalServer, self).__init__(parent=parent)
        connect_direct(self.newConnection, self.sig_new_connection)
        connect_direct(self.sig_new_connection, self.on_new_connection)
        self.m_socket_list: List[QLocalSocket] = []

    def on_new_connection(self):
        new_socket = QPSLLocalServer.nextPendingConnection(self)
        List.append(self.m_socket_list, new_socket)
        connect_direct(new_socket.readyRead, self.read_data)
        ref = weakref.proxy(self)

        def new_socket_disconnect():
            if weakref.getweakrefcount(ref):
                QPSLLocalServer.on_disconnected(ref, new_socket)

        connect_direct(new_socket.disconnected, new_socket_disconnect)
        self.report_status_with_level(status="server: connect %s socket" %
                                      new_socket,
                                      level=logging.Warning)

    def on_disconnected(self, socket: QLocalSocket):
        if socket in self.m_socket_list:
            List.remove(self.m_socket_list, socket)
        self.report_status_with_level(status="server: disconnect %s socket" %
                                      socket,
                                      level=logging.Warning)

    def listen(self, listen_name: str):
        self.report_status_with_level(status="server: listen to %s" %
                                      listen_name,
                                      level=logging.Warning)
        QLocalServer.listen(self, listen_name)

    def close_and_listen(self, listen_name: str):
        self.report_status_with_level(status="server: close and listen to %s" %
                                      listen_name,
                                      level=logging.Warning)
        QLocalServer.close(self)
        QLocalServer.listen(self, listen_name)

    def read_data(self):
        socket: QLocalSocket = QLocalServer.sender(self)
        data = socket.readAll()
        self.sig_read_data.emit(data)
        self.report_status_with_level(
            status="server: received %s from %s socket" % (data, socket),
            level=logging.Debug)
