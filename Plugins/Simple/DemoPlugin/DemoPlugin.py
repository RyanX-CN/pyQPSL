from Tool import *


class DemoPluginWorker(QPSLWorker):
    sig_open_device, sig_to_open_device, sig_device_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_close_device, sig_to_close_device, sig_device_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_to_start_query, sig_query_started = pyqtSignal(), pyqtSignal()
    sig_to_stop_query, sig_query_stopped = pyqtSignal(), pyqtSignal()
    sig_to_query_position = pyqtSignal()
    sig_move, sig_to_move = pyqtSignal(float), pyqtSignal(float)
    sig_answer_position = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.m_keep_query_controller = SharedStateController(
            value=SharedStateController.State.Stop)
        self.m_stage: QPSLVirtualStage

    def load_attr(self, virtual_minimum: float, virtual_maximum: float,
                  virtual_position: float):
        super().load_attr()
        self.m_stage = QPSLVirtualStage(minimum=virtual_minimum,
                                        maximum=virtual_maximum,
                                        position=virtual_position,
                                        interval=20)
        self.setup_logic()
        return self

    def to_delete(self):
        self.close()
        return super().to_delete()

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_open_device, self.sig_open_device,
                                 self.open)
        connect_asynch_and_synch(self.sig_to_close_device,
                                 self.sig_close_device, self.close)
        connect_asynch_and_synch(self.sig_to_move, self.sig_move,
                                 self.move_distance_until_stop)
        connect_queued(self.sig_to_start_query, self.on_start_query)
        connect_queued(self.sig_to_stop_query, self.on_stop_query)
        connect_queued(self.sig_to_query_position, self.on_query_position)

    @QPSLObjectBase.log_decorator()
    def open(self):
        if self.is_opened():
            return
        self.m_stage.open()
        self.sig_device_opened.emit()
        self.add_warning(msg="Device Opened")

    @QPSLObjectBase.log_decorator()
    def close(self):
        if not self.is_opened():
            return
        self.on_stop_query()
        self.m_stage.close()
        self.sig_device_closed.emit()
        self.add_warning(msg="Device Closed")

    @QPSLObjectBase.log_decorator()
    def is_opened(self):
        return self.m_stage.is_opened()

    @QPSLObjectBase.log_decorator()
    def get_min(self):
        return self.m_stage.get_minimum()

    @QPSLObjectBase.log_decorator()
    def get_max(self):
        return self.m_stage.get_maximum()

    @QPSLObjectBase.log_decorator()
    def get_position(self):
        return self.m_stage.get_position()

    @pyqtSlot()
    @QPSLObjectBase.log_decorator()
    def on_query_position(self):
        self.sig_answer_position.emit(self.get_position())

    @QPSLObjectBase.log_decorator()
    def on_start_query(self):
        if not self.m_stage.get_state():
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
    def move_distance_until_stop(self, move_dis: float):
        self.m_stage.move_to(target=move_dis)
        while self.m_stage.is_moving():
            sleep_for(30)


class DemoPluginUI(QPSLVFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()
        self.m_worker = DemoPluginWorker()

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
        self.button_query: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_query")
        self.spin_move_distance: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_move_distance")
        self.button_move: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_move")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr(*self.slider.get_range(),
                                self.slider.get_value())

        # switch open and close
        connect_direct(self.toggle_button_open.sig_open,
                       self.m_worker.sig_to_open_device)
        connect_direct(self.toggle_button_open.sig_close,
                       self.m_worker.sig_to_close_device)
        connect_queued(self.m_worker.sig_device_opened,
                       self.toggle_button_open.set_opened)
        connect_queued(self.m_worker.sig_device_closed,
                       self.toggle_button_open.set_closed)
        connect_direct(self.toggle_button_open.sig_state_changed,
                       self.on_stage_state_changed)

        # switch keep query or not
        connect_queued(self.toggle_button_query.sig_open,
                       self.m_worker.sig_to_start_query)
        connect_queued(self.toggle_button_query.sig_close,
                       self.m_worker.sig_to_stop_query)
        connect_queued(self.m_worker.sig_query_started,
                       self.toggle_button_query.set_opened)
        connect_queued(self.m_worker.sig_query_stopped,
                       self.toggle_button_query.set_closed)

        # position
        connect_queued(self.button_query.clicked,
                       self.m_worker.sig_to_query_position)
        connect_queued(self.m_worker.sig_answer_position,
                       self.slider.set_value)

        # move
        connect_direct(self.slider.sig_value_clicked_at,
                       self.m_worker.sig_to_move)
        connect_direct(self.button_move.sig_clicked,
                       self.on_move_by_spinbox_value)
        connect_direct(self.spin_move_distance.sig_value_changed,
                       self.on_move_by_spinbox_value)

        self.on_stage_state_changed(state=False)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_stage_state_changed(self, state: bool):
        self.slider.setEnabled(state)
        self.spin_move_distance.setEnabled(state)
        self.toggle_button_query.setEnabled(state)
        self.button_query.setEnabled(state)
        self.button_move.setEnabled(state)

    @QPSLObjectBase.log_decorator()
    def on_move_by_spinbox_value(self):
        self.m_worker.sig_to_move.emit(self.spin_move_distance.value())


MainWidget = DemoPluginUI