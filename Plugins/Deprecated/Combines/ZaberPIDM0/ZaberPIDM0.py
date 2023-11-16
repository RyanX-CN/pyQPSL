from Tool import *


class ZaberPIDMPluginWorker(QPSLWorker):
    sig_work_started=pyqtSignal()
    sig_work_stop=pyqtSignal()
    sig_work_stopped=pyqtSignal()
    sig_zaber_move = pyqtSignal(float)
    sig_zaber_move_over = pyqtSignal([],[float])
    sig_pi_move = pyqtSignal(float)
    sig_pi_move_over = pyqtSignal([],[float])
    sig_dm_send=pyqtSignal(str)
    sig_dm_send_over=pyqtSignal()

    def __init__(self, parent):
        super(ZaberPIDMPluginWorker, self).__init__(parent=parent)
        
    @QPSLObjectBase.logger_decorator
    def start_work(self):
        try:
            self.m_keep_work=True
            self.sig_work_started.emit()
            for zp in float_range(self.m_zaber_from, self.m_zaber_to, self.m_zaber_step):
                if not self.m_keep_work:
                    self.report_status("work was aborted")
                    return
                self.sig_zaber_move.emit(zp)
                waiter = QPSLWait(None, self.sig_zaber_move_over)
                waiter.start_wait(1000)
                if waiter.m_result == False:
                    self.report_status("zaber late for position:%f" % zp)
                    return
                self.sig_zaber_move_over[float].emit(zp)

                for pp in float_range(self.m_pi_from, self.m_pi_to, self.m_pi_step):
                    if not self.m_keep_work:
                        self.report_status("work was aborted")
                        return
                    self.sig_pi_move.emit(pp)
                    waiter = QPSLWait(None, self.sig_pi_move_over)
                    waiter.start_wait(1000)
                    if waiter.m_result == False:
                        self.report_status("pi late for position:%f" % pp)
                        return
                    self.sig_pi_move_over[float].emit(pp)
                    
                    for dm_index in range(1, self.m_dm_file_number+1, 1):
                        if not self.m_keep_work:
                            self.report_status("work was aborted")
                            return
                        self.sig_dm_send.emit("%s\\%d.txt"%(self.m_dm_path,dm_index))
                        waiter = QPSLWait(None, self.sig_dm_send_over)
                        waiter.start_wait(1000)
                        if waiter.m_result == False:
                            self.report_status("dm send late: %s\\%d.txt" % (self.m_dm_path,dm_index))
                            return
                    
                    ### choose best dm
                    best_dm=random.randint(0,self.m_dm_file_number-1)
                    print("zaber = %f, pi = %f, best_dm = %d"%(zp, pp, best_dm))
                    self.sig_dm_send.emit("%s\\%d.txt"%(self.m_dm_path,best_dm))
                    waiter = QPSLWait(None, self.sig_dm_send_over)
                    waiter.start_wait(1000)
                    if waiter.m_result == False:
                        self.report_status("dm send late: %s\\%d.txt" % (self.m_dm_path,best_dm))
                        return
        except BaseException as e:
            raise e
        finally:
            self.sig_work_stopped.emit()
    
    @QPSLObjectBase.logger_decorator
    def stop_work(self):
        self.m_keep_work=False


class ZaberPIDMPluginUI(QPSLDockWidget):
    def __init__(self, parent):
        super(ZaberPIDMPluginUI, self).__init__(parent=parent)
        self.m_zaber_path = 'Plugins.ZaberPlugin.ZaberPlugin'
        self.m_pi_path = 'Plugins.PIPlugin.PIPlugin'
        self.m_galvano_path = 'Plugins.GalvanoPlugin.GalvanoPlugin'
        self.m_dm_path = 'Externals.dm_control.dm_control'
        self.setupUi()
        self.setupLogic()

    @QPSLObjectBase.logger_decorator
    def setupUi(self):

        # box
        self.m_box_content = QPSLSplitter(self, Qt.Orientation.Horizontal)
        self.setWidget(self.m_box_content)

        # # subplugins
        self.m_box_subplugins = QPSLSplitter(
            self.m_box_content, Qt.Orientation.Vertical)

        # # # zaber page
        self.m_zaber_class = getattr(
            import_module(self.m_zaber_path), "MainWidget")
        self.m_zaber = self.m_zaber_class(self.m_box_subplugins)
        self.m_zaber.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.m_zaber.setWindowTitle("zaber")

        # # # pi page
        self.m_pi_class = getattr(import_module(self.m_pi_path), "MainWidget")
        self.m_pi = self.m_pi_class(self.m_box_subplugins)
        self.m_pi.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.m_pi.setWindowTitle("pi")

        # # # dm page
        self.m_dm_class = getattr(import_module(self.m_dm_path), "MainWidget")
        self.m_dm = self.m_dm_class(self.m_box_subplugins)
        self.m_dm.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.m_dm.setWindowTitle("dm")

        # # # galvano page
        self.m_galvano_class = getattr(
            import_module(self.m_galvano_path), "MainWidget")
        self.m_galvano = self.m_galvano_class(self.m_box_subplugins)
        self.m_galvano.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.m_galvano.setWindowTitle("galvano")

        # # procedure
        self.m_box_procedure = QPSLSplitter(
            self.m_box_content, Qt.Orientation.Vertical)

        # # # zaber procedure
        self.m_zaber_procedure = QPSLSplitter(
            self.m_box_procedure, Qt.Orientation.Vertical)

        # # # # zaber range
        self.m_zaber_range = QPSLSplitter(
            self.m_zaber_procedure, Qt.Orientation.Horizontal)
        zaber_min, zaber_max = self.m_zaber.m_slider.range()
        self.m_label_zaber_range = QPSLLabel(self.m_zaber_range,"zaber:")
        self.m_spin_zaber_from = QPSLDoubleSpinBox(
            self.m_zaber_range, zaber_min, zaber_min, zaber_max, "from:")
        self.m_spin_zaber_to = QPSLDoubleSpinBox(
            self.m_zaber_range, zaber_max, zaber_min, zaber_max, "to:")
        self.m_spin_zaber_step = QPSLDoubleSpinBox(
            self.m_zaber_range, (zaber_max-zaber_min)/10, 0, zaber_max-zaber_min, "step:")

        # # # # zaber progress
        self.m_zaber_progress = QPSLProgressBar(self.m_zaber_procedure)
        self.m_zaber_progress.setRange(0, 4)

        # # # pi procedure
        self.m_pi_procedure = QPSLSplitter(
            self.m_box_procedure, Qt.Orientation.Vertical)

        # # # # pi range
        self.m_pi_range = QPSLSplitter(
            self.m_pi_procedure, Qt.Orientation.Horizontal)
        pi_min, pi_max = self.m_pi.m_slider.range()
        self.m_label_pi_range = QPSLLabel(self.m_pi_range,"pi:")
        self.m_spin_pi_from = QPSLDoubleSpinBox(
            self.m_pi_range, pi_min, pi_min, pi_max, "from:")
        self.m_spin_pi_to = QPSLDoubleSpinBox(
            self.m_pi_range, pi_max, pi_min, pi_max, "to:")
        self.m_spin_pi_step = QPSLDoubleSpinBox(
            self.m_pi_range, (pi_max-pi_min)/5, 0, pi_max-pi_min, "step:")

        # # # # pi progress
        self.m_pi_progress = QPSLProgressBar(self.m_pi_procedure)
        self.m_pi_progress.setRange(0, 4)

        # # # dm procedure
        self.m_dm_procedure = QPSLSplitter(
            self.m_box_procedure, Qt.Orientation.Vertical)

        # # # # dm range
        self.m_dm_range = QPSLSplitter(
            self.m_dm_procedure, Qt.Orientation.Horizontal)
        self.m_label_dm_range = QPSLLabel(self.m_dm_range,"dm:")
        self.m_dm_path = QPSLChooseOpenDirButton(self.m_dm_range)
        self.m_dm_file_number = QPSLSpinBox(self.m_dm_range,10,1,10000,"file number")

        # # # # dm progress
        self.m_dm_progress = QPSLProgressBar(self.m_dm_procedure)
        self.m_dm_progress.setRange(0, 4)

        # # # galvano procedure
        self.m_galvano_procedure = QPSLSplitter(
            self.m_box_procedure, Qt.Orientation.Vertical)

        # # # # galvano range
        self.m_galvano_path = QPSLChooseSaveFileButton(self.m_dm_procedure)
        # # # # galvano progress
        self.m_galvano_progress = QPSLProgressBar(self.m_galvano_procedure)
        self.m_galvano_progress.setRange(0, 4)

        # # # main procedure
        self.m_main_procedure = QPSLSplitter(
            self.m_box_procedure, Qt.Orientation.Vertical)

        self.m_button_switch = QPSLToggleButton(
            self.m_main_procedure, "start", "stop")

    @QPSLObjectBase.logger_decorator
    def setupLogic(self):
        self.m_worker = ZaberPIDMPluginWorker(self)

        # zaber
        self.m_worker.init_and_connect_attr(
            self.m_spin_zaber_from.sig_value_changed, "m_zaber_from", self.m_spin_zaber_from.value())
        self.m_worker.init_and_connect_attr(
            self.m_spin_zaber_to.sig_value_changed, "m_zaber_to", self.m_spin_zaber_to.value())
        self.m_worker.init_and_connect_attr(
            self.m_spin_zaber_step.sig_value_changed, "m_zaber_step", self.m_spin_zaber_step.value())
        
        self.m_spin_zaber_from.editingFinished.connect(self.adjust_zaber_progress)
        self.m_spin_zaber_to.editingFinished.connect(self.adjust_zaber_progress)
        self.m_worker.sig_zaber_move_over[float].connect(self.show_zaber_progress, Qt.ConnectionType.QueuedConnection)

        self.m_worker.sig_zaber_move.connect(
            self.m_zaber.m_worker.move_absolute_distance, Qt.ConnectionType.QueuedConnection)
        self.m_zaber.m_worker.sig_move_over.connect(
            self.m_worker.sig_zaber_move_over, Qt.ConnectionType.QueuedConnection)

        # pi
        self.m_worker.init_and_connect_attr(
            self.m_spin_pi_from.sig_value_changed, "m_pi_from", self.m_spin_pi_from.value())
        self.m_worker.init_and_connect_attr(
            self.m_spin_pi_to.sig_value_changed, "m_pi_to", self.m_spin_pi_to.value())
        self.m_worker.init_and_connect_attr(
            self.m_spin_pi_step.sig_value_changed, "m_pi_step", self.m_spin_pi_step.value())
        
        self.m_spin_pi_from.editingFinished.connect(self.adjust_pi_progress)
        self.m_spin_pi_to.editingFinished.connect(self.adjust_pi_progress)
        self.m_worker.sig_pi_move_over[float].connect(lambda x:self.m_pi_progress.setValue(x*10000), Qt.ConnectionType.QueuedConnection)

        self.m_worker.sig_pi_move.connect(
            self.m_pi.m_worker.move_absolute_distance, Qt.ConnectionType.QueuedConnection)
        self.m_pi.m_worker.sig_move_over.connect(
            self.m_worker.sig_pi_move_over, Qt.ConnectionType.QueuedConnection)

        # dm
        self.m_worker.init_and_connect_attr(
            self.m_dm_path.sig_choose_open_dir_name[str], "m_dm_path", self.m_dm_path.m_path)
        self.m_worker.init_and_connect_attr(
            self.m_dm_file_number.sig_value_changed, "m_dm_file_number", self.m_dm_file_number.value())
        
        self.m_worker.sig_dm_send.connect(
            self.m_dm.send_file_array, Qt.ConnectionType.QueuedConnection)
        self.m_dm.sig_send_over.connect(
            self.m_worker.sig_dm_send_over, Qt.ConnectionType.QueuedConnection)

        
        # start stop
        self.m_button_switch.sig_open.connect(self.m_worker.start_work, Qt.ConnectionType.QueuedConnection)
        self.m_worker.sig_work_started.connect(self.m_button_switch.set_opened, Qt.ConnectionType.QueuedConnection)
        self.m_button_switch.sig_close.connect(self.m_worker.stop_work, Qt.ConnectionType.QueuedConnection)
        self.m_worker.sig_work_stopped.connect(self.m_button_switch.set_closed, Qt.ConnectionType.QueuedConnection)

        self.m_worker.start_thread()

    @QPSLObjectBase.logger_decorator
    def adjust_zaber_progress(self):
        self.m_zaber_progress.setRange(self.m_spin_zaber_from*10000,self.m_spin_zaber_to*10000)
    
    @QPSLObjectBase.logger_decorator
    def show_zaber_progress(self, val):
        self.m_zaber_progress.setValue(val*10000)
    
    @QPSLObjectBase.logger_decorator
    def adjust_pi_progress(self):
        self.m_pi_progress.setRange(self.m_spin_pi_from*10000,self.m_spin_pi_to*10000)

MainWidget = ZaberPIDMPluginUI
