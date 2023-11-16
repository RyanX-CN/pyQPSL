from Tool import *


class CalculatorPluginUI(QPSLDockWidget):
    def __init__(self, parent):
        super(CalculatorPluginUI, self).__init__(parent=parent)
        self.setupLoader()
        self.setupUi()
        self.setupLogic()

    def __del__(self):
        if self.m_loader.m_hwnd:
            win32gui.PostMessage(self.m_loader.m_hwnd, 16, 0, 0)

    @QPSLObjectBase.logger_decorator
    def setupLoader(self):
        self.m_loader = QPSLLoader(
            self, "C:\WINDOWS\System32\calc.exe",'计算器')
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
            self.m_button_run_exe = QPSLPushButton(
                self.m_box_load, "run exe")
            self.m_button_find_exe = QPSLPushButton(
                self.m_box_load, "find exe")
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
            self.m_box_content.add_tab(
                self.m_external_widget, self.m_loader.m_exe_path)

    @QPSLObjectBase.logger_decorator
    def setupLogic(self):
        if not self.m_loader.m_hwnd:
            self.m_button_run_exe.clicked.connect(
                self.m_loader.run_exe_and_find, Qt.ConnectionType.QueuedConnection)
            self.m_button_find_exe.clicked.connect(
                self.m_loader.find_exe_by_window_name, Qt.ConnectionType.QueuedConnection)
        else:
            pass

    @QPSLObjectBase.logger_decorator
    def show_progress(self):
        self.m_progress = QPSLProgressDialog(
            None, "opening %s..." % self.m_loader.m_exe_path, 0, 100)
        self.m_progress.show()
        self.m_progress.canceled.connect(
            self.m_loader.cancle_find_window, Qt.ConnectionType.QueuedConnection)
        self.m_loader.sig_try_find_exe.connect(
            self.m_progress.setValue, Qt.ConnectionType.QueuedConnection)

    @QPSLObjectBase.logger_decorator
    def not_found_window(self):
        self.m_progress.deleteLater()
        del self.m_progress
        message = QPSLMessageBox(
            None, "warning", "not found %s" % self.m_loader.m_exe_path)
        QTimer.singleShot(1000, message.close)
        message.exec()
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def found_window(self):
        self.m_progress.deleteLater()
        del self.m_progress
        message = QPSLMessageBox(
            None, "infomation", "found %s" % self.m_loader.m_exe_path)
        QTimer.singleShot(500, message.close)
        message.exec()
        self.setupUi()
        self.setupLogic()


MainWidget = CalculatorPluginUI
