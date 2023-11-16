from Tool import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .NIDAQmxDOAPI import *


class NIDAQmxDOPluginWorker(QPSLWorker):
    sig_query_device_list, sig_to_query_device_list, sig_answer_device_list = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(list)
    sig_query_terminal_list, sig_to_query_terminal_list, sig_answer_terminal_list = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(list)
    sig_query_line_list, sig_to_query_line_list, sig_answer_line_list = pyqtSignal(
        str, int), pyqtSignal(str, int), pyqtSignal(list, int)
    sig_init_task, sig_to_init_task, sig_task_inited = pyqtSignal(
        list, str, float, int, int, np.ndarray), pyqtSignal(list, str, float, int, int, np.ndarray), pyqtSignal()
    sig_clear_task, sig_to_clear_task, sig_task_clear = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_start_task, sig_to_start_task, sig_task_started = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_stop_task, sig_to_stop_task, sig_task_stopped = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_data_written = pyqtSignal(int, np.ndarray)

    def load_attr(self):
        super().load_attr()
        self.m_task = DAQmxDigitalOutputTask()
        self.m_arr2d: np.ndarray = None
        self.setup_logic()
        return self

    def to_delete(self):
        if self.m_task.has_handle():
            self.on_stop_task()
            self.on_clear_task()
        self.sig_data_written.disconnect()
        return super().to_delete()
    
    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_query_device_list,
                                 self.sig_query_device_list,
                                 self.on_query_device)
        connect_asynch_and_synch(self.sig_to_query_terminal_list,
                                 self.sig_query_terminal_list,
                                 self.on_query_terminal)
        connect_asynch_and_synch(self.sig_to_query_line_list,
                                 self.sig_query_line_list,
                                 self.on_query_line)
        connect_asynch_and_synch(self.sig_to_init_task, self.sig_init_task,
                                 self.on_init_task)
        connect_asynch_and_synch(self.sig_to_clear_task, self.sig_clear_task,
                                 self.on_clear_task)
        connect_asynch_and_synch(self.sig_to_start_task, self.sig_start_task,
                                 self.on_start_task)
        connect_asynch_and_synch(self.sig_to_stop_task, self.sig_stop_task,
                                 self.on_stop_task)
    
    @QPSLObjectBase.log_decorator()
    def on_query_device(self):
        error_code,device_name_list, error_buffer = DAQmxGetDeviceList()
        self.sig_answer_device_list.emit(device_name_list)

    @QPSLObjectBase.log_decorator()
    def on_query_terminal(self, device_name: str):
        error_code, terminal_name_list, error_buffer = DAQmxGetTerminalList(device_name=device_name)
        self.sig_answer_terminal_list.emit(terminal_name_list)
    
    @QPSLObjectBase.log_decorator()
    def on_query_line(self, device_name: str, line_id: int):
        error_code, line_name_list, error_buffer = DAQmxGetDOLineList(
            device_name=device_name)
        self.sig_answer_line_list.emit(line_name_list, line_id)
        
    @QPSLObjectBase.log_decorator()
    def on_init_task(self, channels: List[str],
                  trigger_source: str, sample_rate: float, sample_number: int,
                  everyn: int, arr2d: np.ndarray):
        line_number = len(channels)
        c_lines = (DAQmxDigitalOutputChannel * line_number)()
        for i, (line_name) in enumerate(channels):
            c_lines[i].physical_line_name = line_name.encode('utf8')
        self.m_task.channels = c_lines
        self.m_task.line_number = line_number
        self.m_task.trigger_source = trigger_source.encode(encoding='utf8')
        self.m_task.sample_rate = sample_rate
        if sample_number:
            self.m_task.sample_mode = DAQmx_Val_FiniteSamps
        else:
            self.m_task.sample_mode = DAQmx_Val_ContSamps
        self.m_task.sample_per_channel = arr2d.shape[1]
        self.m_task.init_task()
        self.m_arr2d = arr2d
        self.m_task.write_data(arr2d=arr2d)
        self.m_self = py_object(self)
        if everyn:
            self.m_task.register_everyn_callback(
                everyn=everyn,
                callback=NIDAQmxDOPluginWorker.on_everyn_callback,
                callback_data=byref(self.m_self))
        self.m_task.register_done_callback(
            callback=NIDAQmxDOPluginWorker.on_done_callback,
            callback_data=byref(self.m_self))
        self.sig_task_inited.emit()
        self.add_warning("do task inited")
            
    @QPSLObjectBase.log_decorator()
    def on_clear_task(self):
        self.m_task.clear_task()
        self.sig_task_clear.emit()
        del self.m_self
        del self.m_arr2d
        self.add_warning("do task cleared")

    @QPSLObjectBase.log_decorator()
    def on_start_task(self):
        self.m_writen_per_channel = 0
        self.m_task.start_task()
        self.sig_task_started.emit()
        self.add_warning("do task started")
    
    @QPSLObjectBase.log_decorator()
    def on_stop_task(self):
        self.m_task.stop_task()
        self.sig_task_stopped.emit()
        self.add_warning("do task stopped")

    @QPSLObjectBase.log_decorator()
    def reset(self):
        if self.m_task.has_handle():
            self.on_stop_task()
            self.on_clear_task()
            self.m_task.reset()
        else:
            self.m_task.reset()

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_uint32, c_void_p)
    def on_everyn_callback(handle: c_void_p, event_type: c_int32,
                        n_sample: c_uint32, callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQmxDOPluginWorker
        index = self.m_writen_per_channel % self.m_arr2d.shape[1]
        self.sig_data_written.emit(self.m_writen_per_channel,
                                 self.m_arr2d[:, index:index + n_sample])
        self.m_writen_per_channel += n_sample
        return 0

    @ctypes.WINFUNCTYPE(c_int32, c_void_p, c_int32, c_void_p)
    def on_done_callback(handle: c_void_p, status: c_int32,
                      callback_data: c_void_p):
        self = ctypes.cast(callback_data, POINTER(py_object)).contents.value
        self: NIDAQmxDOPluginWorker
        self.on_stop_task()
        return status

class NIDAQmxDOPluginUI(QPSLVFrameList,QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        generators = json.get("generators")
        if generators is not None:
            for generator_dict in generators:
                if generator_dict is None:
                    self.m_waves.append((None, None))
                else:
                    self.m_waves.append((generator_dict,
                                         QWaveDialog.generate_wave_from_dict(
                                             wave=generator_dict)))
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        generators = []
        for generator, wave in self.m_waves:
            if generator is None:
                generators.append(None)
            else:
                generators.append(generator)
        res.update({"generators": generators})
        return res
           
    def __init__(self):
        super().__init__()
        self.m_worker = NIDAQmxDOPluginWorker()
        self.m_waves: List[Tuple[Dict, np.ndarray]] = []

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
        self.btn_device: QPSLPushButton = self.findChild(QPSLPushButton,
                                                    "btn_device")
        self.cbox_device: QPSLComboBox = self.findChild(QPSLComboBox,
                                                        "cbox_device")
        self.btn_terminal: QPSLPushButton = self.findChild(QPSLPushButton,
                                                           "btn_terminal")
        self.cbox_terminal: QPSLComboBox = self.findChild(QPSLComboBox,
                                                          "cbox_terminal")
        self.sbox_sample_rate: QPSLSpinBox = self.findChild(QPSLSpinBox,
                                                            "sbox_sample_rate")
        self.sbox_sample_number: QPSLSpinBox = self.findChild(QPSLSpinBox,
                                                            "sbox_sample_number")
        self.btn_add_line: QPSLPushButton = self.findChild(QPSLPushButton,
                                                           "btn_add_line")
        self.btn_remove_line: QPSLPushButton = self.findChild(QPSLPushButton,
                                                              "btn_remove_line")
        self.plot_line: QPSLPlotWidget = self.findChild(QPSLPlotWidget,
                                                        "plot_line")
        self.tab_lines: QPSLTabWidget = self.findChild(QPSLTabWidget,
                                                         "tab_lines")
        self.btn_init_task: QPSLToggleButton = self.findChild(QPSLToggleButton,
                                                              "btn_init_task")
        self.btn_start_task: QPSLToggleButton = self.findChild(QPSLToggleButton,
                                                               "btn_start_task")
        self.btn_reset:QPSLPushButton = self.findChild(QPSLPushButton,
                                                       "btn_reset")
    
    @QPSLObjectBase.log_decorator()
    def setupStyle(self):
        pass

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()

        connect_direct(self.btn_device.sig_clicked,
                       self.m_worker.sig_to_query_device_list)
        connect_queued(self.m_worker.sig_answer_device_list,
                       self.on_get_device_list)
        connect_direct(self.btn_terminal.sig_clicked,
                       self.on_click_query_terminal)
        connect_queued(self.m_worker.sig_answer_terminal_list,
                       self.on_get_terminal_list)
        connect_direct(self.btn_add_line.sig_clicked,
                       self.on_click_add_line)
        connect_direct(self.btn_remove_line.sig_clicked,
                       self.on_click_remove_line)
        for i,box in enumerate(self.tab_lines.get_widgets()):
            self.setup_logic_line_box(index=i)
        connect_queued(self.m_worker.sig_answer_line_list,
                       self.on_get_line_list)
        
        # connect_queued(self.m_worker.sig_data_written, self.on_get_data)

        connect_direct(self.btn_init_task.sig_open,
                       self.on_click_init_task)
        connect_queued(self.m_worker.sig_task_inited,
                       self.btn_init_task.set_opened)
        connect_direct(self.btn_init_task.sig_close,
                       self.m_worker.sig_to_clear_task)
        connect_queued(self.m_worker.sig_task_clear,
                       self.btn_init_task.set_closed)
        # connect_direct(self.btn_init_task.sig_state_changed,
        #                self.on_task_state_changed)

        connect_direct(self.btn_start_task.sig_open,
                       self.m_worker.sig_to_start_task)
        connect_queued(self.m_worker.sig_task_started,
                       self.btn_start_task.set_opened)
        connect_direct(self.btn_start_task.sig_close,
                       self.m_worker.sig_to_stop_task)
        connect_queued(self.m_worker.sig_task_stopped,
                       self.btn_start_task.set_closed)
        connect_direct(self.btn_reset.sig_clicked,
                       self.m_worker.reset)

        self.sbox_sample_number.setSpecialValueText(" Continuous Sample")
        # self.on_nidaq_task_state_changed(state=False)
        self.m_worker.start_thread()
    
    @QPSLObjectBase.log_decorator()
    def on_get_device_list(self, device_name_list: List[str]):
        current = None
        if self.cbox_device.count():
            current = self.cbox_device.currentText()
        self.cbox_device.clear()
        self.cbox_device.addItems(device_name_list)
        if current is not None:
            index = device_name_list.index(current)
            self.cbox_device.setCurrentIndex(index)
        else:
            self.cbox_device.setCurrentIndex(0)

    @QPSLObjectBase.log_decorator()
    def on_click_query_terminal(self):
        device_name = self.cbox_device.currentText()
        self.m_worker.sig_to_query_terminal_list.emit(device_name)

    @QPSLObjectBase.log_decorator()
    def on_get_terminal_list(self, terminal_name_list: List[str]):
        current = None
        if self.cbox_terminal.count():
            current = self.cbox_terminal.currentText()
        self.cbox_terminal.clear()
        self.cbox_terminal.addItems(terminal_name_list)
        index = 0
        if current is not None and current in terminal_name_list:
            index = terminal_name_list.index(current)
        self.cbox_terminal.setCurrentIndex(index)
    
    @QPSLObjectBase.log_decorator()
    def on_click_query_line(self, line:str):
        device_name = self.cbox_device.currentText()
        line_id = int(line.split()[1])
        self.m_worker.sig_to_query_line_list.emit(device_name, line_id)
        # self.cbox_device.currentIndexChanged

    @QPSLObjectBase.log_decorator()
    def on_get_line_list(self, line_name_list: List[str], 
                         line_id: int):
        tab_line: QPSLVFrameList = self.tab_lines.get_widget(index=line_id).remove_type()
        frame_line: QPSLFrameList = tab_line.get_widget(0).remove_type()  
        cbox_line: QPSLComboBox = frame_line.get_widget(1).remove_type()    
        current = None
        if cbox_line.count():
            current = cbox_line.currentText()
        cbox_line.clear()
        cbox_line.addItems(line_name_list)
        index = 0
        if current is not None and current in line_name_list:
            index = line_name_list.index(current)
        cbox_line.setCurrentIndex(index)

    @QPSLObjectBase.log_decorator()
    def on_click_add_line(self):
        index = self.tab_lines.count()
        line_box: QPSLHFrameList = QPSLObjectBase.from_json(
            self.tab_lines.get_widget(index - 1).to_json())
        self.tab_lines.add_tab(tab=line_box, title="line_{0}".format(index))
        self.setup_logic_line_box(index=index)

    @QPSLObjectBase.log_decorator()
    def on_click_remove_line(self):
        if self.tab_lines.count() == 1:
            raise BaseException("can't remove last line")
        tab = self.tab_lines.get_tab(self.tab_lines.count() - 1)
        self.tab_lines.remove_tab(tab=tab)
        tab.deleteLater()

    @QPSLObjectBase.log_decorator()
    def on_click_init_task(self):
        channels = []
        for tab_line in self.tab_lines.get_widgets():
            frame_line: QPSLFrameList = tab_line.get_widget(0).remove_type()  
            cbox_line: QPSLComboBox = frame_line.get_widget(1).remove_type()
            channels.append(cbox_line.currentText()) 
        if self.cbox_terminal.currentText() != "None":
            trigger_source = self.cbox_terminal.currentText()
        else:
            trigger_source =""
        sample_rate =self.sbox_sample_rate.value()
        sample_number =self.sbox_sample_number.value()
        everyn = 50
        arr2d = []
        lcm = 1
        for tab_line in self.tab_lines.get_widgets():
            sbox_cycle: QPSLSpinBox = tab_line.get_widget(1).remove_type()
            sbox_ratio: QPSLDoubleSpinBox = tab_line.get_widget(2).remove_type()
            sbox_delay: QPSLSpinBox = tab_line.get_widget(3).remove_type()
            cycle,ratio,delay = sbox_cycle.value(),sbox_ratio.value(),sbox_delay.value()
            if ratio > 1:
                return None
            arr = numpy_array_shift(array=np.array([0] * int(ratio*cycle) + 
                                                [1] *(cycle - int(ratio*cycle))),
                                 right_shift=delay + cycle - int(ratio * cycle))
            if arr is None:
                raise BaseException("wave{0} is None",format())
            # print(arr)
            arr2d.append(arr)
            if self.sbox_sample_number.value() == 0:
                lcm = lcm * len(arr)// math.gcd(lcm, len(arr))
        if lcm > 10000000:
            raise BaseException(
                "lcm of all array_lenths is too big! lcm ={0}".format(lcm)
            )
        arr2d = [
            numpy_array_adapt_length(
                array=arr,
                length=self.sbox_sample_number.value()
                if self.sbox_sample_number.value() else lcm)
            for arr in arr2d
        ]
        arr2d = np.vstack(arr2d)
        self.m_worker.sig_to_init_task.emit(channels, trigger_source, sample_rate,
                                   sample_number, everyn, arr2d)

    # @QPSLObjectBase.log_decorator()
    # def on_btn_clear_task_clicked(self):
    #     self.sig_to_clear_task.emit()

    # @QPSLObjectBase.log_decorator()
    # def on_btn_start_task_clicked(self):
    #     self.sig_to_start_task.emit()

    # @QPSLObjectBase.log_decorator()
    # def on_btn_stop_task_clicked(self):
    #     self.sig_to_stop_task.emit()

    @QPSLObjectBase.log_decorator()
    def on_nidaq_task_state_changed(self, state: bool):
        for cbox in self.cboxes:
            cbox.setEnabled(not state)
        for btn in self.push_buttons:
            btn.setEnabled(not state)
        for spin in self.spins:
            spin.setEnabled(not state)
        self.btn_start.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_nidaq_switch_state_changed(self, state: bool):
        self.btn_init.setEnabled(not state)

    @QPSLObjectBase.log_decorator()
    def on_data_written(self, start_index: int, arr2d: np.ndarray):
        pass

    @QPSLObjectBase.log_decorator()
    def setup_logic_line_box(self, index: int):
        tab: QPSLVFrameList = self.tab_lines.get_widget(index)
        frame: QPSLFrameList = tab.get_widget(0).remove_type()  
        btn_line: QPSLPushButton = frame.get_widget(0).remove_type()
        btn_line.set_text("Line {0}".format(index))
        connect_direct(btn_line.sig_clicked_str,
                       self.on_click_query_line) 
        self.on_click_query_line(btn_line.text())


MainWidget = NIDAQmxDOPluginUI

