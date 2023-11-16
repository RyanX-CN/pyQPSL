from QPSLClass.Base import *
from Utils.Deprecated.QPSLCountDown import QPSLCountDown
from Utils.Deprecated.QPSLEventLoop import QPSLEventLoop
from Utils.Deprecated.QPSLProcess import QPSLProcess
from Utils.Classes.QPSLWorker import QPSLWorker


class QPSLLoader(QPSLWorker):
    sig_show_progress = pyqtSignal()
    sig_try_find_exe = pyqtSignal(int)
    sig_found_exe_result = pyqtSignal(int)

    def __init__(self, parent: QWidget, exe_path: str, find_window_name: str):
        super(QPSLLoader, self).__init__(parent=parent)
        self.m_exe_path: str = exe_path
        self.m_find_window_name: str = find_window_name
        self.m_process: QPSLProcess = None
        self.m_move_loop: QPSLEventLoop = None
        self.m_counter: QPSLCountDown = None
        self.m_hwnd: int = 0

    def run_exe_and_find(self):
        self.m_process = QPSLProcess(self)
        self.m_process.start(self.m_exe_path)
        self.find_exe_by_window_name()

    def find_exe_by_window_name(self):
        if self.m_move_loop:
            return
        self.sig_show_progress.emit()
        self.m_move_loop = QPSLEventLoop(None)
        self.m_counter = QPSLCountDown(None, interval=20, init_number=100)

        def call(self: QPSLLoader):

            def internal_call(value):
                pyqtBoundSignal.emit(self.sig_try_find_exe, 99 - value)
                hwnds = []
                win32gui.EnumChildWindows(
                    None, lambda hwnd, param: param.append(hwnd), hwnds)
                for hwnd in hwnds:
                    window_name = win32gui.GetWindowText(hwnd)
                    if self.m_find_window_name == window_name:
                        self.m_hwnd = hwnd
                        break
                if self.m_hwnd:
                    self.m_counter.stop_timer()
                time.sleep(0.05)

            return internal_call

        connect_direct(self.m_counter.sig_to_value, call(weakref.proxy(self)))
        connect_direct(self.m_counter.sig_timer_stopped, self.m_move_loop.quit)
        self.m_counter.start_timer()
        QEventLoop.exec_(self.m_move_loop)

        pyqtBoundSignal.emit(self.sig_found_exe_result, self.m_hwnd)
        if self.m_hwnd:
            self.report_status_with_level(status="%s started, window id = %d" %
                                          (self.m_exe_path, self.m_hwnd),
                                          level=logging.Warning)
        else:
            self.report_status_with_level(status="%s didn't start!!!" %
                                          self.m_exe_path,
                                          level=logging.Error)

        self.m_counter = None
        self.m_move_loop = None

    def cancle_find_window(self):
        if self.m_counter:
            self.m_counter.stop_timer()