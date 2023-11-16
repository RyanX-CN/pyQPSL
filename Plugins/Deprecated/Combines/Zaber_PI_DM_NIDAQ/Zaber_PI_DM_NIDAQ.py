from Plugins.ZaberPlugin.ZaberPlugin import MainWidget as ZaberWidget
from Plugins.PIPlugin.PIPlugin import MainWidget as PIWidget
from Plugins.DMPlugin.DMPlugin import MainWidget as DMWidget
from Plugins.NIDAQGalvanoPlugin.NIDAQGalvanoPlugin import MainWidget as GalvanoWidget
from Plugins.NIDAQAIPlugin.NIDAQAIPlugin import MainWidget as AIWidget
from Tool import *


class Zaber_PI_DM_NIDAQ_Worker(QPSLWorker):
    sig_startted = pyqtSignal()
    sig_stopped = pyqtSignal()
    sig_zaber_move = pyqtSignal(float)
    sig_report_zaber_position = pyqtSignal(int, float)
    sig_pi_move = pyqtSignal(float)
    sig_report_pi_position = pyqtSignal(int, float)
    sig_pi_small_move = pyqtSignal(float)
    sig_report_pi_small_position = pyqtSignal(int, float)

    def __init__(self, parent: QObject, object_name: str):
        super().__init__(parent=parent, object_name=object_name)

    def to_delete(self):
        if hasattr(self, "m_state_controller"
                   ) and self.m_state_controller.is_continue():
            self.stop_work()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def get_para_dict(self, para_dict: Dict):
        self.m_para_dict = para_dict
        self.m_zaber_range: np.ndarray = self.m_para_dict['zaber_range']
        self.m_pi_range: np.ndarray = self.m_para_dict['pi_range']
        self.m_pi_small_range: np.ndarray = self.m_para_dict['pi_small_range']
        self.m_state_controller: SharedStateController = self.m_para_dict[
            'state_controller']

    @QPSLObjectBase.log_decorator()
    def start_work(self):

        def func():
            for zaber_index, zaber_position in enumerate(self.m_zaber_range):
                if self.m_state_controller.reply_if_stop():
                    return
                self.sig_zaber_move.emit(zaber_position)
                self.sig_report_zaber_position.emit(zaber_index,
                                                    zaber_position)
                for pi_index, pi_position in enumerate(self.m_pi_range):
                    if self.m_state_controller.reply_if_stop():
                        return
                    self.sig_pi_move.emit(pi_position)
                    self.sig_report_pi_position.emit(pi_index, pi_position)
                    for pi_small_index, pi_small_position in enumerate(
                            self.m_pi_small_range):
                        if self.m_state_controller.reply_if_stop():
                            return
                        self.sig_pi_small_move.emit(pi_position +
                                                    pi_small_position)
                        self.sig_report_pi_small_position.emit(
                            pi_small_index, pi_position + pi_small_position)
            self.m_state_controller.set_stop()
            self.sig_stopped.emit()

        QThreadPool.globalInstance().start(func)
        self.sig_startted.emit()

    @QPSLObjectBase.log_decorator()
    def stop_work(self):
        if self.m_state_controller.is_continue():
            self.m_state_controller.set_stop_until_reply()
        self.sig_stopped.emit()


class Zaber_PI_DM_NIDAQ_UI(QPSLTabWidget):
    sig_worker_delete = pyqtSignal()
    sig_set_para_dict, sig_to_set_para_dict = pyqtSignal(dict), pyqtSignal(
        dict)
    sig_start, sig_to_start = pyqtSignal(), pyqtSignal()
    sig_stop, sig_to_stop = pyqtSignal(), pyqtSignal()

    # sig_close, sig_to_close = pyqtSignal(), pyqtSignal()
    # sig_load_map, sig_to_load_map = pyqtSignal(), pyqtSignal()
    # sig_send_single_value, sig_to_send_single_value = pyqtSignal(
    #     float), pyqtSignal(float)
    # sig_send_array_value, sig_to_send_array_value = pyqtSignal(
    #     list), pyqtSignal(list)

    def __init__(self,
                 parent: QWidget,
                 object_name="zpdg",
                 virtual_mode: bool = False):
        super().__init__(parent=parent, object_name=object_name)
        self.m_virtual_mode = virtual_mode
        self.m_worker = Zaber_PI_DM_NIDAQ_Worker(self, object_name="worker")
        self.setupUi()
        self.setupStyle()
        self.setupLogic()
        self.init()
        self.m_worker.start_thread()

    def to_delete(self):
        self.sig_worker_delete.emit()
        self.m_worker.stop_thread()
        self.tab_zaber.to_delete()
        self.tab_pi.to_delete()
        self.tab_dm.to_delete()
        self.tab_galvano.to_delete()
        self.tab_ai.to_delete()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def setupUi(self):
        self.add_tab(tab=QPSLHorizontalGroupList(self, object_name="control"),
                     title="control")
        self.add_tab(tab=ZaberWidget(self, virtual_mode=self.m_virtual_mode),
                     title="zaber")
        self.add_tab(tab=PIWidget(self, virtual_mode=self.m_virtual_mode),
                     title="pi")
        self.add_tab(tab=DMWidget(self, virtual_mode=self.m_virtual_mode),
                     title="dm")
        self.add_tab(tab=GalvanoWidget(self, virtual_mode=self.m_virtual_mode),
                     title="galvano")
        self.add_tab(tab=AIWidget(self, virtual_mode=self.m_virtual_mode),
                     title="ai")
        self.tab_control.add_widget(widget=QPSLVerticalGroupList(
            self.tab_control, object_name="box_config"))
        self.tab_control.add_widget(widget=QPSLVerticalGroupList(
            self.tab_control, object_name="box_control"))

        def setup_config():
            self.box_config.add_widget(widget=QPSLHorizontalGroupList(
                self.box_config, object_name="box_zaber_config"))
            self.box_config.add_widget(widget=QPSLGridGroupList(
                self.box_config, object_name="box_pi_config"))
            self.box_config.add_widget(widget=QPSLHorizontalGroupList(
                self.box_config, object_name="box_dm_config"))
            self.box_config.add_widget(widget=QPSLHorizontalGroupList(
                self.box_config, object_name="box_nidaq_config"))

            def setup_config_zaber():
                self.box_config_zaber.add_widget(
                    widget=QPSLLabel(self.box_config_zaber,
                                     object_name="label_config_zaber",
                                     text="zaber task:"))
                self.box_config_zaber.add_widget(widget=QPSLFloatRangeTaskBox(
                    self.box_config_zaber,
                    object_name="box_zaber_range_task",
                    min=0,
                    max=25400,
                    step_num=10))
                self.box_config_zaber.set_stretch(sizes=(1, 7))

            def setup_config_pi():
                self.box_config_pi.add_widget_simple(widget=QPSLLabel(
                    self.box_config_pi,
                    object_name="label_config_pi",
                    text="pi task:"),
                                                     grid=(0, 0, 0, 0))
                self.box_config_pi.add_widget_simple(
                    widget=QPSLFloatRangeTaskBox(
                        self.box_config_pi,
                        object_name="box_pi_range_task",
                        min=-1,
                        max=1,
                        step_num=10),
                    grid=(0, 0, 1, 2))
                self.box_config_pi.add_widget_simple(widget=QPSLSpinBox(
                    self.box_config_pi,
                    object_name="spin_pi_small_step_num",
                    min=1,
                    max=1000,
                    value=2,
                    prefix="pi step num within each pi interval:"),
                                                     grid=(1, 1, 0, 1))
                self.box_config_pi.add_widget_simple(widget=QPSLLabel(
                    self.box_config_pi, object_name="label_pi_small_step_dis"),
                                                     grid=(1, 1, 2, 2))
                self.box_config_pi.set_stretch(row_sizes=(1, 1),
                                               column_sizes=(1, 3, 4))
                self.update_pi_small_step()

            def setup_config_dm():
                self.box_config_dm.add_widget(
                    widget=QPSLGetDirectoryBox(self.box_config_dm,
                                               object_name="box_getdmdir",
                                               text="DM dir:"))
                self.box_config_dm.add_widget(
                    widget=QPSLTextLabel(self.box_config_dm,
                                         object_name="label_dmdir",
                                         frame_shape=QFrame.Shape.NoFrame))
                self.box_config_dm.set_stretch(sizes=(2, 3))

            def setup_config_galvano():
                self.box_config_nidaq.add_widget(
                    widget=QPSLSpinBox(self.box_config_nidaq,
                                       object_name="spin_galvano_row",
                                       min=1,
                                       max=1000,
                                       value=500,
                                       prefix="row:"))
                self.box_config_nidaq.add_widget(
                    widget=QPSLSpinBox(self.box_config_nidaq,
                                       object_name="spin_galvano_column",
                                       min=1,
                                       max=1000,
                                       value=500,
                                       prefix="col:"))
                self.box_config_nidaq.add_widget(
                    widget=QPSLSpinBox(self.box_config_nidaq,
                                       object_name="spin_galvano_sample_rate",
                                       min=1,
                                       max=20000000,
                                       value=1000000,
                                       prefix="sample rate:"))

            setup_config_zaber()
            setup_config_pi()
            setup_config_dm()
            setup_config_galvano()
            self.box_config.set_stretch(sizes=(1, 2, 1, 1))

        def setup_control():
            self.box_control.add_widget(widget=QPSLProgressBar(
                self.box_control, object_name="prog_zaber"))
            self.box_control.add_widget(widget=QPSLProgressBar(
                self.box_control, object_name="prog_pi"))
            self.box_control.add_widget(widget=QPSLProgressBar(
                self.box_control, object_name="prog_pi_small"))
            self.box_control.add_widget(widget=QPSLProgressBar(
                self.box_control, object_name="prog_dm"))
            self.box_control.add_widget(widget=QPSLProgressBar(
                self.box_control, object_name="prog_nidaq"))
            self.box_control.add_widget(
                widget=QPSLToggleButton(self.box_control,
                                        object_name="btn_switch",
                                        closed_text="start",
                                        opened_text="stop"))

        setup_config()
        setup_control()
        self.tab_control.set_stretch(sizes=(3, 1))

        def old():
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
            self.m_spin_pi_small_step = QPSLDoubleSpinBox(
                self.m_tab_main,
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
            self.m_layout_control_box.add_widget(self.m_button_start, 0, 0, 0,
                                                 0)

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

    @QPSLObjectBase.log_decorator()
    def setupStyle(self):
        self.label_dmdir.update_background_palette(color="#ffffff")

    @QPSLObjectBase.log_decorator()
    def setupLogic(self):
        connect_blocked(self.sig_worker_delete, self.m_worker.to_delete)

        # synch/asynch
        connect_queued_and_blocked(self.sig_set_para_dict,
                                   self.sig_to_set_para_dict,
                                   self.m_worker.get_para_dict)
        connect_queued_and_blocked(self.sig_to_start, self.sig_start,
                                   self.m_worker.start_work)
        connect_queued_and_blocked(self.sig_to_stop, self.sig_stop,
                                   self.m_worker.stop_work)

        connect_direct(self.box_pi_range_task.sig_value_changed,
                       self.update_pi_small_step)
        connect_direct(self.spin_pi_small_step_num.valueChanged,
                       self.update_pi_small_step)
        connect_direct(self.box_dmdir_selector.sig_path_changed,
                       self.label_dmdir.setText)

        connect_direct(self.btn_switch.sig_open, self.start_work)
        connect_direct(self.m_worker.sig_startted, self.btn_switch.set_opened)
        connect_queued(self.m_worker.sig_startted, self.on_work_started)
        connect_direct(self.btn_switch.sig_close, self.stop_work)
        connect_direct(self.m_worker.sig_stopped, self.btn_switch.set_closed)
        connect_queued(self.m_worker.sig_startted, self.on_work_stopped)

        # zaber
        connect_blocked(self.m_worker.sig_zaber_move,
                        self.tab_zaber.move_absolute_micrometer_and_wait)
        connect_queued(self.m_worker.sig_report_zaber_position,
                       self.set_zaber_prog)

        # pi
        connect_blocked(self.m_worker.sig_pi_move,
                        self.tab_pi.sig_move_absolute)
        connect_queued(self.m_worker.sig_report_pi_position, self.set_pi_prog)

        # pi small
        connect_queued(self.m_worker.sig_report_pi_small_position,
                       self.set_pi_small_prog)

        def old():

            self.m_button_start.sig_open.connect(self.prepare_work)
            self.sig_start_work.connect(self.m_worker.start_work,
                                        Qt.ConnectionType.QueuedConnection)
            self.m_worker.sig_task_started.connect(
                self.m_button_start.set_opened,
                Qt.ConnectionType.QueuedConnection)
            self.m_worker.sig_task_stopped.connect(
                self.m_button_start.set_closed,
                Qt.ConnectionType.QueuedConnection)
            self.m_button_start.sig_close.connect(self.stop_work)

            # zaber
            self.m_worker.sig_zaber_move.connect(
                self.m_plugin_zaber.sig_zaber_move,
                Qt.ConnectionType.QueuedConnection)
            self.m_plugin_zaber.sig_zaber_move.connect(
                self.m_worker.sig_zaber_arrive,
                Qt.ConnectionType.QueuedConnection)

            # pi
            self.m_worker.sig_pi_move.connect(
                self.m_plugin_pi.sig_pi_move,
                Qt.ConnectionType.QueuedConnection)
            self.m_plugin_pi.sig_pi_move.connect(
                self.m_worker.sig_pi_arrive,
                Qt.ConnectionType.QueuedConnection)

            # dm
            self.m_worker.sig_dm_load.connect(
                self.m_plugin_dm.send_file, Qt.ConnectionType.QueuedConnection)
            self.m_plugin_dm.sig_send_over.connect(
                self.m_worker.sig_dm_over, Qt.ConnectionType.QueuedConnection)

            # daq
            self.m_worker.sig_daq_start.connect(
                self.m_plugin_daq.start_task,
                Qt.ConnectionType.QueuedConnection)
            self.m_plugin_daq.sig_report_frame_data.connect(
                self.m_worker.sig_daq_report_data,
                Qt.ConnectionType.QueuedConnection)

            self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def init(self):
        self.box_dmdir_selector.set_path("./Plugins/DMPlugin/resources/Shapes")

    @QPSLObjectBase.log_decorator()
    def update_pi_small_step(self, *args):
        interval_length = self.box_pi_range_task.get_interval_length()
        self.label_pi_small_step_dis.setText(
            "pi step distance within each pi interval:{0:.6f}".format(
                interval_length / self.spin_pi_small_step_num.value()))

    @QPSLObjectBase.log_decorator()
    def prepare_work(self) -> bool:
        if not self.tab_zaber.is_ready():
            self.setCurrentWidget(self.tab_zaber)
            self.add_error("zaber plugin is not ready!!!")
            return False
        if not self.tab_pi.is_ready():
            self.setCurrentWidget(self.tab_pi)
            self.add_error("pi plugin is not ready!!!")
            return False
        if not self.tab_dm.is_ready():
            self.setCurrentWidget(self.tab_dm)
            self.add_error("dm plugin is not ready!!!")
            return False

        zaber_range = self.box_zaber_range_task.get_values()
        pi_range = self.box_pi_range_task.get_values()
        pi_small_ranges = np.linspace(start=0,
                                      stop=pi_range[1] - pi_range[0],
                                      num=self.spin_pi_small_step_num.value(),
                                      endpoint=False)
        dm_file_path = self.box_dmdir_selector.get_path()
        row = self.spin_nidaq_row.value()
        column = self.spin_nidaq_column.value()
        sample_rate = self.spin_nidaq_sample_rate.value()

        self.m_para_dict = dict()
        self.m_para_dict['zaber_range'] = zaber_range
        self.m_para_dict['pi_range'] = pi_range
        self.m_para_dict['pi_small_range'] = pi_small_ranges
        self.m_para_dict['dm_file_path'] = dm_file_path
        self.m_para_dict['row'] = row
        self.m_para_dict['column'] = column
        self.m_para_dict['sample_rate'] = sample_rate
        self.m_para_dict['state_controller'] = SharedStateController(
            value=SharedStateController.State.Continue)
        self.sig_set_para_dict.emit(self.m_para_dict)
        return True

    @QPSLObjectBase.log_decorator()
    def start_work(self):
        if self.prepare_work():
            self.sig_to_start.emit()

    @QPSLObjectBase.log_decorator()
    def on_work_started(self):
        self.prog_zaber.setRange(0, len(self.m_para_dict['zaber_range']))
        self.prog_zaber.setValue(0)
        self.prog_pi.setRange(0, len(self.m_para_dict['pi_range']))
        self.prog_pi.setValue(0)
        self.prog_pi_small.setRange(0, len(self.m_para_dict['pi_small_range']))
        self.prog_pi_small.setValue(0)

    @QPSLObjectBase.log_decorator()
    def stop_work(self):
        self.sig_to_stop.emit()

    @QPSLObjectBase.log_decorator()
    def on_work_stopped(self):
        pass

    @QPSLObjectBase.log_decorator()
    def set_zaber_prog(self, zaber_index: int, zaber_position: float):
        self.prog_zaber.setValue(zaber_index + 1)
        self.prog_zaber.setFormat(
            "zaber position: {0}\n%p%".format(zaber_position))

    @QPSLObjectBase.log_decorator()
    def set_pi_prog(self, pi_index: int, pi_position: float):
        self.prog_pi.setValue(pi_index + 1)
        self.prog_pi.setFormat("pi position: {0}\n%p%".format(pi_position))

    @QPSLObjectBase.log_decorator()
    def set_pi_small_prog(self, pi_small_index: int, pi_small_position: float):
        self.prog_pi_small.setValue(pi_small_index + 1)
        self.prog_pi_small.setFormat(
            "pi' position: {0}\n%p%".format(pi_small_position))

    @property
    def tab_control(self) -> QPSLHorizontalGroupList:
        return self.get_tab(0)

    @property
    def box_config(self) -> QPSLVerticalGroupList:
        return self.tab_control.get_widget(0)

    @property
    def box_control(self) -> QPSLVerticalGroupList:
        return self.tab_control.get_widget(1)

    @property
    def box_config_zaber(self) -> QPSLHorizontalGroupList:
        return self.box_config.get_widget(0)

    @property
    def box_zaber_range_task(self) -> QPSLFloatRangeTaskBox:
        return self.box_config_zaber.get_widget(1)

    @property
    def box_config_pi(self) -> QPSLGridGroupList:
        return self.box_config.get_widget(1)

    @property
    def box_pi_range_task(self) -> QPSLFloatRangeTaskBox:
        return self.box_config_pi.get_widget(1)

    @property
    def spin_pi_small_step_num(self) -> QPSLSpinBox:
        return self.box_config_pi.get_widget(2)

    @property
    def label_pi_small_step_dis(self) -> QPSLLabel:
        return self.box_config_pi.get_widget(3)

    @property
    def box_config_dm(self) -> QPSLHorizontalGroupList:
        return self.box_config.get_widget(2)

    @property
    def box_dmdir_selector(self) -> QPSLGetDirectoryBox:
        return self.box_config_dm.get_widget(0)

    @property
    def label_dmdir(self) -> QPSLLabel:
        return self.box_config_dm.get_widget(1)

    @property
    def box_config_nidaq(self) -> QPSLHorizontalGroupList:
        return self.box_config.get_widget(3)

    @property
    def spin_nidaq_row(self) -> QPSLSpinBox:
        return self.box_config_nidaq.get_widget(0)

    @property
    def spin_nidaq_column(self) -> QPSLSpinBox:
        return self.box_config_nidaq.get_widget(1)

    @property
    def spin_nidaq_sample_rate(self) -> QPSLDoubleSpinBox:
        return self.box_config_nidaq.get_widget(2)

    @property
    def prog_zaber(self) -> QPSLProgressBar:
        return self.box_control.get_widget(0)

    @property
    def prog_pi(self) -> QPSLProgressBar:
        return self.box_control.get_widget(1)

    @property
    def prog_pi_small(self) -> QPSLProgressBar:
        return self.box_control.get_widget(2)

    @property
    def prog_dm(self) -> QPSLProgressBar:
        return self.box_control.get_widget(3)

    @property
    def prog_nidaq(self) -> QPSLProgressBar:
        return self.box_control.get_widget(4)

    @property
    def btn_switch(self) -> QPSLToggleButton:
        return self.box_control.get_widget(5)

    @property
    def tab_zaber(self) -> ZaberWidget:
        return self.get_tab(1)

    @property
    def tab_pi(self) -> PIWidget:
        return self.get_tab(2)

    @property
    def tab_dm(self) -> DMWidget:
        return self.get_tab(3)

    @property
    def tab_galvano(self) -> GalvanoWidget:
        return self.get_tab(4)

    @property
    def tab_ai(self) -> AIWidget:
        return self.get_tab(5)


MainWidget = Zaber_PI_DM_NIDAQ_UI
