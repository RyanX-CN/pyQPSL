from Tool import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .DMAPI import DMController


class DMPluginWorker(QPSLWorker):
    sig_open_device, sig_to_open_device, sig_device_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_close_device, sig_to_close_device, sig_device_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_load_map, sig_to_load_map, sig_map_loaded, sig_map_unloaded = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(), pyqtSignal()
    sig_set_single_value, sig_to_set_single_value = pyqtSignal(
        float), pyqtSignal(float)
    sig_set_file_path, sig_to_set_file_path = pyqtSignal(str), pyqtSignal(str)
    sig_get_float_array = pyqtSignal(list)
    sig_send_float_array, sig_to_send_float_array = pyqtSignal(
        list), pyqtSignal(list)

    def load_attr(self, serial_number: str):
        super().load_attr()
        self.m_serial_number = serial_number  # "17BW025#021"
        if self.is_virtual:
            self.m_dm = QPSLVirtualDM()
        else:
            self.m_dm = DMController()
        self.setup_logic()
        return self

    def to_delete(self):
        self.on_close_device()
        return super().to_delete()

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_open_device, self.sig_open_device,
                                 self.on_open_device)
        connect_asynch_and_synch(self.sig_to_close_device,
                                 self.sig_close_device, self.on_close_device)
        connect_asynch_and_synch(self.sig_to_load_map, self.sig_load_map,
                                 self.on_load_map)
        connect_asynch_and_synch(self.sig_to_set_single_value,
                                 self.sig_set_single_value,
                                 self.on_set_single_value)
        connect_asynch_and_synch(self.sig_to_set_file_path,
                                 self.sig_set_file_path, self.on_set_file_path)
        connect_asynch_and_synch(self.sig_to_send_float_array,
                                 self.sig_send_float_array,
                                 self.on_send_float_array)

    @QPSLObjectBase.log_decorator()
    def on_open_device(self):
        if self.is_opened():
            return
        self.m_dm.BMCOpen(serial_number=self.m_serial_number)
        self.sig_device_opened.emit()
        self.add_warning(msg="Device Opened")

    @QPSLObjectBase.log_decorator()
    def on_close_device(self):
        if not self.is_opened():
            return
        if self.is_map_loaded():
            self.sig_map_unloaded.emit()
        self.m_dm.BMCClose()
        self.sig_device_closed.emit()
        self.add_warning(msg="Device Closed")

    @QPSLObjectBase.log_decorator()
    def on_load_map(self):
        if self.is_map_loaded():
            return
        self.m_dm.BMCLoadMap()
        self.sig_map_loaded.emit()
        self.add_warning(msg="Map Loaded")

    @QPSLObjectBase.log_decorator()
    def on_set_single_value(self, val: float):
        self.sig_get_float_array.emit([val] * 140)

    @QPSLObjectBase.log_decorator()
    def on_set_file_path(self, file_path: str):
        with open(file_path, "rt") as f:
            arr = list(map(lambda line: float(line.strip()), f.readlines()))
        self.sig_get_float_array.emit(arr)

    @QPSLObjectBase.log_decorator()
    def on_send_float_array(self, arr: List[float]):
        self.m_dm.BMCSetArray(arr)

    def is_map_loaded(self):
        return self.m_dm.is_map_loaded()

    def is_opened(self):
        return self.m_dm.is_opened()


class DMPluginUI(QPSLHFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.m_serial_number = json.get("serial_number")
        if self.m_serial_number is None:
            self.m_serial_number = "17BW025#021"
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        res.update({"serial_number": self.m_serial_number})
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = DMPluginWorker()

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
        self.table_grid: QPSLTableWidget = self.findChild(
            QPSLTableWidget, "table_grid")
        self.toggle_button_open: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_open")
        self.toggle_button_load_map: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_load_map")
        self.spin_single_value: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_single_value")
        self.box_get_file_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_file_path")
        self.edit_array: QPSLTextEdit = self.findChild(QPSLTextEdit,
                                                       "edit_array")
        self.button_send: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_send")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr(serial_number=self.m_serial_number)
        self.table_grid.horizontalHeader().hide()
        self.table_grid.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_grid.verticalHeader().hide()
        self.table_grid.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_grid.verticalHeader().setMinimumSectionSize(20)
        self.table_grid.horizontalHeader().setMinimumSectionSize(30)
        self.table_grid.setMinimumWidth(362)

        for i in range(12):
            for j in range(12):
                self.table_grid.setItem(i, j, QTableWidgetItem())

        connect_direct(self.toggle_button_open.sig_open,
                       self.m_worker.sig_to_open_device)
        connect_queued(self.m_worker.sig_device_opened,
                       self.toggle_button_open.set_opened)
        connect_direct(self.toggle_button_open.sig_close,
                       self.m_worker.sig_to_close_device)
        connect_queued(self.m_worker.sig_device_closed,
                       self.toggle_button_open.set_closed)
        connect_direct(self.toggle_button_open.sig_state_changed,
                       self.on_stage_state_changed)

        connect_direct(self.toggle_button_load_map.sig_open,
                       self.m_worker.sig_to_load_map)
        connect_queued(self.m_worker.sig_map_loaded, self.on_map_loaded)
        connect_queued(self.m_worker.sig_map_unloaded,
                       self.toggle_button_load_map.set_closed)

        connect_direct(self.spin_single_value.sig_editing_finished_at,
                       self.m_worker.sig_to_set_single_value)
        connect_direct(self.box_get_file_path.sig_path_changed,
                       self.box_get_file_path.set_icon_checked)
        connect_direct(self.box_get_file_path.sig_path_changed,
                       self.m_worker.sig_to_set_file_path)
        connect_queued(self.m_worker.sig_get_float_array,
                       self.on_get_float_array)
        connect_direct(self.button_send.sig_clicked, self.on_click_send)

        self.on_get_float_array(arr=[0] * 140)
        self.on_stage_state_changed(state=False)
        self.spin_single_value.setSingleStep(0.05)
        self.edit_array.installEventFilter(self)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_map_loaded(self):
        self.toggle_button_load_map.set_opened()
        self.toggle_button_load_map.setEnabled(False)

    @QPSLObjectBase.log_decorator()
    def on_get_float_array(self, arr: List[float]):
        self.edit_array.setText('; '.join(
            map(lambda v: "{0:6f}".format(v), arr)))

    @QPSLObjectBase.log_decorator()
    def on_edit_array_text_changed(self):
        text = self.edit_array.document().toRawText()
        arr = list(map(float, text.split('; ')))
        self.m_arr = arr
        self.edit_array.setText('; '.join(
            map(lambda v: "{0:6f}".format(v), arr)))

    @QPSLObjectBase.log_decorator()
    def on_click_send(self):
        text = self.edit_array.document().toRawText()
        arr = list(map(float, text.split('; ')))
        self.m_worker.sig_to_send_float_array.emit(arr)
        self.on_show_array(arr)

    @QPSLObjectBase.log_decorator()
    def on_stage_state_changed(self, state: bool):
        self.toggle_button_load_map.setEnabled(state)
        self.spin_single_value.setEnabled(state)
        self.box_get_file_path.setEnabled(state)
        self.edit_array.setEnabled(state)
        self.button_send.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_show_array(self, value: List[float]):
        if isinstance(value, list):
            value = iter(value)
        for i in range(12):
            for j in range(12):
                item = self.table_grid.item(i, j)
                if (0 < i < 11) or (0 < j < 11):
                    val = value if isinstance(value, float) else next(value)
                    item.setToolTip("{0}".format(val))
                else:
                    val = 0
                item.setBackground(
                    QColor("#{0:x}{0:x}{0:x}".format(int(
                        (256 - 1e-10) * val))))

    def eventFilter(self, obj: QPSLTextEdit, ev: QEvent) -> bool:
        if obj == self.edit_array and ev.type(
        ) == QEvent.Type.FocusAboutToChange:
            self.on_edit_array_text_changed()
        return super().eventFilter(obj, ev)


MainWidget = DMPluginUI