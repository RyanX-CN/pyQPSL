from Tool import *

os_path_append("./Plugins/DMPlugin/bin")
from Plugins.DMPlugin.DMAPI import DMController


class DMPluginWorker(QPSLWorker):
    sig_device_opened, sig_device_closed = pyqtSignal(), pyqtSignal()
    sig_query_started, sig_query_stopped = pyqtSignal(), pyqtSignal()
    sig_map_loaded = pyqtSignal()
    sig_single_value_sent = pyqtSignal(float)
    sig_array_value_sent = pyqtSignal(list)

    def __init__(self, parent: QWidget, object_name: str, virtual_mode: bool):
        super(DMPluginWorker, self).__init__(parent=parent,
                                             object_name=object_name)
        self.m_serial_number = "17BW025#021"
        self.m_virtual_mode = virtual_mode
        if self.m_virtual_mode:
            self.m_dm = QPSLVirtualDM()
        else:
            self.m_dm = DMController()

    def to_delete(self):
        self.close()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def open(self):
        if self.is_opened():
            return
        self.m_dm.BMCOpen(serial_number=self.m_serial_number)
        self.sig_device_opened.emit()
        self.add_warning(msg="Device Opened")

    @QPSLObjectBase.log_decorator()
    def close(self):
        if not self.is_opened():
            return
        self.m_dm.BMCClose()
        self.sig_device_closed.emit()
        self.add_warning(msg="Device Closed")

    @QPSLObjectBase.log_decorator()
    def is_opened(self):
        return self.m_dm.is_opened()

    @QPSLObjectBase.log_decorator()
    def load_map(self):
        if self.is_map_loaded():
            return
        self.m_dm.BMCLoadMap()
        self.sig_map_loaded.emit()
        self.add_warning(msg="Map Loaded")

    @QPSLObjectBase.log_decorator()
    def is_map_loaded(self):
        return self.m_dm.is_map_loaded()

    @QPSLObjectBase.log_decorator()
    def send_single_value(self, value: float):
        self.m_dm.BMCSetArray(double_arr=[value] * 140)
        self.sig_single_value_sent.emit(value)
        self.add_info(msg="Send single value over: {0}".format(value))

    @QPSLObjectBase.log_decorator()
    def send_array_value(self, value_arr: List[float]):
        self.m_dm.BMCSetArray(double_arr=value_arr)
        self.sig_array_value_sent.emit(value_arr)
        self.add_info(
            msg="Send array value over: {0}".format(simple_str(value_arr)))


class DMPluginUI(QPSLHorizontalGroupList):
    sig_worker_delete = pyqtSignal()
    sig_open, sig_to_open = pyqtSignal(), pyqtSignal()
    sig_close, sig_to_close = pyqtSignal(), pyqtSignal()
    sig_load_map, sig_to_load_map = pyqtSignal(), pyqtSignal()
    sig_send_single_value, sig_to_send_single_value = pyqtSignal(
        float), pyqtSignal(float)
    sig_send_array_value, sig_to_send_array_value = pyqtSignal(
        list), pyqtSignal(list)

    def __init__(self,
                 parent: QWidget,
                 object_name="DM",
                 virtual_mode=False,
                 font_family="Arial"):
        super(DMPluginUI, self).__init__(parent=parent,
                                         object_name=object_name)
        self.m_font_family = font_family
        self.m_worker = DMPluginWorker(self,
                                       object_name="worker",
                                       virtual_mode=virtual_mode)
        self.setupUi()
        self.setupStyle()
        self.setupLogic()
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def is_ready(self):
        return self.btn_switch.get_state() and self.btn_load_map.get_state()

    def to_delete(self):
        self.sig_worker_delete.emit()
        self.m_worker.stop_thread()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def setupUi(self):
        self.add_widget(QPSLGridGroupList(self, object_name="grid"))
        for i in range(12):
            for j in range(12):
                self.box_grid.add_widget_simple(QPSLLabel(
                    self.box_grid, object_name="label_{0}_{1}".format(i, j)),
                                                grid=(i, i, j, j))
        self.box_grid.layout.setSpacing(0)
        self.add_widget(QPSLVerticalGroupList(self, object_name="box_control"))
        self.box_control.add_widget(widget=QPSLToggleButton(
            self.box_control, object_name="btn_switch"))
        self.box_control.add_widget(
            widget=QPSLToggleButton(self.box_control,
                                    object_name="btn_load map",
                                    closed_text="load map",
                                    opened_text="map loaded"))
        self.box_control.add_widget(widget=QPSLHorizontalGroupList(
            self.box_control, object_name="box_single_value"))
        self.box_single_value.add_widget(
            widget=QPSLDoubleSpinBox(self.box_single_value,
                                     object_name="spin_single_value",
                                     min=0,
                                     max=1,
                                     value=0,
                                     prefix="val: ",
                                     decimals=6))
        self.spin_single_value.setSingleStep(0.1)
        self.box_single_value.add_widget(widget=QPSLPushButton(
            self.box_single_value, object_name="btn_send_array", text="send"))
        self.box_control.add_widget(widget=QPSLHorizontalGroupList(
            self.box_control, object_name="box_file_array"))
        self.box_file_array.add_widget(widget=QPSLChooseOpenFileButton(
            self.box_file_array,
            object_name="btn_choose_file",
            prefix="file: ",
            init_path=
            r".\Plugins\DMPlugin\resources\Shapes\Alignmentshape140.csv"))
        self.box_file_array.add_widget(widget=QPSLPushButton(
            self.box_file_array, object_name="btn_send_array", text="send"))
        self.set_stretch(sizes=(3, 2))

        self.btn_choose_file_array.set_tooltip_enable()

    @QPSLObjectBase.log_decorator()
    def setupStyle(self):
        self.on_dm_state_changed(state=False)
        label_color = "#ffffff"
        button_color = "#bbbbbb"
        self.box_grid.update_background_palette(color=label_color)
        for btn in self.toggle_buttons:
            btn.set_font(font=QFont(self.m_font_family, 10))
        for btn in self.push_buttons:
            btn.set_font(font=QFont(self.m_font_family, 10))
            btn.update_background_palette(color=button_color)
        for spin in self.double_spins:
            spin.setFont(QFont(self.m_font_family, 10))

    @QPSLObjectBase.log_decorator()
    def setupLogic(self):
        connect_blocked(self.sig_worker_delete, self.m_worker.to_delete)

        # synch/asynch
        connect_queued_and_blocked(self.sig_to_open, self.sig_open,
                                   self.m_worker.open)
        connect_queued_and_blocked(self.sig_to_close, self.sig_close,
                                   self.m_worker.close)
        connect_queued_and_blocked(self.sig_to_load_map, self.sig_load_map,
                                   self.m_worker.load_map)
        connect_queued_and_blocked(self.sig_to_send_single_value,
                                   self.sig_send_single_value,
                                   self.m_worker.send_single_value)
        connect_queued_and_blocked(self.sig_to_send_array_value,
                                   self.sig_send_array_value,
                                   self.m_worker.send_array_value)

        # switch open and close
        connect_direct(self.btn_switch.sig_open, self.sig_to_open)
        connect_direct(self.btn_switch.sig_close, self.sig_to_close)
        connect_queued(self.m_worker.sig_device_opened,
                       self.btn_switch.set_opened)
        connect_queued(self.m_worker.sig_device_closed,
                       self.btn_switch.set_closed)
        connect_direct(self.btn_switch.sig_state_changed,
                       self.on_dm_state_changed)

        # load map
        connect_direct(self.btn_load_map.sig_open, self.sig_to_load_map)
        connect_queued(self.m_worker.sig_map_loaded, self.on_map_loaded)

        # send single value
        connect_direct(self.btn_send_single_value.sig_clicked,
                       self.click_send_single_value)
        connect_queued(self.m_worker.sig_single_value_sent,
                       self.on_single_value_sent)

        # send file array
        connect_direct(self.btn_send_file_array.sig_clicked,
                       self.click_send_file_array)
        connect_queued(self.m_worker.sig_array_value_sent,
                       self.on_array_value_sent)

    @QPSLObjectBase.log_decorator()
    def on_dm_state_changed(self, state: bool):
        self.box_grid.setEnabled(state)
        self.btn_load_map.set_closed()
        self.update_grid_show(value=float(1))
        for btn in self.toggle_buttons:
            if btn != self.btn_switch:
                btn.setEnabled(state)
        for btn in self.push_buttons:
            btn.setEnabled(state)
        for spin in self.double_spins:
            spin.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_map_loaded(self):
        self.btn_load_map.set_opened()
        self.btn_load_map.setEnabled(False)

    @QPSLObjectBase.log_decorator()
    def click_send_single_value(self):
        value = self.spin_single_value.value()
        self.sig_to_send_single_value.emit(value)

    @QPSLObjectBase.log_decorator()
    def on_single_value_sent(self, value: float):
        self.update_grid_show(value=value)

    @QPSLObjectBase.log_decorator()
    def click_send_file_array(self):
        with open(self.btn_choose_file_array.get_path(), "rt") as f:
            arr = list(map(lambda line: float(line.strip()), f.readlines()))
        self.sig_to_send_array_value.emit(arr)

    @QPSLObjectBase.log_decorator()
    def on_array_value_sent(self, value_arr: List[float]):
        self.update_grid_show(value=value_arr)

    @QPSLObjectBase.log_decorator()
    def update_grid_show(self, value: Union[float, List[float]]):
        if isinstance(value, list):
            value = iter(value)
        img = QImage(12, 12, QImage.Format.Format_Grayscale8)
        for i in range(12):
            for j in range(12):
                label = self.box_grid.get_widget(i * 12 + j)
                if (0 < i < 11) or (0 < j < 11):
                    val = value if isinstance(value, float) else next(value)
                    label.setToolTip("{0}".format(val))
                else:
                    val = 0
                QPSLScalePixmapLabel.update_background_palette(
                    label, "#{0:x}{0:x}{0:x}".format(int(255 * val)))

    @property
    def box_grid(self) -> QPSLGridGroupList:
        return self.get_widget(0)

    @property
    def box_control(self) -> QPSLVerticalGroupList:
        return self.get_widget(1)

    @property
    def btn_switch(self) -> QPSLToggleButton:
        return self.box_control.get_widget(0)

    @property
    def btn_load_map(self) -> QPSLToggleButton:
        return self.box_control.get_widget(1)

    @property
    def box_single_value(self) -> QPSLHorizontalGroupList:
        return self.box_control.get_widget(2)

    @property
    def spin_single_value(self) -> QPSLDoubleSpinBox:
        return self.box_single_value.get_widget(0)

    @property
    def btn_send_single_value(self) -> QPSLPushButton:
        return self.box_single_value.get_widget(1)

    @property
    def box_file_array(self) -> QPSLHorizontalGroupList:
        return self.box_control.get_widget(3)

    @property
    def btn_choose_file_array(self) -> QPSLChooseOpenFileButton:
        return self.box_file_array.get_widget(0)

    @property
    def btn_send_file_array(self) -> QPSLPushButton:
        return self.box_file_array.get_widget(1)

    @property
    def toggle_buttons(self) -> List[QPSLToggleButton]:
        return [self.btn_switch, self.btn_load_map]

    @property
    def push_buttons(self) -> List[QPSLPushButton]:
        return [
            self.btn_send_single_value, self.btn_choose_file_array,
            self.btn_send_file_array
        ]

    @property
    def double_spins(self) -> List[QPSLDoubleSpinBox]:
        return [self.spin_single_value]


MainWidget = DMPluginUI