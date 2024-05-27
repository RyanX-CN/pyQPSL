from Tool import *
import pipython

loading_warning("pipython version = {0}".format(pipython.__version__))
from pipython import GCSDevice


class PIPluginWorker(QPSLWorker):
    sig_open_device, sig_to_open_device, sig_device_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_close_device, sig_to_close_device, sig_device_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_set_serve_on, sig_to_set_serve_on, sig_serve_set_on = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_set_serve_off, sig_to_set_serve_off, sig_serve_set_off = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_to_start_query, sig_query_started = pyqtSignal(), pyqtSignal()
    sig_to_stop_query, sig_query_stopped = pyqtSignal(), pyqtSignal()
    sig_to_query_position = pyqtSignal()
    sig_answer_position = pyqtSignal(float)
    sig_reference, sig_to_reference = pyqtSignal(), pyqtSignal()
    sig_move_home, sig_to_move_home = pyqtSignal(), pyqtSignal()
    sig_move_absolute, sig_to_move_absolute = pyqtSignal(float), pyqtSignal(
        float)
    sig_move_relative, sig_to_move_relative = pyqtSignal(float), pyqtSignal(
        float)

    def __init__(self):
        super(PIPluginWorker, self).__init__()
        self.m_serial_number: str = None
        self.m_dllpath: str = None
        self.m_keep_query = SharedStateController(
            value=SharedStateController.State.Stop)

    def load_attr(self, virtual_minimum: float, virtual_maximum: float,
                  virtual_position: float, serial_number: str):
        super().load_attr()
        self.m_serial_number = serial_number  #"0121004023"
        self.m_dllpath = "./{0}/bin/PI_GCS2_DLL_x64.dll".format(
            __package__.replace('.', '/'))
        if self.is_virtual:
            self.m_stage = QPSLVirtualStage(
                minimum=virtual_minimum,
                maximum=virtual_maximum,
                position=virtual_position,
            )
        else:
            self.m_device = None
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
        connect_asynch_and_synch(self.sig_to_set_serve_on,
                                 self.sig_set_serve_on, self.on_set_serve_on)
        connect_asynch_and_synch(self.sig_to_set_serve_off,
                                 self.sig_set_serve_off, self.on_set_serve_off)

        connect_queued(self.sig_to_start_query, self.on_start_query)
        connect_queued(self.sig_to_stop_query, self.on_stop_query)
        connect_queued(self.sig_to_query_position, self.on_query_position)

        connect_asynch_and_synch(self.sig_to_reference, self.sig_reference,
                                 self.on_reference)
        connect_asynch_and_synch(self.sig_to_move_home, self.sig_move_home,
                                 self.on_move_home)
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
            self.m_device = GCSDevice(gcsdll=self.m_dllpath)
            self.m_device.ConnectUSB(serialnum=self.m_serial_number)
            IDN = str.strip(self.m_device.qIDN())
            self.add_warning(msg="Found device IDN: %s" % IDN)
            if self.m_device.HasqVER():
                VER = str.strip(GCSDevice.qVER(self.m_device))
                self.add_warning(msg="VER: %s" % VER)
        self.add_warning(msg="Device Opened")
        self.sig_device_opened.emit()

    @QPSLObjectBase.log_decorator()
    def on_close_device(self):
        if not self.is_opened():
            return
        self.on_set_serve_off()
        self.on_stop_query()
        if self.is_virtual:
            self.m_stage.close()
        else:
            self.m_device.close()
            self.m_device = None
        self.add_warning(msg="Device Closed")
        self.sig_device_closed.emit()

    @QPSLObjectBase.log_decorator()
    def on_set_serve_on(self):
        if self.is_virtual:
            pass
        else:
            GCSDevice.SVO(self.m_device, axes=['1'], values=True)
        self.sig_serve_set_on.emit()

    @QPSLObjectBase.log_decorator()
    def on_set_serve_off(self):
        if self.is_virtual:
            pass
        else:
            GCSDevice.SVO(self.m_device, axes=['1'], values=False)
        self.sig_serve_set_off.emit()

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
            while not self.m_keep_query.reply_if_stop():
                QMetaObject.invokeMethod(self, func_name)
                sleep_for(20)

        self.m_keep_query.set_continue()
        QThreadPool.globalInstance().start(func)
        self.sig_query_started.emit()

    @QPSLObjectBase.log_decorator()
    def on_stop_query(self):
        if self.m_keep_query.is_continue():
            self.m_keep_query.set_stop_until_reply()
            self.sig_query_stopped.emit()

    @QPSLObjectBase.log_decorator()
    def on_reference(self):
        if self.is_virtual:
            pass
        else:
            GCSDevice.FRF(self.m_device, axes=['1'])

    @QPSLObjectBase.log_decorator()
    def on_move_home(self):
        if self.is_virtual:
            self.m_stage.home()
        else:
            GCSDevice.GOH(self.m_device, axes=['1'])

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_distance(self, position: float):
        if self.is_virtual:
            self.m_stage.move_to(target=position)
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            GCSDevice.MOV(self.m_device, axes=['1'], values=position)
            self.wait_on_ready(polldelay=0.02)

    @QPSLObjectBase.log_decorator()
    def on_move_relative_distance(self, position: float):
        if self.is_virtual:
            self.m_stage.move_to(target=self.m_stage.get_position() + position)
            while self.m_stage.is_moving():
                time.sleep(0.02)
        else:
            GCSDevice.MVR(self.m_device, axes=['1'], values=position)
            self.wait_on_ready(polldelay=0.02)

    def is_opened(self) -> bool:
        if self.is_virtual:
            return self.m_stage.is_opened()
        else:
            return self.m_device is not None

    def get_min(self):
        if self.is_virtual:
            return -1
        else:
            Min = GCSDevice.qTMN(self.m_device, axes='1')
            return Min['1']

    def get_max(self):
        if self.is_virtual:
            return 1
        else:
            Max = GCSDevice.qTMX(self.m_device, axes='1')
            return Max['1']

    def get_position(self):
        if self.is_virtual:
            return self.m_stage.get_position()
        else:
            return GCSDevice.qPOS(self.m_device, axes='1')['1']

    def wait_on_ready(self, polldelay=0.02):
        if not GCSDevice.HasIsControllerReady():
            return
        while not GCSDevice.IsControllerReady():
            time.sleep(polldelay)

    def wait_on_target(self, pidevice, axes=None, polldelay=0.02):
        self.wait_on_ready(polldelay=polldelay)
        while not all(list(GCSDevice.qONT(self.m_device, axes='1').values())):
            time.sleep(polldelay)


class PIPluginUI(QPSLVFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.m_serial_number = json.get("serial_number")
        if self.m_serial_number is None:
            self.m_serial_number = "0121004023"
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        res.update({"serial_number": self.m_serial_number})
        return res

    def __init__(self):
        super(PIPluginUI, self).__init__()
        self.m_worker = PIPluginWorker()

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
        self.toggle_button_serve: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_serve")
        self.toggle_button_query: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_query")
        self.button_reference: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reference")
        self.button_move_home: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_home")
        self.button_query_position: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_query_position")
        self.spin_move: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_move")
        self.button_move_absolute: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_absolute")
        self.button_move_relative: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move_relative")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr(virtual_minimum=self.slider.get_range()[0],
                                virtual_maximum=self.slider.get_range()[1],
                                virtual_position=self.slider.get_value(),
                                serial_number=self.m_serial_number)

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

        connect_direct(self.toggle_button_serve.sig_open,
                       self.m_worker.sig_to_set_serve_on)
        connect_queued(self.m_worker.sig_serve_set_on,
                       self.toggle_button_serve.set_opened)
        connect_direct(self.toggle_button_serve.sig_close,
                       self.m_worker.sig_to_set_serve_off)
        connect_queued(self.m_worker.sig_serve_set_off,
                       self.toggle_button_serve.set_closed)

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
                       self.slider.set_value)

        connect_direct(self.button_reference.sig_clicked,
                       self.m_worker.sig_to_reference)
        connect_direct(self.button_move_home.sig_clicked,
                       self.m_worker.sig_to_move_home)
        connect_direct(self.button_move_absolute.sig_clicked,
                       self.on_move_absolute)
        connect_direct(self.button_move_relative.sig_clicked,
                       self.on_move_relative)
        connect_direct(self.slider.sig_value_clicked_at,
                       self.m_worker.sig_to_move_absolute)

        self.on_stage_state_changed(state=False)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_stage_state_changed(self, state: bool):
        self.slider.setEnabled(state)
        self.spin_move.setEnabled(state)
        self.toggle_button_serve.setEnabled(state)
        self.toggle_button_query.setEnabled(state)
        for btn in [
                self.button_reference, self.button_move_home,
                self.button_query_position, self.button_move_absolute,
                self.button_move_relative
        ]:
            btn.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute(self):
        self.m_worker.sig_to_move_absolute.emit(self.spin_move.value())

    @QPSLObjectBase.log_decorator()
    def on_move_relative(self):
        self.m_worker.sig_to_move_relative.emit(self.spin_move.value())


MainWidget = PIPluginUI
