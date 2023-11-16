from Tool import *
from Plugins.ZaberPlugin.ZaberPlugin import ZaberPluginUI
from Plugins.PIPlugin.PIPlugin import PIPluginUI
from Externals.DM_control.DM_control import DMPluginUI
from Externals.DAQ_control.DAQ_control import DAQPluginUI


def choose_best(daq_result: List[np.ndarray]):
    length = len(daq_result)
    return random.randint(1, length)


class ZaberPIDMPluginWorker(QPSLWorker):
    sig_task_started = pyqtSignal()
    sig_task_stopped = pyqtSignal()
    sig_zaber_move = pyqtSignal(float)
    sig_zaber_arrive = pyqtSignal()
    sig_pi_move = pyqtSignal(float)
    sig_pi_arrive = pyqtSignal()
    sig_dm_load = pyqtSignal(str)
    sig_dm_over = pyqtSignal()
    sig_daq_start = pyqtSignal()
    # sig_daq_report_data = pyqtSignal(np.ndarray)
    sig_daq_report_data = pyqtSignal(str)
    sig_daq_report_data_over = pyqtSignal()

    def __init__(self, parent, state_controller: SharedStateController):
        super(ZaberPIDMPluginWorker, self).__init__(parent=parent)
        self.m_state_controller = state_controller
        self.m_list: List[str] = []
        self.sig_daq_report_data.connect(self.report_data)

    @QPSLObjectBase.logger_decorator_args
    def start_work(self, zaber_range: List[float], pi_range: List[float],
                   pi_small_step: float, dm_files: List[str],
                   daq_save_dir: str):
        try:
            self.sig_task_started.emit()

            def zaber_work(zaber_position):
                self.sig_zaber_move.emit(zaber_position)
                waiter = QPSLWait(None, self.sig_zaber_arrive)
                waiter.start_wait(1000)
                if waiter.m_result == False:
                    raise BaseException("!!!zaber late for position:%f" %
                                        zaber_position)

            def pi_work(pi_position):
                self.sig_pi_move.emit(pi_position)
                waiter = QPSLWait(None, self.sig_pi_arrive)
                waiter.start_wait(1000)
                if waiter.m_result == False:
                    raise BaseException("!!!pi late for position:%f" %
                                        pi_position)

            def dm_work(dm_file):
                self.sig_dm_load.emit(dm_file)
                waiter = QPSLWait(None, self.sig_dm_over)
                waiter.start_wait(1000)
                if waiter.m_result == False:
                    raise BaseException("!!!dm late for file:%s" % dm_file)

            def daq_work():
                waiter = QPSLWait(None, self.sig_daq_report_data_over)
                self.sig_daq_start.emit()
                waiter.start_wait(10000)
                if waiter.m_result == False:
                    raise BaseException("!!!daq late")
                time.sleep(0.1)

            def zaber_trip(zaber_range):
                for zaber_position in float_range(zaber_range[0],
                                                  zaber_range[1],
                                                  zaber_range[2]):
                    if self.m_state_controller.get_value() == "stop":
                        raise BaseException("!!!task aborted")
                    zaber_work(zaber_position=zaber_position)
                    yield zaber_position

            def pi_trip(pi_range):
                for pi_position in float_range(pi_range[0], pi_range[1],
                                               pi_range[2]):
                    if self.m_state_controller.get_value() == "stop":
                        raise BaseException("!!!task aborted")
                    pi_work(pi_position=pi_position)
                    yield pi_position

            def dm_trip(dm_files):
                for dm_file in dm_files:
                    if self.m_state_controller.get_value() == "stop":
                        raise BaseException("!!!task aborted")
                    dm_work(dm_file=dm_file)
                    yield dm_file

            for z_position in zaber_trip(zaber_range=zaber_range):
                for p_position in pi_trip(pi_range=pi_range):
                    self.m_list.clear()
                    for dm_file in dm_trip(dm_files=dm_files):
                        print(z_position, p_position, dm_file)
                        daq_work()
                    best = choose_best(self.m_list)
                    dm_work(dm_file=dm_files[best - 1])

                    pi_small_range = [
                        p_position, p_position + pi_range[2], pi_small_step
                    ]
                    paras = []
                    self.m_list.clear()
                    for p_small_position in pi_trip(pi_range=pi_small_range):
                        paras.append(
                            "%.3f_%s_%.3f" %
                            (z_position, dm_files[best - 1], p_small_position))
                        daq_work()
                    for filename, arr in zip(paras, self.m_list):
                        with open("%s/%s.txt" % (daq_save_dir, filename),
                                  "wt") as f:
                            # f.write('\n'.join(map(str, arr)))
                            f.write(arr)

        except BaseException as e:
            print(e)
        finally:
            self.sig_task_stopped.emit()

    @QPSLObjectBase.logger_decorator_args
    def report_data(self, data: str):
        print("report data", data)
        self.m_list.append(data)
        self.sig_daq_report_data_over.emit()


class ZaberPIDMPluginUI(QPSLDockWidget):
    sig_start_work = pyqtSignal([list, list, float, list, str])

    def __init__(self, parent):
        super(ZaberPIDMPluginUI, self).__init__(parent=parent)
        self.m_state_controller = SharedStateController()
        self.m_worker = ZaberPIDMPluginWorker(self, self.m_state_controller)
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def setupUi(self):
        # box
        self.m_box_content = QPSLTabWidget(self)
        self.setWidget(self.m_box_content)

        # # main tab
        self.m_tab_main = QPSLSplitter(self.m_box_content,
                                       Qt.Orientation.Vertical)
        self.m_box_content.add_tab(self.m_tab_main, "main")

        # # # zaber range
        self.m_zaber_range = QPSLSplitter(self.m_tab_main,
                                          Qt.Orientation.Horizontal)
        self.m_spin_zaber_start = QPSLDoubleSpinBox(self.m_zaber_range,
                                                    value=0,
                                                    lower=-10000,
                                                    upper=10000,
                                                    prefix="zaber from: ")
        self.m_spin_zaber_end = QPSLDoubleSpinBox(self.m_zaber_range,
                                                  value=1000,
                                                  lower=-10000,
                                                  upper=10000,
                                                  prefix="zaber to: ")
        self.m_spin_zaber_step = QPSLDoubleSpinBox(self.m_zaber_range,
                                                   value=100,
                                                   lower=0.01,
                                                   upper=10000,
                                                   prefix="zaber step: ")

        # # # pi range
        self.m_pi_range = QPSLSplitter(self.m_tab_main,
                                       Qt.Orientation.Horizontal)
        self.m_spin_pi_start = QPSLDoubleSpinBox(self.m_pi_range,
                                                 value=0,
                                                 lower=-10000,
                                                 upper=10000,
                                                 prefix="pi from: ")
        self.m_spin_pi_end = QPSLDoubleSpinBox(self.m_pi_range,
                                               value=1,
                                               lower=-10000,
                                               upper=10000,
                                               prefix="pi to: ")
        self.m_spin_pi_step = QPSLDoubleSpinBox(self.m_pi_range,
                                                value=0.5,
                                                lower=0.01,
                                                upper=10000,
                                                prefix="pi step: ")

        # # # pi small step
        self.m_spin_pi_small_step = QPSLDoubleSpinBox(self.m_tab_main,
                                                      value=0.1,
                                                      lower=0.01,
                                                      upper=10000,
                                                      prefix="pi small step: ")

        # # # dm directory
        self.m_dm_directory = QPSLChooseOpenDirButton(
            self.m_tab_main, init_text="choose dm open directory")

        # # # daq save directory
        self.m_daq_directory = QPSLChooseSaveDirButton(
            self.m_tab_main, init_text="choose daq save directory")

        # # # control box
        self.m_control_box = QPSLGroupBox(self.m_tab_main, "control...")
        self.m_layout_control_box = QPSLGridLayout(self.m_control_box)

        # # # # start/stop control
        self.m_button_start = QPSLToggleButton(self.m_control_box,
                                               closed_text="start",
                                               opened_text="stop")
        self.m_layout_control_box.add_widget(self.m_button_start, 0, 0, 0, 0)

        # # zaber tab
        self.m_tab_zaber = QPSLSplitter(self.m_box_content,
                                        Qt.Orientation.Vertical)
        self.m_box_content.add_tab(self.m_tab_zaber, "zaber")
        self.m_plugin_zaber = ZaberPluginUI(self.m_tab_zaber)

        # # pi tab
        self.m_tab_pi = QPSLSplitter(self.m_box_content,
                                     Qt.Orientation.Vertical)
        self.m_box_content.add_tab(self.m_tab_pi, "pi")
        self.m_plugin_pi = PIPluginUI(self.m_tab_pi)

        # # dm tab
        self.m_tab_dm = QPSLSplitter(self.m_box_content,
                                     Qt.Orientation.Vertical)
        self.m_box_content.add_tab(self.m_tab_dm, "dm")
        self.m_plugin_dm = DMPluginUI(self.m_tab_dm)

        # # daq tab
        self.m_tab_daq = QPSLSplitter(self.m_box_content,
                                      Qt.Orientation.Vertical)
        self.m_box_content.add_tab(self.m_tab_daq, "daq")
        self.m_plugin_daq = DAQPluginUI(self.m_tab_daq)

    @QPSLObjectBase.logger_decorator
    def setupLogic(self):
        self.m_tab_zaber.sig_status.connect(self.m_box_content.sig_status)
        self.m_tab_pi.sig_status.connect(self.m_box_content.sig_status)
        self.m_tab_dm.sig_status.connect(self.m_box_content.sig_status)
        self.m_tab_daq.sig_status.connect(self.m_box_content.sig_status)

        self.m_button_start.sig_open.connect(self.prepare_work)
        self.sig_start_work.connect(self.m_worker.start_work,
                                    Qt.ConnectionType.QueuedConnection)
        self.m_worker.sig_task_started.connect(
            self.m_button_start.set_opened, Qt.ConnectionType.QueuedConnection)
        self.m_worker.sig_task_stopped.connect(
            self.m_button_start.set_closed, Qt.ConnectionType.QueuedConnection)
        self.m_button_start.sig_close.connect(self.stop_work)

        # zaber
        self.m_worker.sig_zaber_move.connect(
            self.m_plugin_zaber.sig_zaber_move,
            Qt.ConnectionType.QueuedConnection)
        self.m_plugin_zaber.sig_zaber_move.connect(
            self.m_worker.sig_zaber_arrive, Qt.ConnectionType.QueuedConnection)

        # pi
        self.m_worker.sig_pi_move.connect(self.m_plugin_pi.sig_pi_move,
                                          Qt.ConnectionType.QueuedConnection)
        self.m_plugin_pi.sig_pi_move.connect(
            self.m_worker.sig_pi_arrive, Qt.ConnectionType.QueuedConnection)

        # dm
        self.m_worker.sig_dm_load.connect(self.m_plugin_dm.send_file,
                                          Qt.ConnectionType.QueuedConnection)
        self.m_plugin_dm.sig_send_over.connect(
            self.m_worker.sig_dm_over, Qt.ConnectionType.QueuedConnection)

        # daq
        self.m_worker.sig_daq_start.connect(self.m_plugin_daq.start_task,
                                            Qt.ConnectionType.QueuedConnection)
        self.m_plugin_daq.sig_report_frame_data.connect(
            self.m_worker.sig_daq_report_data,
            Qt.ConnectionType.QueuedConnection)

        self.m_worker.start_thread()

    @QPSLObjectBase.logger_decorator
    def prepare_work(self):
        zaber_range = [
            self.m_spin_zaber_start.value(),
            self.m_spin_zaber_end.value(),
            self.m_spin_zaber_step.value(),
        ]
        pi_range = [
            self.m_spin_pi_start.value(),
            self.m_spin_pi_end.value(),
            self.m_spin_pi_step.value()
        ]
        pi_small_step = self.m_spin_pi_small_step.value()
        dm_open_files = os.listdir(self.m_dm_directory.m_path)
        daq_save_dir = self.m_daq_directory.m_path
        self.m_state_controller.set_continue()
        self.sig_start_work.emit(zaber_range, pi_range, pi_small_step,
                                 dm_open_files, daq_save_dir)

    @QPSLObjectBase.logger_decorator
    def stop_work(self):
        self.m_state_controller.set_stop()

    @QPSLObjectBase.logger_decorator_args
    def closeEvent(self, event: QCloseEvent):
        self.m_state_controller.set_stop()
        self.m_worker.stop_thread()
        del self.m_worker
        self.m_plugin_zaber.close()
        self.m_plugin_pi.close()
        self.m_plugin_dm.close()
        self.m_plugin_daq.close()
        return super().closeEvent(event)


MainWidget = ZaberPIDMPluginUI
