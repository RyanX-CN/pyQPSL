from Tool import *


class DCAMPluginUI(QPSLDockWidget):
    sig_dcam_opened = pyqtSignal()
    sig_dcam_closed = pyqtSignal()
    sig_internal_live_started = pyqtSignal()
    sig_internal_live_stopped = pyqtSignal()

    def __init__(self, parent: QWidget):
        super(DCAMPluginUI, self).__init__(parent=parent)
        self.m_to_send: bytes = "nothing"
        self.setupLoader()
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def setupLoader(self):
        self.m_loader = QPSLLoader(
            self, ".\\Externals\\dcam_control\\dcam_control.exe")
        self.m_loader.sig_show_progress.connect(
            self.show_progress, Qt.ConnectionType.QueuedConnection)
        self.m_loader.sig_not_found_window.connect(
            self.not_found_window, Qt.ConnectionType.QueuedConnection)
        self.m_loader.sig_found_window.connect(
            self.found_window, Qt.ConnectionType.QueuedConnection)
        self.m_loader.start_thread()

    @QPSLObjectBase.logger_decorator
    def setupUi(self):
        if not self.m_loader.m_hwnd:
            self.setMinimumSize(500, 100)
            # load box
            self.m_box_load = QPSLGroupBox(self, "")
            self.setWidget(self.m_box_load)

            # load buttons
            self.m_layout_load = QPSLHBoxLayout(self.m_box_load)
            self.m_button_run_exe = QPSLPushButton(self.m_box_load, "run exe")
            self.m_button_find_exe = QPSLPushButton(self.m_box_load,
                                                    "find exe")
            self.m_layout_load.add_widgets(
                [self.m_button_run_exe, self.m_button_find_exe])

        else:
            self.setMinimumSize(500, 300)
            # box
            self.m_box_content = QPSLTabWidget(self)
            self.setWidget(self.m_box_content)

            # # external page
            self.m_external_window = QWindow.fromWinId(self.m_loader.m_hwnd)
            self.m_external_widget = QPSLHScrollArea.createWindowContainer(
                self.m_external_window, None)
            self.m_box_content.add_tab(self.m_external_widget,
                                       self.m_loader.m_exe_path)

            # # socket page
            self.m_tab_socket = QPSLGroupBox(self.m_box_content, "")
            self.m_box_content.add_tab(self.m_tab_socket, "socket")

            self.m_layout_socket = QPSLVBoxLayout(self.m_tab_socket)

            self.m_edit_listen_name = QPSLLineEdit(self.m_tab_socket,
                                                   "listen name")
            self.m_edit_listen_name.set_text('dcam')

            self.m_list_server_log = QPSLListWidget(self.m_tab_socket, cap=100)

            self.m_layout_socket.add_widgets(
                [self.m_edit_listen_name, self.m_list_server_log])

            # # control page
            self.m_tab_control = QPSLSplitter(self.m_box_content,
                                              Qt.Orientation.Vertical)
            self.m_box_content.add_tab(self.m_tab_control, "control")

            # # # control row1
            self.m_row_control_1 = QPSLSplitter(self.m_tab_control,
                                                Qt.Orientation.Horizontal)

            self.m_button_switch = QPSLToggleButton(self.m_row_control_1)

            self.m_button_internal_live = QPSLToggleButton(
                self.m_row_control_1, "start live", "stop live")

            self.m_spin_exposure = QPSLDoubleSpinBox(self.m_row_control_1, 0,
                                                     0, 1, "exposure:",
                                                     " second")

    @QPSLObjectBase.logger_decorator
    def setupLogic(self):
        if not self.m_loader.m_hwnd:
            self.m_button_run_exe.clicked.connect(
                self.m_loader.run_exe_and_find,
                Qt.ConnectionType.QueuedConnection)
            self.m_button_find_exe.clicked.connect(
                self.m_loader.find_exe_by_window_name,
                Qt.ConnectionType.QueuedConnection)
        else:
            self.m_server = QPSLLocalServer(self)
            self.m_server.sig_status.connect(
                self.m_list_server_log.add_item_scroll)
            self.m_server.listen(self.m_edit_listen_name.text())

            # listen
            self.m_edit_listen_name.sig_editing_finished[str].connect(
                self.m_server.close_and_listen,
                Qt.ConnectionType.QueuedConnection)

            # open close
            self.m_button_switch.sig_open.connect(self.open_dcam)
            self.sig_dcam_opened.connect(self.m_button_switch.set_opened)
            self.m_button_switch.sig_close.connect(self.close_dcam)
            self.sig_dcam_closed.connect(self.m_button_switch.set_closed)

            # exposure
            self.m_spin_exposure.editingFinished.connect(self.setget_exposure)

            # internal live
            self.m_button_internal_live.sig_open.connect(
                self.start_internal_live)
            self.sig_internal_live_started.connect(
                self.m_button_internal_live.set_opened)
            self.m_button_internal_live.sig_close.connect(
                self.stop_internal_live)
            self.sig_internal_live_stopped.connect(
                self.m_button_internal_live.set_closed)

    @QPSLObjectBase.logger_decorator
    def show_progress(self):
        self.m_progress = QPSLProgressDialog(
            None, "opening %s..." % self.m_loader.m_exe_path, 0, 100)
        self.m_progress.show()
        self.m_progress.canceled.connect(self.m_loader.cancle_find_window,
                                         Qt.ConnectionType.QueuedConnection)
        self.m_loader.sig_try_find_exe.connect(
            self.m_progress.setValue, Qt.ConnectionType.QueuedConnection)

    @QPSLObjectBase.logger_decorator
    def not_found_window(self):
        self.m_progress.deleteLater()
        del self.m_progress
        message = QPSLMessageBox(None, "warning",
                                 "not found %s" % self.m_loader.m_exe_path)
        QTimer.singleShot(1000, message.close)
        message.exec()
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def found_window(self):
        self.m_progress.deleteLater()
        del self.m_progress
        message = QPSLMessageBox(None, "infomation",
                                 "found %s" % self.m_loader.m_exe_path)
        QTimer.singleShot(500, message.close)
        message.exec()
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def open_dcam(self):
        self.m_server.m_socket_list[0].write(b'open')

    @QPSLObjectBase.logger_decorator
    def close_dcam(self):
        self.m_server.m_socket_list[0].write(b'close')

    @QPSLObjectBase.logger_decorator
    def start_internal_live(self):
        self.m_server.m_socket_list[0].write(b'start_internal_live')

    @QPSLObjectBase.logger_decorator
    def stop_internal_live(self):
        self.m_server.m_socket_list[0].write(b'stop_internal_live')

    @QPSLObjectBase.logger_decorator
    def setget_exposure(self):
        self.m_server.m_socket_list[0].write(b'setget_exposure %f' %
                                             (self.m_spin_exposure.value()))

    @QPSLObjectBase.logger_decorator_args
    def handle_data(self, data: QByteArray):
        s = data.data().decode('utf8')
        if s.startswith('socket:open'):
            if s.startswith('socket:open true'):
                self.sig_dcam_opened.emit()
        elif s.startswith('socket:close'):
            if s.startswith('socket:close true'):
                self.sig_dcam_closed.emit()
        elif s.startswith('socket:getexposure'):
            if s.startswith('socket:getexposure true'):
                self.m_spin_exposure.setValue(float(s.split()[-1]))
        elif s.startswith('socket:start_internal_live'):
            if s.startswith('socket:start_internal_live true'):
                self.sig_internal_live_started.emit()
        elif s.startswith('socket:stop_internal_live'):
            if s.startswith('socket:stop_internal_live true'):
                self.sig_internal_live_stopped.emit()

        self.report_status(s)


MainWidget = DCAMPluginUI
