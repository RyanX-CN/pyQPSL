from Tool import *

os_path_append("./Plugins/NIDAQAOPlugin/bin")
from Plugins.NIDAQAOPlugin.NIDAQAOAPI import *


class NIDAQGalvanoPluginWorker(QPSLWorker):
    sig_answer_device_list = pyqtSignal(list)
    sig_answer_terminal_list = pyqtSignal(list)
    sig_answer_channel_list = pyqtSignal(list)
    sig_task_inited = pyqtSignal()
    sig_task_cleared = pyqtSignal()
    sig_task_startted = pyqtSignal()
    sig_task_stopped = pyqtSignal()
    sig_write_data = pyqtSignal(int, np.ndarray)

    def __init__(self, parent: QWidget, object_name: str, virtual_mode: bool):
        super(NIDAQGalvanoPluginWorker, self).__init__(parent=parent,
                                                       object_name=object_name)
        self.m_task = DAQmxAnalogOutputTask()

    def to_delete(self):
        if self.m_task.has_handle():
            self.stop_task()
            self.clear_task()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def on_query_device(self):
        self.sig_answer_device_list.emit(DAQmxGetDeviceList()[1])

    @QPSLObjectBase.log_decorator()
    def on_query_terminal(self, device_name: str):
        res, terminals, err = DAQmxGetTerminalList(device_name=device_name)
        self.sig_answer_terminal_list.emit(terminals)

    @QPSLObjectBase.log_decorator()
    def on_query_channel(self, device_name: str):
        self.sig_answer_channel_list.emit(
            DAQmxGetAOChannelList(device_name=device_name)[1])

    @QPSLObjectBase.log_decorator()
    def init_task(self, channel_x: Tuple[str, float,
                                         float], channel_y: Tuple[str, float,
                                                                  float],
                  trigger_source: str, sample_rate: float, sample_number: int,
                  everyn: int, arr_x: np.ndarray, arr_y: np.ndarray):
        c_channels = (DAQmxAnalogOutputChannel * 2)()
        c_channels[0].physical_channel_name = channel_x[0].encode('utf8')
        c_channels[0].min_val = channel_x[1]
        c_channels[0].max_val = channel_x[2]
        c_channels[1].physical_channel_name = channel_y[0].encode('utf8')
        c_channels[1].min_val = channel_y[1]
        c_channels[1].max_val = channel_y[2]
        self.m_task.channels = c_channels
        self.m_task.channel_number = 2
        self.m_task.trigger_source = trigger_source.encode(encoding='utf8')
        self.m_task.sample_rate = sample_rate
        if sample_number:
            self.m_task.sample_mode = DAQmx_Val_FiniteSamps
        else:
            self.m_task.sample_mode = DAQmx_Val_ContSamps
        self.m_task.sample_per_channel = len(arr_x)
        self.m_task.init_task()
        self.m_arr2d = np.vstack((arr_x, arr_y))
        self.m_task.write_data(arr2d=self.m_arr2d)
        self.m_self = py_object(self)
        if everyn:
            self.m_task.register_everyn_callback(
                everyn=everyn,
                callback=NIDAQGalvanoPluginWorker.everyn_callback,
                callback_data=byref(self.m_self))
        self.m_task.register_done_callback(
            callback=NIDAQGalvanoPluginWorker.done_callback,
            callback_data=byref(self.m_self))
        self.sig_task_inited.emit()

    @QPSLObjectBase.log_decorator()
    def clear_task(self):
        self.m_task.clear_task()
        self.sig_task_cleared.emit()
        del self.m_self
        del self.m_arr2d

    @QPSLObjectBase.log_decorator()
    def start_task(self):
        self.m_writen_per_channel = 0
        self.m_task.start_task()
        self.sig_task_startted.emit()

    @QPSLObjectBase.log_decorator()
    def stop_task(self):
        self.m_task.stop_task()
        self.sig_task_stopped.emit()

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_uint32, c_void_p)
    def everyn_callback(handle: c_void_p, event_type: c_int32,
                        n_sample: c_uint32, callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQGalvanoPluginWorker
        index = self.m_writen_per_channel % self.m_arr2d.shape[1]
        self.sig_write_data.emit(self.m_writen_per_channel,
                                 self.m_arr2d[:, index:index + n_sample])
        self.m_writen_per_channel += n_sample
        return 0

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_void_p)
    def done_callback(handle: c_void_p, status: c_int32,
                      callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQGalvanoPluginWorker
        self.stop_task()
        return status


class NIDAQGalvanoPluginUI(QPSLTabWidget):
    sig_worker_delete = pyqtSignal()
    sig_query_device, sig_to_query_device = pyqtSignal(), pyqtSignal()
    sig_query_terminal, sig_to_query_terminal = pyqtSignal(str), pyqtSignal(
        str)
    sig_query_channel, sig_to_query_channel = pyqtSignal(str), pyqtSignal(str)
    sig_init_task, sig_to_init_task = pyqtSignal(
        tuple, tuple, str, float, int, int, np.ndarray,
        np.ndarray), pyqtSignal(tuple, tuple, str, float, int, int, np.ndarray,
                                np.ndarray)
    sig_clear_task, sig_to_clear_task = pyqtSignal(), pyqtSignal()
    sig_start_task, sig_to_start_task = pyqtSignal(), pyqtSignal()
    sig_stop_task, sig_to_stop_task = pyqtSignal(), pyqtSignal()
    sig_write_data = pyqtSignal(int, np.ndarray)

    def __init__(self,
                 parent: QWidget,
                 object_name="NIDAQGalvano",
                 virtual_mode=False,
                 font_family="Arial"):
        super(NIDAQGalvanoPluginUI, self).__init__(parent=parent,
                                                   object_name=object_name)
        self.m_font_family = font_family
        self.m_worker = NIDAQGalvanoPluginWorker(self,
                                                 object_name="worker",
                                                 virtual_mode=virtual_mode)
        self.setupUi()
        self.setupStyle()
        self.setupLogic()
        self.on_nidaq_task_state_changed(False)
        self.m_worker.start_thread()
        self.init()

    def to_delete(self):
        self.sig_worker_delete.emit()
        self.m_worker.stop_thread()
        self.graph.stop_work()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def setupUi(self):

        def setup_config_page():
            self.add_tab(tab=QPSLVerticalGroupList(self, object_name="tab_config"),
                         title="config")
            self.tab_config.add_widget(widget=QPSLNIDAQTaskBox(
                self.tab_config, object_name="box_task"))
            self.tab_config.add_widget(widget=QPSLHorizontalGroupList(
                self.tab_config, object_name="box_channels"))
            self.box_channels.add_widget(
                widget=QPSLNIDAQChannelBox(self.box_channels,
                                           object_name="box_channel_x",
                                           text="channel x:"))
            self.box_channels.add_widget(
                widget=QPSLNIDAQChannelBox(self.box_channels,
                                           object_name="box_channel_y",
                                           text="channel y:"))
            self.tab_config.set_stretch(sizes=(2, 2, 5))

        def setup_wavemaker_pages():
            self.add_tab(tab=QPSLWaveMaker(self, object_name="wavemaker_x"),
                         title="wavemaker_x")
            self.add_tab(tab=QPSLWaveMaker(self, object_name="wavemaker_y"),
                         title="wavemaker_y")

        def setup_control_page():
            self.add_tab(tab=QPSLVerticalGroupList(self, object_name="tab_control"),
                         title="control")
            self.tab_control.add_widget(
                widget=QPSLRotatePlot(self.tab_control, object_name="graph"))
            self.tab_control.add_widget(widget=QPSLHorizontalGroupList(
                self.tab_control, object_name="box_control"))
            self.box_control.add_widget(
                widget=QPSLSpinBox(self.tab_control,
                                   object_name="spin_everyn",
                                   min=0,
                                   max=20000000,
                                   value=100,
                                   prefix="everyn:"))
            self.spin_everyn.setSpecialValueText("no callback")
            self.box_control.add_widget(
                widget=QPSLToggleButton(self.box_control,
                                        object_name="btn_task",
                                        closed_text="init task",
                                        opened_text="clear task"))
            self.box_control.add_widget(
                widget=QPSLToggleButton(self.box_control,
                                        object_name="btn_switch",
                                        closed_text="start task",
                                        opened_text="stop task"))
            self.box_control.add_widget(
                widget=QPSLToggleButton(self.box_control,
                                        object_name="btn_show",
                                        closed_text="start show",
                                        opened_text="stop show"))
            self.box_control.set_stretch(sizes=(1, 1, 1, 1))
            self.tab_control.set_stretch(sizes=(3, 1))

        setup_config_page()
        setup_wavemaker_pages()
        setup_control_page()

    @QPSLObjectBase.log_decorator()
    def setupStyle(self):
        button_color = "#bbbbbb"
        self.tabBar().setFont(QFont(self.m_font_family, 10))
        self.graph.setFont(QFont(self.m_font_family, 10))
        self.graph.btn_clear.update_background_palette(color=button_color)
        for btn in self.toggle_buttons:
            btn.set_font(font=QFont(self.m_font_family, 10))
        for btn in self.push_buttons:
            btn.set_font(font=QFont(self.m_font_family, 10))
            btn.update_background_palette(color=button_color)
        for spin in self.spins:
            spin.setFont(QFont(self.m_font_family, 10))
        for cbox in self.cboxes:
            cbox.setFont(QFont(self.m_font_family, 10))

    @QPSLObjectBase.log_decorator()
    def setupLogic(self):
        connect_blocked(self.sig_worker_delete, self.m_worker.to_delete)
        # synch/asynch
        connect_queued_and_blocked(self.sig_to_query_device,
                                   self.sig_query_device,
                                   self.m_worker.on_query_device)
        connect_queued_and_blocked(self.sig_to_query_terminal,
                                   self.sig_query_terminal,
                                   self.m_worker.on_query_terminal)
        connect_queued_and_blocked(self.sig_to_query_channel,
                                   self.sig_query_channel,
                                   self.m_worker.on_query_channel)
        connect_queued_and_blocked(self.sig_to_init_task, self.sig_init_task,
                                   self.m_worker.init_task)
        connect_queued_and_blocked(self.sig_to_clear_task, self.sig_clear_task,
                                   self.m_worker.clear_task)
        connect_queued_and_blocked(self.sig_to_start_task, self.sig_start_task,
                                   self.m_worker.start_task)
        connect_queued_and_blocked(self.sig_to_stop_task, self.sig_stop_task,
                                   self.m_worker.stop_task)

        # device channel
        connect_direct(self.box_task.cbox_device.sig_fresh,
                       self.on_btn_query_device_clicked)
        connect_queued(self.m_worker.sig_answer_device_list,
                       self.box_task.cbox_device.set_texts)
        connect_direct(self.box_task.cbox_terminal.sig_fresh,
                       self.on_btn_query_terminal_clicked)
        connect_queued(self.m_worker.sig_answer_terminal_list,
                       self.box_task.cbox_terminal.set_texts)
        connect_direct(self.box_channel_x.cbox_channel.sig_fresh,
                       self.on_btn_query_channel_clicked)
        connect_direct(self.box_channel_y.cbox_channel.sig_fresh,
                       self.on_btn_query_channel_clicked)
        connect_queued(self.m_worker.sig_answer_channel_list,
                       self.box_channel_x.cbox_channel.set_texts)
        connect_queued(self.m_worker.sig_answer_channel_list,
                       self.box_channel_y.cbox_channel.set_texts)

        # task, show, data
        connect_direct(self.btn_task.sig_open, self.on_btn_init_task_clicked)
        connect_queued(self.m_worker.sig_task_inited, self.btn_task.set_opened)
        connect_direct(self.btn_task.sig_close, self.on_btn_clear_task_clicked)
        connect_queued(self.m_worker.sig_task_cleared,
                       self.btn_task.set_closed)
        connect_direct(self.btn_switch.sig_open,
                       self.on_btn_start_task_clicked)
        connect_queued(self.m_worker.sig_task_startted,
                       self.btn_switch.set_opened)
        connect_direct(self.btn_switch.sig_close,
                       self.on_btn_stop_task_clicked)
        connect_queued(self.m_worker.sig_task_stopped,
                       self.btn_switch.set_closed)
        connect_queued(self.m_worker.sig_write_data, self.sig_write_data)
        connect_direct(self.sig_write_data, self.on_data_writen)
        connect_direct(self.btn_show.sig_open, self.graph.start_work)
        connect_direct(self.graph.sig_work_started, self.btn_show.set_opened)
        connect_direct(self.btn_show.sig_close, self.graph.stop_work)
        connect_direct(self.graph.sig_work_stopped, self.btn_show.set_closed)

        # state
        connect_direct(self.btn_task.sig_state_changed,
                       self.on_nidaq_task_state_changed)
        connect_direct(self.btn_switch.sig_state_changed,
                       self.on_nidaq_switch_state_changed)

    @QPSLObjectBase.log_decorator()
    def init(self):
        self.sig_query_device.emit()
        QApplication.processEvents()
        assert self.box_task.cbox_device.current_text()
        self.sig_query_terminal.emit(self.box_task.cbox_device.current_text())
        QApplication.processEvents()
        assert self.box_task.cbox_terminal.current_text()
        self.sig_query_channel.emit(self.box_task.cbox_device.current_text())
        QApplication.processEvents()
        assert self.box_channel_x.cbox_channel.current_text()
        assert self.box_channel_y.cbox_channel.current_text()
        self.box_channel_y.cbox_channel.cbox_data.setCurrentIndex(1)
        self.init_bitrapezoid_trapezoid(row=20,
                                        column=20,
                                        dwell=5,
                                        x_min=-1,
                                        x_max=1,
                                        y_min=-1,
                                        y_max=1)

    @QPSLObjectBase.log_decorator()
    def init_bitrapezoid_trapezoid(self, row: int, column: int, dwell: int,
                                   x_min: float, x_max: float, y_min: float,
                                   y_max: float):
        self.tab_wavemaker_x.cbox_wave_type.setCurrentText("bitrapezoid")
        self.tab_wavemaker_x.spin_min.setValue(x_min)
        self.tab_wavemaker_x.spin_max.setValue(x_max)
        self.tab_wavemaker_x.spin_cycle.setValue(dwell * column * 2)
        self.tab_wavemaker_x.spin_phase.setValue(0)
        self.tab_wavemaker_x.spin_para.setValue(column)
        self.tab_wavemaker_x.update_wave()

        self.tab_wavemaker_y.cbox_wave_type.setCurrentText("trapezoid")
        self.tab_wavemaker_y.spin_min.setValue(y_min)
        self.tab_wavemaker_y.spin_max.setValue(y_max)
        self.tab_wavemaker_y.spin_cycle.setValue(dwell * column * row)
        self.tab_wavemaker_y.spin_phase.setValue(0)
        self.tab_wavemaker_y.spin_para.setValue(row)
        self.tab_wavemaker_y.update_wave()

    @QPSLObjectBase.log_decorator()
    def on_btn_query_device_clicked(self):
        self.sig_to_query_device.emit()

    @QPSLObjectBase.log_decorator()
    def on_btn_query_terminal_clicked(self):
        self.sig_to_query_terminal.emit(
            self.box_task.cbox_device.current_text())

    @QPSLObjectBase.log_decorator()
    def on_btn_query_channel_clicked(self):
        self.sig_to_query_channel.emit(
            self.box_task.cbox_device.current_text())

    @QPSLObjectBase.log_decorator()
    def on_btn_init_task_clicked(self):
        channel_x = (self.box_channel_x.cbox_channel.current_text(),
                     self.box_channel_x.spin_min.value(),
                     self.box_channel_x.spin_max.value())
        channel_y = (self.box_channel_y.cbox_channel.current_text(),
                     self.box_channel_y.spin_min.value(),
                     self.box_channel_y.spin_max.value())
        trigger_source = self.box_task.cbox_terminal.current_text()
        sample_rate = self.box_task.spin_sample_rate.value()
        sample_number = self.box_task.spin_sample_number.value()
        everyn = self.spin_everyn.value()
        arr_x = self.tab_wavemaker_x.make_wave()
        arr_y = self.tab_wavemaker_y.make_wave()
        if self.box_task.spin_sample_number.value() == 0:
            lcm = len(arr_x) * len(arr_y) // math.gcd(len(arr_x), len(arr_y))
            if lcm > 100000000:
                raise BaseException(
                    "lcm of all array-lengths is too big! lcm = {0}".format(
                        lcm))
        arr_x = numpy_array_adapt_length(
            array=arr_x,
            length=self.box_task.spin_sample_number.value()
            if self.box_task.spin_sample_number.value() else lcm)
        arr_y = numpy_array_adapt_length(
            array=arr_y,
            length=self.box_task.spin_sample_number.value()
            if self.box_task.spin_sample_number.value() else lcm)
        self.sig_to_init_task.emit(channel_x, channel_y, trigger_source,
                                   sample_rate, sample_number, everyn, arr_x,
                                   arr_y)

    @QPSLObjectBase.log_decorator()
    def on_btn_clear_task_clicked(self):
        self.sig_to_clear_task.emit()

    @QPSLObjectBase.log_decorator()
    def on_btn_start_task_clicked(self):
        self.sig_to_start_task.emit()

    @QPSLObjectBase.log_decorator()
    def on_btn_stop_task_clicked(self):
        self.sig_to_stop_task.emit()

    @QPSLObjectBase.log_decorator()
    def on_nidaq_task_state_changed(self, state: bool):
        for cbox in self.cboxes:
            cbox.setEnabled(not state)
        for btn in self.push_buttons:
            btn.setEnabled(not state)
        for spin in self.spins:
            spin.setEnabled(not state)
        for wave_maker in self.wave_makers:
            wave_maker.setEnabled(not state)
        self.btn_switch.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_nidaq_switch_state_changed(self, state: bool):
        self.btn_task.setEnabled(not state)

    @QPSLObjectBase.log_decorator(level=QPSL_LOG_LEVEL.ALL.value)
    def on_data_writen(self, start_index: int, arr2d: np.ndarray):
        if self.btn_show.get_state():
            interval = 1 / self.box_task.spin_sample_rate.value()
            xs = np.linspace(start=start_index * interval,
                             stop=(start_index + arr2d.shape[1]) * interval,
                             num=arr2d.shape[1],
                             endpoint=False)
            for arr in arr2d:
                self.graph.add_data(x=xs, y=arr)

    @property
    def tab_config(self) -> QPSLVerticalGroupList:
        return self.get_tab(0)

    @property
    def tab_wavemaker_x(self) -> QPSLWaveMaker:
        return self.get_tab(1)

    @property
    def tab_wavemaker_y(self) -> QPSLWaveMaker:
        return self.get_tab(2)

    @property
    def tab_control(self) -> QPSLVerticalGroupList:
        return self.get_tab(-1)

    @property
    def box_task(self) -> QPSLNIDAQTaskBox:
        return self.tab_config.get_widget(0)

    @property
    def box_channels(self) -> QPSLHorizontalGroupList:
        return self.tab_config.get_widget(1)

    @property
    def box_channel_x(self) -> QPSLNIDAQChannelBox:
        return self.box_channels.get_widget(0)

    @property
    def box_channel_y(self) -> QPSLNIDAQChannelBox:
        return self.box_channels.get_widget(1)

    @property
    def graph(self) -> QPSLRotatePlot:
        return self.tab_control.get_widget(0)

    @property
    def box_control(self) -> QPSLHorizontalGroupList:
        return self.tab_control.get_widget(1)

    @property
    def spin_everyn(self) -> QPSLSpinBox:
        return self.box_control.get_widget(0)

    @property
    def btn_task(self) -> QPSLToggleButton:
        return self.box_control.get_widget(1)

    @property
    def btn_switch(self) -> QPSLToggleButton:
        return self.box_control.get_widget(2)

    @property
    def btn_show(self) -> QPSLToggleButton:
        return self.box_control.get_widget(3)

    @property
    def toggle_buttons(self) -> Iterable[QPSLToggleButton]:
        yield from (self.btn_task, self.btn_switch, self.btn_show)

    @property
    def channels(self) -> Iterable[QPSLNIDAQChannelBox]:
        yield from (self.box_channel_x, self.box_channel_y)

    @property
    def push_buttons(self) -> Iterable[QPSLPushButton]:
        yield from self.box_task.push_buttons
        yield from (channel.cbox_channel.btn_fresh
                    for channel in self.channels)

    @property
    def spins(self) -> Iterable[Union[QPSLSpinBox, QPSLDoubleSpinBox]]:
        yield from self.box_task.spins
        yield from (channel.spin_min for channel in self.channels)
        yield from (channel.spin_max for channel in self.channels)
        for wavemaker in self.wave_makers:
            yield from wavemaker.spins
        yield self.spin_everyn

    @property
    def cboxes(self) -> Iterable[QPSLComboBox]:
        yield from map(lambda cbox: cbox.cbox_data, self.box_task.cboxes)
        yield from (channel.cbox_channel.cbox_data
                    for channel in self.channels)
        yield from (wave_maker.cbox_wave_type
                    for wave_maker in self.wave_makers)

    @property
    def wave_makers(self) -> Iterable[QPSLWaveMaker]:
        yield from (self.get_tab(i) for i in range(1, self.count() - 1))


MainWidget = NIDAQGalvanoPluginUI