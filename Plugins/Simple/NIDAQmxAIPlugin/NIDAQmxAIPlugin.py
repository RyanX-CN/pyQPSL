from Tool import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .NIDAQmxAIAPI import *


class NIDAQmxAIPluginWorker(QPSLWorker):
    sig_query_device_list, sig_to_query_device_list, sig_answer_device_list = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(list)
    sig_query_terminal_list, sig_to_query_terminal_list, sig_answer_terminal_list = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(list)
    sig_query_channel_list, sig_to_query_channel_list, sig_answer_channel_list = pyqtSignal(
        str, int), pyqtSignal(str, int), pyqtSignal(list, int)
    sig_init_task, sig_to_init_task, sig_task_inited = pyqtSignal(
        list, float, int, float, float,
        int), pyqtSignal(list, float, int, float, float, int), pyqtSignal()
    sig_clear_task, sig_to_clear_task, sig_task_clear = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_start_task, sig_to_start_task, sig_task_started = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_stop_task, sig_to_stop_task, sig_task_stopped = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_to_start_show, sig_show_started = pyqtSignal(), pyqtSignal()
    sig_to_stop_show, sig_show_stopped = pyqtSignal(), pyqtSignal()
    sig_query_buffer_size, sig_to_query_buffer_size, sig_answer_buffer_size = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int)
    sig_set_buffer_size, sig_to_set_buffer_size, sig_buffer_size_set = pyqtSignal(
        int), pyqtSignal(int), pyqtSignal()

    sig_data_read = pyqtSignal(int, np.ndarray)

    def load_attr(self):
        super().load_attr()
        self.m_task = DAQmxAnalogInputTask()
        self.setup_logic()
        return self

    def to_delete(self):
        if self.m_task.has_handle():
            self.on_stop_task()
            self.on_clear_task()
        self.sig_data_read.disconnect()
        return super().to_delete()

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_query_device_list,
                                 self.sig_query_device_list,
                                 self.on_query_device)
        connect_asynch_and_synch(self.sig_to_query_terminal_list,
                                 self.sig_query_terminal_list,
                                 self.on_query_terminal)
        connect_asynch_and_synch(self.sig_to_query_channel_list,
                                 self.sig_query_channel_list,
                                 self.on_query_channel)
        connect_asynch_and_synch(self.sig_to_init_task, self.sig_init_task,
                                 self.on_init_task)
        connect_asynch_and_synch(self.sig_to_clear_task, self.sig_clear_task,
                                 self.on_clear_task)
        connect_asynch_and_synch(self.sig_to_start_task, self.sig_start_task,
                                 self.on_start_task)
        connect_asynch_and_synch(self.sig_to_stop_task, self.sig_stop_task,
                                 self.on_stop_task)
        connect_asynch_and_synch(self.sig_to_query_buffer_size,
                                 self.sig_query_buffer_size,
                                 self.on_query_buffer_size)
        connect_asynch_and_synch(self.sig_to_set_buffer_size,
                                 self.sig_set_buffer_size,
                                 self.on_set_buffer_size)

        connect_queued(self.sig_to_start_show, self.on_start_show)
        connect_queued(self.sig_to_stop_show, self.on_stop_show)

    @QPSLObjectBase.log_decorator()
    def on_query_device(self):
        error_code, device_name_list, error_buffer = DAQmxGetDeviceList()
        self.sig_answer_device_list.emit(device_name_list)

    @QPSLObjectBase.log_decorator()
    def on_query_terminal(self, device_name: str):
        error_code, terminal_name_list, error_buffer = DAQmxGetTerminalList(
            device_name=device_name)
        self.sig_answer_terminal_list.emit(terminal_name_list)

    @QPSLObjectBase.log_decorator()
    def on_query_channel(self, device_name: str, channel_id: int):
        error_code, channel_name_list, error_buffer = DAQmxGetAIChannelList(
            device_name=device_name)
        self.sig_answer_channel_list.emit(channel_name_list, channel_id)

    @QPSLObjectBase.log_decorator()
    def on_init_task(self, channel_names: List[str], sample_rate: float,
                     sample_number: int, min_val: float, max_val: float,
                     everyn: int):
        self.m_task.init_task(channel_names=channel_names,
                              sample_rate=sample_rate,
                              sample_number=sample_number,
                              min_val=min_val,
                              max_val=max_val)
        self.m_self = py_object(self)
        if everyn:
            self.m_task.register_everyn_callback(
                everyn=everyn,
                callback=NIDAQmxAIPluginWorker.on_everyn_callback,
                callback_data=byref(self.m_self))
        self.m_task.register_done_callback(
            callback=NIDAQmxAIPluginWorker.on_done_callback,
            callback_data=byref(self.m_self))
        self.sig_task_inited.emit()
        self.add_warning("task inited")

    @QPSLObjectBase.log_decorator()
    def on_clear_task(self):
        self.on_stop_task()
        self.m_task.clear_task()
        self.sig_task_clear.emit()
        del self.m_self
        self.add_warning("task cleared")

    @QPSLObjectBase.log_decorator()
    def on_start_task(self):
        self.m_read_per_channel = 0
        self.m_task.start_task()
        self.sig_task_started.emit()
        self.add_warning("task started")

    @QPSLObjectBase.log_decorator()
    def on_stop_task(self):
        self.on_stop_show()
        self.m_task.stop_task()
        self.sig_task_stopped.emit()
        self.add_warning("task stopped")

    @QPSLObjectBase.log_decorator()
    def on_start_show(self):
        self.sig_show_started.emit()

    @QPSLObjectBase.log_decorator()
    def on_stop_show(self):
        self.sig_show_stopped.emit()

    @QPSLObjectBase.log_decorator()
    def on_set_buffer_size(self, buffer_size: int):
        self.m_task.set_buffer_size(buffer_size=buffer_size)
        self.sig_buffer_size_set.emit()
        self.add_warning("buffer size set {0}".format(buffer_size))

    @QPSLObjectBase.log_decorator()
    def on_query_buffer_size(self):
        error_code, buffer_size = self.m_task.get_buffer_size()
        self.sig_answer_buffer_size.emit(buffer_size)
        self.add_warning("buffer size = {0}".format(buffer_size.value))

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_uint32, c_void_p)
    def on_everyn_callback(handle: c_void_p, event_type: c_int32,
                           n_sample: c_uint32, callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQmxAIPluginWorker
        code, arr2d = self.m_task.read_data(read_per_channel=n_sample)
        self.sig_data_read.emit(self.m_read_per_channel, arr2d)
        self.m_read_per_channel += arr2d.shape[1]
        return code

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_void_p)
    def on_done_callback(handle: c_void_p, status: c_int32,
                         callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQmxAIPluginWorker
        self.on_stop_task()
        return status


class NIDAQmxAIPluginUI(QPSLHFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()
        self.m_worker = NIDAQmxAIPluginWorker()

    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self

    def to_delete(self):
        self.m_worker.stop_thread()
        self.m_worker.to_delete()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()

    def get_named_widgets(self):
        self.box_device: QPSLHFrameList = self.findChild(
            QPSLHFrameList, "box_device")
        self.button_device: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_device")
        self.combobox_device: QPSLComboBox = self.findChild(
            QPSLComboBox, "combobox_device")
        self.button_terminal: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_terminal")
        self.combobox_terminal: QPSLComboBox = self.findChild(
            QPSLComboBox, "combobox_terminal")
        self.spin_sample_rate: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_sample_rate")
        self.spin_sample_number: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_sample_number")
        self.spin_min_val: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_min_val")
        self.spin_max_val: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_max_val")
        self.area_channels: QPSLVScrollArea = self.findChild(
            QPSLVScrollArea, "area_channels")
        self.button_add_channel: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_add_channel")
        self.button_remove_channel: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_remove_channel")
        self.plot_show: QPSLComboCurvePlotWidget = self.findChild(
            QPSLComboCurvePlotWidget, "plot_show")
        self.toggle_button_init_task: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_init_task")
        self.toggle_button_start_task: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_start_task")
        self.toggle_button_start_show: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_start_show")
        self.spin_everyn: QPSLSpinBox = self.findChild(QPSLSpinBox,
                                                       "spin_everyn")
        self.spin_time_window: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_time_window")

    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()

        connect_direct(self.button_device.sig_clicked,
                       self.m_worker.sig_to_query_device_list)
        connect_queued(self.m_worker.sig_answer_device_list,
                       self.on_get_device_list)
        connect_direct(self.button_terminal.sig_clicked,
                       self.on_click_query_terminal)
        connect_queued(self.m_worker.sig_answer_terminal_list,
                       self.on_get_terminal_list)
        connect_direct(self.button_add_channel.sig_clicked,
                       self.on_click_add_channel)
        connect_direct(self.button_remove_channel.sig_clicked,
                       self.on_click_remove_channel)
        for i, box in enumerate(self.area_channels.get_widgets()):
            button: QPSLPushButton = box.get_widget(0).remove_type()
            connect_direct(button.sig_clicked_str, self.on_click_query_channel)
        connect_queued(self.m_worker.sig_answer_channel_list,
                       self.on_get_channel_list)

        connect_queued(self.m_worker.sig_data_read, self.on_get_data)

        connect_direct(self.toggle_button_init_task.sig_open,
                       self.on_click_init_task)
        connect_queued(self.m_worker.sig_task_inited,
                       self.toggle_button_init_task.set_opened)
        connect_direct(self.toggle_button_init_task.sig_close,
                       self.m_worker.sig_to_clear_task)
        connect_queued(self.m_worker.sig_task_clear,
                       self.toggle_button_init_task.set_closed)
        connect_direct(self.toggle_button_init_task.sig_state_changed,
                       self.on_task_state_changed)

        connect_direct(self.toggle_button_start_task.sig_open,
                       self.on_click_start_task)
        connect_queued(self.m_worker.sig_task_started,
                       self.toggle_button_start_task.set_opened)
        connect_direct(self.toggle_button_start_task.sig_close,
                       self.m_worker.sig_to_stop_task)
        connect_queued(self.m_worker.sig_task_stopped,
                       self.toggle_button_start_task.set_closed)

        connect_direct(self.toggle_button_start_show.sig_open,
                       self.m_worker.sig_to_start_show)
        connect_queued(self.m_worker.sig_show_started,
                       self.toggle_button_start_show.set_opened)
        connect_direct(self.toggle_button_start_show.sig_close,
                       self.m_worker.sig_to_stop_show)
        connect_queued(self.m_worker.sig_show_stopped,
                       self.toggle_button_start_show.set_closed)

        connect_direct(self.spin_time_window.sig_value_changed_to,
                       self.on_time_window_changed)

        self.box_device.installEventFilter(self)
        self.spin_sample_number.setSpecialValueText(" Continuous Sample")
        self.spin_everyn.setSpecialValueText("no callback")
        self.on_task_state_changed(state=False)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_get_device_list(self, device_name_list: List[str]):
        current = None
        if self.combobox_device.count():
            current = self.combobox_device.currentText()
        self.combobox_device.clear()
        self.combobox_device.addItems(device_name_list)
        if current is not None:
            index = device_name_list.index(current)
            self.combobox_device.setCurrentIndex(index)
        else:
            self.combobox_device.setCurrentIndex(0)

    @QPSLObjectBase.log_decorator()
    def on_click_query_terminal(self):
        device_name = self.combobox_device.currentText()
        self.m_worker.sig_to_query_terminal_list.emit(device_name)

    @QPSLObjectBase.log_decorator()
    def on_get_terminal_list(self, terminal_name_list: List[str]):
        current = None
        if self.combobox_terminal.count():
            current = self.combobox_terminal.currentText()
        self.combobox_terminal.clear()
        self.combobox_terminal.addItems(terminal_name_list)
        index = 0
        if current is not None and current in terminal_name_list:
            index = terminal_name_list.index(current)
        self.combobox_terminal.setCurrentIndex(index)

    @QPSLObjectBase.log_decorator()
    def on_click_query_channel(self, channel: str):
        device_name = self.combobox_device.currentText()
        channel_id = int(channel.split()[-1][:-1])
        self.m_worker.sig_to_query_channel_list.emit(device_name, channel_id)

    @QPSLObjectBase.log_decorator()
    def on_get_channel_list(self, channel_name_list: List[str],
                            channel_id: int):
        frame: QPSLHFrameList = self.area_channels.get_widget(channel_id - 1)
        combobox: QPSLComboBox = frame.get_widget(1).remove_type()
        current = None
        if combobox.count():
            current = combobox.currentText()
        combobox.clear()
        combobox.addItems(channel_name_list)
        index = 0
        if current is not None and current in channel_name_list:
            index = channel_name_list.index(current)
        combobox.setCurrentIndex(index)

    @QPSLObjectBase.log_decorator()
    def on_click_add_channel(self):
        index = len(self.area_channels.get_widgets())
        channel_box: QPSLHFrameList = QPSLObjectBase.from_json(
            self.area_channels.get_widget(index - 1).to_json())
        button_channel: QPSLPushButton = channel_box.get_widget(
            0).remove_type()
        button_channel.set_text("Channel {0}:".format(index + 1))
        connect_direct(button_channel.sig_clicked_str,
                       self.on_click_query_channel)
        self.area_channels.add_widget(widget=channel_box)
        self.on_click_query_channel(button_channel.text())
        self.update_channel_box_height()

    @QPSLObjectBase.log_decorator()
    def on_click_remove_channel(self):
        if len(self.area_channels.get_widgets()) == 1:
            raise BaseException("can't remove last channel")
        self.area_channels.remove_widget(
            widget=self.area_channels.get_widgets()[-1])

    @QPSLObjectBase.log_decorator()
    def on_click_init_task(self):
        channels = []
        for box in self.area_channels.get_widgets():
            combobox: QPSLComboBox = box.get_widget(1).remove_type()
            channels.append(combobox.currentText())
        sample_rate = self.spin_sample_rate.value()
        sample_number = self.spin_sample_number.value()
        min_val = self.spin_min_val.value()
        max_val = self.spin_max_val.value()
        everyn = self.spin_everyn.value()
        self.m_worker.sig_to_init_task.emit(channels, sample_rate,
                                            sample_number, min_val, max_val,
                                            everyn)
        while len(self.plot_show.get_deques()) < len(channels):
            self.plot_show.add_deque(deque=QPSLCurveDeque().load_attr(
                deque_name="series {0}".format(
                    len(self.plot_show.get_deques()) + 1)))
        if self.spin_sample_number.value():
            limit = (self.spin_sample_number.value() +
                     self.spin_everyn.value() - 1) // self.spin_everyn.value()
        else:
            limit = 9999
        capacity = round(self.spin_time_window.value() *
                         self.spin_sample_rate.value() /
                         self.spin_everyn.value())
        for i in range(len(channels)):
            self.plot_show.get_deque(index=i).set_capacity(
                capacity=min(capacity, limit))

    @QPSLObjectBase.log_decorator()
    def on_click_start_task(self):
        self.m_worker.sig_to_start_task.emit()
        self.plot_show.clear_data()
        self.plot_show.plot_widget.setYRange(self.spin_min_val.value(),
                                             self.spin_max_val.value())

    @QPSLObjectBase.log_decorator()
    def on_time_window_changed(self, window: float):
        if self.spin_sample_number.value():
            limit = (self.spin_sample_number.value() +
                     self.spin_everyn.value() - 1) // self.spin_everyn.value()
        else:
            limit = 9999
        capacity = round(self.spin_time_window.value() *
                         self.spin_sample_rate.value() /
                         self.spin_everyn.value())
        if self.toggle_button_init_task.get_state():
            for i in range(len(self.area_channels.get_widgets())):
                self.plot_show.get_deque(index=i).set_capacity(
                    capacity=min(capacity, limit))

    @QPSLObjectBase.log_decorator()
    def on_get_data(self, index: int, data_y: np.ndarray):
        if not self.toggle_button_start_show.get_state():
            return
        interval = 1 / self.spin_sample_rate.value()
        length = data_y.shape[1]
        data_x = np.linspace(start=index * interval,
                             stop=(index + length) * interval,
                             num=length,
                             endpoint=False)
        for i, row in enumerate(data_y):
            self.plot_show.get_deque(i).append_data(x=data_x, y=row)

    @QPSLObjectBase.log_decorator()
    def on_task_state_changed(self, state: bool):
        if self.get_widgets():
            self.get_widget(0).setEnabled(not state)
        self.toggle_button_start_task.setEnabled(state)
        self.toggle_button_start_show.setEnabled(state)
        self.spin_everyn.setEnabled(not state)
        self.plot_show.button_add_deque.setEnabled(not state)
        self.plot_show.button_remove_deque.setEnabled(not state)

    def update_channel_box_height(self):
        height = self.box_device.height()
        for w in self.area_channels.get_widgets():
            w.setFixedHeight(height)

    def eventFilter(self, obj: QPSLHFrameList, ev: QEvent) -> bool:
        if obj == self.box_device and ev.type() == QEvent.Type.Resize:
            self.update_channel_box_height()
        return super().eventFilter(obj, ev)


MainWidget = NIDAQmxAIPluginUI