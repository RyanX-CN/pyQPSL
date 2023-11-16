from Tool import *


class ControllerPluginWorker(QPSLWorker):

    def __init__(self, parent: QWidget, object_name: str):
        super(ControllerPluginWorker, self).__init__(parent=parent,
                                                     object_name=object_name)

    @QPSLObjectBase.log_decorator()
    def on_command_test(self):
        self.add_error(100 / 0)

    @QPSLObjectBase.log_decorator()
    def on_command_exec(self, cmd: str):
        self.add_warning(msg="try exec command: %s..." % cmd)
        cmd = str.split(cmd)
        if len(cmd) == 3 and cmd[0] == "clock" and cmd[1].isdigit(
        ) and cmd[2].isdigit():
            t = time.time()
            for i in range(int(cmd[1])):
                sleep_for(1000)
                self.add_warning(
                    msg="{0} {1} seconds".format(cmd[2],
                                                 time.time() - t))
        elif len(cmd) == 3 and cmd[0] == "synchclock" and cmd[1].isdigit(
        ) and cmd[2].isdigit():
            counter = QPSLCountDown(self,
                                    object_name="counter",
                                    interval=1000,
                                    init_number=int(cmd[1]))
            event_loop = QPSLEventLoop(None, object_name="event_loop")
            start_time = time.time()

            def value_callback(value: int):
                self.add_warning(msg="synch id = %s, %f seconds" %
                                 (cmd[2], time.time() - start_time))

            connect_direct(counter.sig_to_value, value_callback)
            connect_direct(counter.sig_to_zero, event_loop.quit)

            counter.start_timer()
            event_loop.exec()
            counter.disconnect()
            counter.deleteLater()


class ControllerPluginUI(QPSLVerticalGroupList):
    sig_worker_delete = pyqtSignal()
    sig_to_exec_current_cmd = pyqtSignal()
    sig_exec_cmd, sig_to_exec_cmd = pyqtSignal(str), pyqtSignal(str)
    sig_test, sig_to_test = pyqtSignal(), pyqtSignal()

    def __init__(self,
                 parent: QWidget,
                 object_name="controller",
                 virtual_mode=False):
        super().__init__(parent=parent, object_name=object_name)
        self.m_worker = ControllerPluginWorker(self, object_name="worker")
        self.setupUi()
        self.setupLogic()
        self.set_command_text(text="synchclock 4 9876")
        self.m_worker.start_thread()

    def to_delete(self):
        self.m_worker.stop_thread()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def setupUi(self):
        # message box
        self.add_widget(
            QPSLTextListWidget(self,
                               object_name="message_box",
                               auto_scale=False))

        # control panel
        self.add_widget(QPSLHSplitter(self, object_name="control_panel"))

        self.control_panel.addWidget(
            QPSLTextLineEdit(self.control_panel,
                             object_name="edit_command",
                             key_text="cmd:",
                             stretch=[1, 5]))
        self.control_panel.addWidget(
            QPSLPushButton(self.control_panel,
                           object_name="btn_command",
                           text="exec"))
        self.control_panel.setMinimumHeight(60)
        self.control_panel.setMaximumHeight(100)

        # test button
        self.add_widget(QPSLPushButton(self, "btn_test"))
        self.btn_test.setMinimumHeight(60)
        self.btn_test.setMaximumHeight(100)

        # stretch
        self.set_stretch(sizes=[10, 1, 1])

    @QPSLObjectBase.log_decorator()
    def setupLogic(self):
        connect_blocked(self.sig_worker_delete, self.m_worker.to_delete)
        #synch/asynch
        connect_queued_and_blocked(self.sig_to_exec_cmd, self.sig_exec_cmd,
                                   self.m_worker.on_command_exec)
        connect_queued_and_blocked(self.sig_to_test, self.sig_test,
                                   self.m_worker.on_command_test)

        connect_direct(self.btn_command.sig_clicked,
                       self.sig_to_exec_current_cmd)
        connect_direct(self.edit_command.sig_return_pressed,
                       self.sig_to_exec_current_cmd)
        connect_direct(self.sig_to_exec_current_cmd, self.exec_current_command)

        connect_direct(self.btn_test.sig_clicked, self.sig_to_test)

    @property
    def message_box(self) -> QPSLTextListWidget:
        return self.get_widget(0)

    @property
    def control_panel(self) -> QPSLSplitter:
        return self.get_widget(1)

    @property
    def edit_command(self) -> QPSLTextLineEdit:
        return self.control_panel.widget(0)

    @property
    def btn_command(self) -> QPSLPushButton:
        return self.control_panel.widget(1)

    @property
    def btn_test(self) -> QPSLPushButton:
        return self.get_widget(2)

    @QPSLObjectBase.log_decorator()
    def set_command_text(self, text: str):
        self.edit_command.set_text(text=text)

    @QPSLObjectBase.log_decorator()
    def exec_current_command(self):
        cmd = self.edit_command.text()
        self.edit_command.clear()
        self.sig_to_exec_cmd.emit(cmd)

    @QPSLObjectBase.log_decorator()
    def closeEvent(self, event: QCloseEvent):
        self.m_worker.stop_thread()
        return super().closeEvent(event)


MainWidget = ControllerPluginUI
