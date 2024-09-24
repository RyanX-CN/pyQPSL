from Tool import *
import zaber_motion

loading_warning("zaber motion version = {0}".format(zaber_motion.__version__))
from zaber_motion.ascii import Connection
from zaber_motion.ascii.device import Device
from zaber_motion.ascii.axis import Axis


class ZaberPluginWorker(QPSLWorker):
    sig_open_device, sig_to_open_device, sig_device_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_close_device, sig_to_close_device, sig_device_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_to_start_query, sig_query_started = pyqtSignal(), pyqtSignal()
    sig_to_stop_query, sig_query_stopped = pyqtSignal(), pyqtSignal()
    sig_to_query_position = pyqtSignal()
    sig_answer_position = pyqtSignal(float)
    sig_move_min, sig_to_move_min = pyqtSignal(), pyqtSignal()
    sig_move_max, sig_to_move_max = pyqtSignal(), pyqtSignal()
    sig_move_home, sig_to_move_home = pyqtSignal(), pyqtSignal()
    sig_move_absolute, sig_to_move_absolute = pyqtSignal(float), pyqtSignal(
        float)
    sig_move_relative, sig_to_move_relative = pyqtSignal(float), pyqtSignal(
        float)

    def __init__(self):
        super(ZaberPluginWorker, self).__init__()
        self.m_port_name: str = None
        self.m_keep_query_controller = SharedStateController(
            value=SharedStateController.State.Stop)

    def load_attr(self, virtual_minimum: float, virtual_maximum: float,
                  virtual_position: float, port_number: str):
        super().load_attr()
        self.m_port_name = port_number  # "COM5"
        if self.is_virtual:
            self.m_stage = QPSLVirtualStage(
                minimum=virtual_minimum,
                maximum=virtual_maximum,
                position=virtual_position,
            )
        else:
            self.m_connection: Connection = None
            self.m_device_list: List[Device] = []
            self.m_axis: Axis = None
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
        connect_queued(self.sig_to_start_query, self.on_start_query)
        connect_queued(self.sig_to_stop_query, self.on_stop_query)
        connect_queued(self.sig_to_query_position, self.on_query_position)

        connect_asynch_and_synch(self.sig_to_move_home, self.sig_move_home,
                                 self.on_move_home)
        connect_asynch_and_synch(self.sig_to_move_min, self.sig_move_min,
                                 self.on_move_min)
        connect_asynch_and_synch(self.sig_to_move_max, self.sig_move_max,
                                 self.on_move_max)
        connect_asynch_and_synch(self.sig_to_move_absolute,
                                 self.sig_move_absolute,
                                 self.on_move_absolute_distance)
        connect_asynch_and_synch(self.sig_to_move_relative,
                                 self.sig_move_relative,
                                 self.on_move_relative_distance)

    @QPSLObjectBase.log_decorator()
    def on_open_device(self):
        if self.is_opened():
            return
        if self.is_virtual:
            self.m_stage.open()
        else:
            self.m_connection = Connection.open_serial_port(
                port_name=self.m_port_name)
            self.m_device_list = self.m_connection.detect_devices(
                identify_devices=False)
            self.add_warning(msg="Found %d devices" % len(self.m_device_list))
            self.choose_axis(device_id=0, axis_id=1)
        self.add_warning(msg="Device Opened")
        self.sig_device_opened.emit()

    @QPSLObjectBase.log_decorator()
    def on_close_device(self):
        if not self.is_opened():
            return
        self.on_stop_query()
        if self.is_virtual:
            self.m_stage.close()
        else:
            self.m_connection.close()
            self.m_connection = None
        self.add_warning(msg="Device Closed")
        self.sig_device_closed.emit()

    @pyqtSlot()
    @QPSLObjectBase.log_decorator()
    def on_query_position(self):
        self.sig_answer_position.emit(self.get_position())

    @QPSLObjectBase.log_decorator()
    def on_start_query(self):
        if not self.is_opened():
            return

        def func():
            func_name = self.on_query_position.__name__
            while not self.m_keep_query_controller.reply_if_stop():
                QMetaObject.invokeMethod(self, func_name)
                sleep_for(20)

        self.m_keep_query_controller.set_continue()
        QThreadPool.globalInstance().start(func)
        self.sig_query_started.emit()

    @QPSLObjectBase.log_decorator()
    def on_stop_query(self):
        if self.m_keep_query_controller.is_continue():
            self.m_keep_query_controller.set_stop_until_reply()
            self.sig_query_stopped.emit()

    @QPSLObjectBase.log_decorator()
    def on_move_home(self):
        if self.is_virtual:
            self.m_stage.home()
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            self.m_axis.home(wait_until_idle=True)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_distance(self, position: float):
        if self.is_virtual:
            self.m_stage.move_to(target=position)
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            self.m_axis.move_absolute(position=position, wait_until_idle=True)

    @QPSLObjectBase.log_decorator()
    def on_move_relative_distance(self, position: float):
        if self.is_virtual:
            self.m_stage.move_to(target=self.m_stage.get_position() + position)
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            self.m_axis.move_relative(position=position, wait_until_idle=True)

    @QPSLObjectBase.log_decorator()
    def on_move_min(self):
        if self.is_virtual:
            self.m_stage.move_to(self.m_stage.get_minimum())
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            self.m_axis.move_min(wait_until_idle=True)

    @QPSLObjectBase.log_decorator()
    def on_move_max(self):
        if self.is_virtual:
            self.m_stage.move_to(self.m_stage.get_maximum())
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            self.m_axis.move_max(wait_until_idle=True)

    def is_opened(self) -> bool:
        if self.is_virtual:
            return self.m_stage.is_opened()
        else:
            return self.m_connection is not None

    def choose_axis(self, device_id: int, axis_id: int):
        self.m_axis = self.m_device_list[device_id].get_axis(
            axis_number=axis_id)

    def get_position(self):
        if self.is_virtual:
            return self.m_stage.get_position()
        else:
            return self.m_axis.get_position()


class ZaberPluginUI(QPSLVFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.m_port_number = json.get("port_number")
        if self.m_port_number is None:
            self.m_port_number = "COM5"
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        res.update({"port_number": self.m_port_number})
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = ZaberPluginWorker()

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
        self.slider: QPSLComboSlider = self.findChild(QPSLComboSlider,
                                                      "slider")
        self.toggle_button_open: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_open")
        self.toggle_button_query: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_query")
        self.button_home: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_home")
        self.button_move_min: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_min")
        self.button_move_max: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_max")
        self.button_query_position: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_query_position")
        self.spin_ratio: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_ratio")
        self.spin_native_unit: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_native_unit")
        self.spin_micrometer: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_micrometer")
        self.button_move_absolute: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_absolute")
        self.button_move_relative: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_relative")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr(virtual_minimum=self.slider.get_range()[0],
                                virtual_maximum=self.micrometer_to_native(
                                    micrometer=self.slider.get_range()[1]),
                                virtual_position=self.micrometer_to_native(
                                    micrometer=self.slider.get_value()),
                                port_number=self.m_port_number)
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

        connect_direct(self.toggle_button_query.sig_open,
                       self.m_worker.sig_to_start_query)
        connect_queued(self.m_worker.sig_query_started,
                       self.toggle_button_query.set_opened)
        connect_direct(self.toggle_button_query.sig_close,
                       self.m_worker.sig_to_stop_query)
        connect_queued(self.m_worker.sig_query_stopped,
                       self.toggle_button_query.set_closed)

        # position
        connect_direct(self.button_query_position.sig_clicked,
                       self.m_worker.sig_to_query_position)
        connect_queued(self.m_worker.sig_answer_position,
                       self.on_answer_position)

        # move
        connect_direct(self.button_move_min.sig_clicked,
                       self.m_worker.sig_to_move_min)
        connect_direct(self.button_move_max.sig_clicked,
                       self.m_worker.sig_to_move_max)
        connect_direct(self.button_home.sig_clicked,
                       self.m_worker.sig_to_move_home)
        connect_direct(self.button_move_absolute.sig_clicked,
                       self.on_click_move_absolute)
        connect_direct(self.button_move_relative.sig_clicked,
                       self.on_click_move_relative)

        # native/micrometer
        connect_direct(self.spin_native_unit.sig_editing_finished_at,
                       self.update_micrometer)
        connect_direct(self.spin_micrometer.sig_editing_finished_at,
                       self.update_native)
        connect_direct(self.spin_ratio.sig_value_changed,
                       self.update_native_by_micrometer)
        connect_direct(self.slider.sig_value_clicked_at,
                       self.on_click_slider_move)

        self.on_stage_state_changed(state=False)
        self.spin_ratio.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def native_to_micrometer(self, native: float):
        return native / self.spin_ratio.value()

    @QPSLObjectBase.log_decorator()
    def micrometer_to_native(self, micrometer: float):
        return micrometer * self.spin_ratio.value()

    @QPSLObjectBase.log_decorator()
    def on_answer_position(self, native_position: float):
        self.slider.set_value(val=self.native_to_micrometer(
            native=native_position))

    @QPSLObjectBase.log_decorator()
    def on_stage_state_changed(self, state: bool):
        self.slider.setEnabled(state)
        self.toggle_button_query.setEnabled(state)
        for button in [
                self.button_home, self.button_move_min, self.button_move_max,
                self.button_query_position, self.button_move_absolute,
                self.button_move_relative
        ]:
            button.setEnabled(state)
        for spin in [
                self.spin_ratio, self.spin_native_unit, self.spin_micrometer
        ]:
            spin.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_click_move_absolute(self):
        self.m_worker.sig_to_move_absolute.emit(self.spin_native_unit.value())

    @QPSLObjectBase.log_decorator()
    def on_click_move_relative(self):
        self.m_worker.sig_to_move_relative.emit(self.spin_native_unit.value())

    @QPSLObjectBase.log_decorator()
    def on_click_slider_move(self, slider_position: float):
        self.m_worker.sig_to_move_absolute.emit(
            self.micrometer_to_native(micrometer=slider_position))

    @QPSLObjectBase.log_decorator()
    def update_micrometer(self, native: float):
        self.spin_micrometer.setValue(self.native_to_micrometer(native))

    @QPSLObjectBase.log_decorator()
    def update_native(self, micrometer: float):
        self.spin_native_unit.setValue(self.micrometer_to_native(micrometer))

    @QPSLObjectBase.log_decorator()
    def update_native_by_micrometer(self):
        self.update_native(micrometer=self.spin_micrometer.value())


MainWidget = ZaberPluginUI
