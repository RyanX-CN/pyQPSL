from Tool import *
from Plugins.OpticalImages.Logics.api import Reconstruction_Read_Sample_Dcimg, Reconstruction_Work
from Plugins.OpticalImages.Logics.api import Pretreatment_Read_TIFF_img, Calibration_Work
from Plugins.OpticalImages.Logics.api import Pretreatment_Read_TIFF_Division_img
from Plugins.OpticalImages.Logics.api import Pretreatment_Read_Flatten_img, Flatten_Work
from Plugins.OpticalImages.Logics.api import Reconstruction2_Work

os_path_append("./Plugins/OpticalImages/bin")
from Plugins.OpticalImages.OpticalImageAPI import Divisor


class OpticalImagePluginWorker(QPSLWorker):
    sig_get_dcimg_sample_data = pyqtSignal(np.ndarray)
    sig_get_dcimg_input_files = pyqtSignal(list)
    sig_reconstruction_started = pyqtSignal()
    sig_reconstruction_report = pyqtSignal(int)
    sig_reconstruction_stopped = pyqtSignal()
    sig_get_tiff_data = pyqtSignal(np.ndarray)
    sig_get_flatten_data = pyqtSignal(np.ndarray, np.ndarray)
    sig_get_tiff_division_data = pyqtSignal(np.ndarray)
    sig_calibration_started = pyqtSignal()
    sig_calibration_report = pyqtSignal(int)
    sig_calibration_stopped = pyqtSignal()
    sig_division_image = pyqtSignal(np.ndarray)
    sig_divide_all_over = pyqtSignal(np.ndarray)
    sig_get_flatten_input_files = pyqtSignal(list)
    sig_flatten_started = pyqtSignal()
    sig_flatten_report = pyqtSignal(int)
    sig_flatten_stopped = pyqtSignal()
    sig_reconstruction2_started = pyqtSignal()
    sig_reconstruction2_report = pyqtSignal(int)
    sig_reconstruction2_stopped = pyqtSignal()

    def __init__(self, parent: QObject, object_name: str, virtual_mode: bool):
        super(OpticalImagePluginWorker, self).__init__(parent=parent,
                                                       object_name=object_name)
        self.m_virtual_mode = virtual_mode

    @QPSLObjectBase.log_decorator()
    def on_get_sample_dcimg_filename(self, sample_input_path: str):
        if not sample_input_path:
            self.add_error("no valid input path")
            self.sig_get_tiff_data.emit(None)
            return
        Reconstruction_Read_Sample_Dcimg(
            img_path=sample_input_path,
            report_signal=self.sig_get_dcimg_sample_data)

    @QPSLObjectBase.log_decorator()
    def on_get_dcimg_input_dir(self, input_path: str):
        if not input_path:
            self.add_error("no valid input path")
            return
        files = os.listdir(input_path)
        self.sig_get_dcimg_input_files.emit(files)

    @QPSLObjectBase.log_decorator()
    def on_get_tiff_filename(self, tiff_path: str):
        if not tiff_path:
            self.add_error("no valid input path")
            self.sig_get_tiff_data.emit(None)
            return
        Pretreatment_Read_TIFF_img(img_path=tiff_path,
                                   report_signal=self.sig_get_tiff_data)

    @QPSLObjectBase.log_decorator()
    def on_get_tiff_division_filename(self, tiff_path: str):
        if not tiff_path:
            self.add_error("no valid input path")
            self.sig_get_tiff_division_data.emit(None)
            return
        Pretreatment_Read_TIFF_Division_img(
            img_path=tiff_path, report_signal=self.sig_get_tiff_division_data)

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_input_dir(self, input_path: str):
        if not input_path:
            self.add_error("no valid input path")
            return
        files = os.listdir(input_path)
        self.sig_get_flatten_input_files.emit(files)

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_input_save_dirs(self, input_path: str, save_path: str):
        if not input_path or not save_path:
            self.add_error("no valid input path")
            self.sig_get_flatten_data.emit(None, None)
            return
        Pretreatment_Read_Flatten_img(input_path=input_path,
                                      save_path=save_path,
                                      report_signal=self.sig_get_flatten_data)

    @QPSLObjectBase.log_decorator()
    def on_reconstruction_work(self, reconstruction_parameter: Dict):
        Reconstruction_Work(parameters=reconstruction_parameter,
                            start_signal=self.sig_reconstruction_started,
                            report_signal=self.sig_reconstruction_report,
                            stop_signal=self.sig_reconstruction_stopped)

    @QPSLObjectBase.log_decorator()
    def on_calibration_work(self, calibration_parameter: Dict):
        Calibration_Work(parameters=calibration_parameter,
                         start_signal=self.sig_calibration_started,
                         report_signal=self.sig_calibration_report,
                         stop_signal=self.sig_calibration_stopped)

    @QPSLObjectBase.log_decorator()
    def on_divide_image(self, task_queue: deque):
        if task_queue:
            while task_queue:
                img, divide_down_ratio, binary_thresh, radius = task_queue.popleft(
                )
            divisor = Divisor()
            divisor.set_graph_data(img.copy())
            divisor.set_divide_down_ratio(divide_down_ratio=divide_down_ratio)
            divisor.set_binary_thresh(binary_thresh=binary_thresh)
            divisor.set_radius(radius=radius)
            divisor.run()
            img = divisor.get_result_data()
            self.sig_division_image.emit(img)

    @QPSLObjectBase.log_decorator()
    def divide_all_images(self, tasks):
        divisor = Divisor()
        res = []
        for img, divide_down_ratio, binary_thresh, radius in tasks:
            divisor.set_graph_data(img.copy())
            divisor.set_divide_down_ratio(divide_down_ratio=divide_down_ratio)
            divisor.set_binary_thresh(binary_thresh=binary_thresh)
            divisor.set_radius(radius=radius)
            divisor.run()
            img = divisor.get_result_data()
            res.append(img)
        self.sig_divide_all_over.emit(np.stack(res, axis=0))

    @QPSLObjectBase.log_decorator()
    def on_flatten_work(self, flatten_parameter: Dict):
        Flatten_Work(parameters=flatten_parameter,
                     start_signal=self.sig_flatten_started,
                     report_signal=self.sig_flatten_report,
                     stop_signal=self.sig_flatten_stopped)

    @QPSLObjectBase.log_decorator()
    def on_reconstruction2_work(self, reconstruction2_parameter: Dict):
        Reconstruction2_Work(parameters=reconstruction2_parameter,
                             start_signal=self.sig_reconstruction2_started,
                             report_signal=self.sig_reconstruction2_report,
                             stop_signal=self.sig_reconstruction2_stopped)


class OpticalImagePluginUI(QPSLTabWidget):
    sig_worker_delete = pyqtSignal()
    sig_to_get_dcimg_sample_data = pyqtSignal(str)
    sig_to_get_tiff_data = pyqtSignal(str)
    sig_to_get_tiff_division_data = pyqtSignal(str)
    sig_to_get_flatten_data = pyqtSignal(str, str)

    sig_start_reconstruction_work = pyqtSignal([dict])
    sig_start_calibration_work = pyqtSignal([dict])
    sig_start_flatten_work = pyqtSignal([dict])
    sig_start_reconstruction2_work = pyqtSignal([dict])

    def __init__(self,
                 parent: QWidget,
                 object_name="OpticalImages",
                 virtual_mode=False,
                 font_family="Arial"):
        super(OpticalImagePluginUI, self).__init__(parent=parent,
                                                   object_name=object_name)
        self.m_dcimg_sample_img_data: np.ndarray = None
        self.m_reconstruction_parameters: dict = dict()
        self.m_reconstruction_state_controller: SharedStateController = SharedStateController(
        )
        self.m_calibration_img_data: np.ndarray = None
        self.m_calibration_parameters: dict = dict()
        self.m_calibration_state_controller: SharedStateController = SharedStateController(
        )
        self.m_flatten_parameters: dict = dict()
        self.m_flatten_state_controller: SharedStateController = SharedStateController(
        )
        self.m_reconstruction2_parameters: dict = dict()
        self.m_reconstruction2_state_controller: SharedStateController = SharedStateController(
        )
        # worker
        self.m_worker = OpticalImagePluginWorker(self,
                                                 object_name="worker",
                                                 virtual_mode=virtual_mode)
        self.setupUi()
        self.setupStyle()
        self.setupLogic()
        self.m_worker.start_thread()
        self.resize(500, 800)

    def to_delete(self):
        self.sig_worker_delete.emit()
        self.m_worker.stop_thread()
        return super().to_delete()

    @QPSLObjectBase.log_decorator()
    def setupUi(self):

        def setup_reconstruction():

            def setup_points():
                self.tab_reconstruction.add_widget(
                    widget=QPSLGridGroupList(self.tab_reconstruction,
                                             object_name="box_points",
                                             title="sample..."))
                self.box_reconstruction_points.add_widget_simple(
                    widget=QPSLGetOpenFileBox(
                        self.box_reconstruction_points,
                        object_name="box_get_sample_input_path",
                        text="sample input:",
                        path="J:/Raw Data/20220830_1/"),
                    grid=(0, 0, 0, 1))
                self.box_reconstruction_points.add_widget_simple(
                    widget=QPSLTextListWidget(self.box_reconstruction_points,
                                              object_name="list_points",
                                              auto_scale=False),
                    grid=(1, 2, 0, 1))
                self.box_reconstruction_points.add_widget_simple(
                    widget=QPSLPushButton(self.box_reconstruction_points,
                                          object_name="btn_show_sample",
                                          text="show sample image"),
                    grid=(0, 0, 2, 2))
                self.box_reconstruction_points.add_widget_simple(
                    widget=QPSLPushButton(self.box_reconstruction_points,
                                          object_name="btn_delete_point",
                                          text="delete"),
                    grid=(1, 1, 2, 2))
                self.box_reconstruction_points.add_widget_simple(
                    widget=QPSLPushButton(self.box_reconstruction_points,
                                          object_name="btn_clear_points",
                                          text="clear"),
                    grid=(2, 2, 2, 2))
                self.box_reconstruction_points.set_stretch(row_sizes=(1, 1, 1),
                                                           column_sizes=(1, 1,
                                                                         1))

            def setup_parameters():
                self.tab_reconstruction.add_widget(
                    widget=QPSLVerticalGroupList(self.tab_reconstruction,
                                                 object_name="box_parameters",
                                                 title="parameters..."))
                self.box_reconstruction_parameters.setContentsMargins(
                    0, 15, 0, 0)
                self.box_reconstruction_parameters.set_spacing(spacing=2)
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLTextLineEdit(self.box_reconstruction_parameters,
                                            object_name="edit_name_prefix",
                                            key_text="name prefix: "))
                self.edit_reconstruction_name_prefix.setContentsMargins(
                    0, 0, 0, 0)

                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLGridGroupList(
                        self.box_reconstruction_parameters,
                        object_name="box_parameters_xy"))
                self.box_reconstruction_parameters_xy.setContentsMargins(
                    0, 0, 0, 0)
                self.box_reconstruction_parameters_xy.set_spacing(spacing=2)
                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLSpinBox(self.box_reconstruction_parameters_xy,
                                       object_name="spin_overlap_x",
                                       min=-1000000,
                                       max=1000000,
                                       value=510,
                                       prefix="OverLap X:"),
                    grid=(0, 0, 0, 0))
                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLDoubleSpinBox(
                        self.box_reconstruction_parameters_xy,
                        object_name="spin_scale_x",
                        min=-1000000,
                        max=1000000,
                        value=1,
                        prefix="scale X:",
                        decimals=4),
                    grid=(1, 1, 0, 0))
                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLDoubleSpinBox(
                        self.box_reconstruction_parameters_xy,
                        object_name="spin_resolve_x",
                        min=1,
                        max=1000000,
                        value=3,
                        prefix="resolve X:",
                        suffix=" um."),
                    grid=(2, 2, 0, 0))

                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLSpinBox(self.box_reconstruction_parameters_xy,
                                       object_name="spin_overlap_y",
                                       min=-1000000,
                                       max=1000000,
                                       value=0,
                                       prefix="OverLap Y:"),
                    grid=(0, 0, 1, 1))
                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLDoubleSpinBox(
                        self.box_reconstruction_parameters_xy,
                        object_name="spin_scale_y",
                        min=-1000000,
                        max=1000000,
                        value=0.8125,
                        prefix="scale Y:",
                        decimals=4),
                    grid=(1, 1, 1, 1))
                self.box_reconstruction_parameters_xy.add_widget_simple(
                    widget=QPSLDoubleSpinBox(
                        self.box_reconstruction_parameters_xy,
                        object_name="spin_resolve_y",
                        min=1,
                        max=1000000,
                        value=3,
                        prefix="resolve Y:",
                        suffix=" um."),
                    grid=(2, 2, 1, 1))

                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLSpinBox(self.box_reconstruction_parameters,
                                       object_name="spin_block_num",
                                       min=1,
                                       max=100000,
                                       value=100,
                                       prefix="block num:"))
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLSpinBox(self.box_reconstruction_parameters,
                                       object_name="spin_spacing",
                                       min=1,
                                       max=100000,
                                       value=1,
                                       prefix="spacing:"))
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLGetDirectoryBox(
                        self.box_reconstruction_parameters,
                        object_name="box_get_input_path",
                        text="input path:",
                        path=
                        "J:/Results/result_dzh/human_brain_slice/22_08_30/recon/"
                    ))
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLGetDirectoryBox(
                        self.box_reconstruction_parameters,
                        object_name="box_get_save_path",
                        text="save path:"))
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLTextListWidget(
                        self.box_reconstruction_parameters,
                        object_name="list_input_files",
                        auto_scale=False,
                        mode=QAbstractItemView.SelectionMode.MultiSelection))
                self.box_reconstruction_parameters.add_widget(
                    widget=QPSLToggleButton(self.box_reconstruction_parameters,
                                            object_name="btn_switch",
                                            closed_text="start",
                                            opened_text="stop"))

                OverLap_dict = {2.9: 260, 2.8: 323, 2.7: 390, 2.5: 510, 2: 815}
                OverLap_suffix = [
                    "for fast reconstruct : ScaleX = 2/3, ScaleY =1/2",
                    "for isotropic reconstruct : ScaleX = 1, ScaleY =1.625/2",
                    "no downsampling in xy plane: ScaleX =2/1.625, ScaleY = 1"
                ]
                OverLap_tip = "\n".join(
                    itertools.chain(("%.1f mm -- %d pixel" % (k, v)
                                     for k, v in OverLap_dict.items()),
                                    OverLap_suffix))
                self.spin_reconstruction_overlap_x.setToolTip(OverLap_tip)
                self.spin_reconstruction_overlap_y.setToolTip(OverLap_tip)

                self.box_reconstruction_parameters.set_stretch(sizes=(1, 3, 1,
                                                                      1, 1, 1,
                                                                      2, 1))

            self.add_tab(tab=QPSLVerticalGroupList(
                self, object_name="tab_reconstruction"),
                         title="reconstruction")
            self.tab_reconstruction.setContentsMargins(15, 5, 5, 5)
            setup_points()
            setup_parameters()
            self.tab_reconstruction.set_stretch(sizes=(3, 10))

        def setup_pretreatment():

            def setup_calibration():
                self.tab_pretreatment.add_widget(
                    widget=QPSLGridGroupList(self.tab_pretreatment,
                                             object_name="box_calibration",
                                             title="calibration..."))

                self.box_calibration.add_widget_simple(
                    widget=QPSLGetOpenFileBox(
                        self.box_calibration,
                        object_name="box_get_sample_input_path",
                        text="sample input:",
                        path="C:/Users/oldyan/Desktop/快捷/C2-test.tif",
                        filter=["tif", "tiff"]),
                    grid=(0, 0, 0, 1))
                self.box_calibration.add_widget_simple(
                    widget=QPSLTextListWidget(self.box_calibration,
                                              object_name="list_points",
                                              auto_scale=False),
                    grid=(1, 2, 0, 1))
                self.box_calibration.add_widget_simple(widget=QPSLPushButton(
                    self.box_calibration,
                    object_name="btn_show_sample",
                    text="show sample image"),
                                                       grid=(0, 0, 2, 2))
                self.box_calibration.add_widget_simple(widget=QPSLPushButton(
                    self.box_calibration,
                    object_name="btn_delete_point",
                    text="delete"),
                                                       grid=(1, 1, 2, 2))
                self.box_calibration.add_widget_simple(widget=QPSLPushButton(
                    self.box_calibration,
                    object_name="btn_clear_points",
                    text="clear"),
                                                       grid=(2, 2, 2, 2))
                self.box_calibration.add_widget_simple(widget=QPSLToggleButton(
                    self.box_calibration,
                    object_name="btn_switch",
                    closed_text="start",
                    opened_text="stop"),
                                                       grid=(3, 3, 0, 2))
                self.box_calibration.set_stretch(row_sizes=(2, 2, 2, 3),
                                                 column_sizes=(1, 1, 1))

            def setup_division():
                self.tab_pretreatment.add_widget(
                    widget=QPSLHorizontalGroupList(self.tab_pretreatment,
                                                   object_name="box_division",
                                                   title="division..."))
                self.box_division.add_widget(widget=QPSLGetOpenFileBox(
                    self.box_division,
                    object_name="box_get_division_path",
                    text="input:",
                    path="C:/Users/oldyan/Desktop/快捷/C2-test.tif",
                    filter=["tif", "tiff"]))
                self.box_division.add_widget(
                    widget=QPSLPushButton(self.box_division,
                                          object_name="btn_division",
                                          text="division"))
                self.box_division.set_stretch(sizes=(2, 1))

            def setup_flatten():
                self.tab_pretreatment.add_widget(
                    widget=QPSLVerticalGroupList(self.tab_pretreatment,
                                                 object_name="box_flatten",
                                                 title="flatten..."))
                self.box_flatten.add_widget(
                    widget=QPSLSpinBox(self.box_flatten,
                                       object_name="spin_thickness",
                                       min=0,
                                       max=1000000,
                                       value=185,
                                       prefix="thickness:"))
                self.box_flatten.add_widget(
                    widget=QPSLDoubleSpinBox(self.box_flatten,
                                             object_name="spin_zsize",
                                             min=0,
                                             max=1000000,
                                             value=2.300,
                                             prefix="zsize:",
                                             decimals=3))
                self.box_flatten.add_widget(widget=QPSLHChoiceGroup(
                    self.box_flatten,
                    object_name="box_use_up_plane",
                    items=["use up plane", "not use up plane"]))
                self.box_flatten.add_widget(widget=QPSLGetDirectoryBox(
                    self.box_flatten,
                    object_name="box_get_flatten_input_path",
                    path=
                    "J:/Results/result_dzh/human_brain_slice/22_08_30/recon/",
                    text="input path:"))
                self.box_flatten.add_widget(widget=QPSLGetDirectoryBox(
                    self.box_flatten,
                    object_name="box_get_flatten_save_path",
                    path=
                    "J:/Results/result_dzh/human_brain_slice/22_08_30/flatten/",
                    text="save path:"))
                self.box_flatten.add_widget(
                    widget=QPSLTextLineEdit(self.box_flatten,
                                            object_name="edit_name_pre",
                                            key_text="name prefix:"))
                self.edit_flatten_name_prefix.set_text(text="C2-test")
                self.box_flatten.add_widget(widget=QPSLTextListWidget(
                    self.box_flatten,
                    object_name="list_flatten_input_files",
                    auto_scale=False,
                    mode=QAbstractItemView.SelectionMode.SingleSelection))

                self.box_flatten.add_widget(widget=QPSLHorizontalGroupList(
                    self.box_flatten, object_name="box_flatten_control"))
                self.box_flatten_control.add_widget(
                    widget=QPSLToggleButton(self.box_flatten_control,
                                            object_name="btn_flatten_switch",
                                            closed_text="start",
                                            opened_text="stop"))
                self.box_flatten_control.add_widget(
                    widget=QPSLPushButton(self.box_flatten_control,
                                          object_name="btn_flatten_show",
                                          text="show"))

                self.box_flatten.set_stretch(sizes=(2, 2, 2, 2, 2, 2, 4, 3))

            self.add_tab(tab=QPSLVerticalGroupList(
                self, object_name="tab_pretreatment"),
                         title="pretreatment")
            setup_calibration()
            setup_division()
            setup_flatten()
            self.tab_pretreatment.set_stretch(sizes=(20, 10, 43))

        def setup_reconstruction2():
            self.add_tab(tab=QPSLVerticalGroupList(
                self, object_name="tab_reconstruction2"),
                         title="reconstruction2")
            self.tab_reconstruction2.add_widget(
                widget=QPSLGetOpenFileBox(self.tab_reconstruction2,
                                          object_name="box_get_path",
                                          text="input path:"))
            self.tab_reconstruction2.add_widget(
                widget=QPSLTextLineEdit(self.tab_reconstruction2,
                                        object_name="edit_name_prefix",
                                        key_text="name prefix:"))
            self.edit_reconstruction2_name_prefix.set_text(
                text='1_27_2_humanbrain_slice_')
            self.tab_reconstruction2.add_widget(
                widget=QPSLTextLineEdit(self.tab_reconstruction2,
                                        object_name="edit_name_suffix",
                                        key_text="name suffix:"))
            self.edit_reconstruction2_name_suffix.set_text(
                text='_bkgd_illu_cor_flatten.tif')
            self.tab_reconstruction2.add_widget(
                widget=QPSLHChoiceGroup(self.tab_reconstruction2,
                                        object_name="box_choice",
                                        items=["use 去条纹", "not use 去条纹"]))
            self.tab_reconstruction2.add_widget(widget=QPSLTableWidget(
                self.tab_reconstruction2, object_name="table"))
            self.table_reconstruction2.setColumnCount(2)
            self.table_reconstruction2.setColumnWidth(0, 200)
            self.table_reconstruction2.setColumnWidth(1, 300)
            self.table_reconstruction2.setHorizontalHeaderLabels(
                "脑片编号 脑片截面序号".split())
            self.table_reconstruction2.setRowCount(20)
            self.table_reconstruction2.setVerticalHeaderLabels(
                map(str, range(20)))
            self.tab_reconstruction2.add_widget(
                widget=QPSLPushButton(self.tab_reconstruction2,
                                      object_name="btn_add_row",
                                      text="add row"))
            self.tab_reconstruction2.add_widget(
                widget=QPSLToggleButton(self.tab_reconstruction2,
                                        object_name="btn_start",
                                        closed_text="start",
                                        opened_text="stop"))
            self.tab_reconstruction2.set_stretch(sizes=(1, 1, 1, 1, 10, 1, 1))

        setup_reconstruction()
        setup_pretreatment()
        setup_reconstruction2()

    @QPSLObjectBase.log_decorator()
    def setupStyle(self):
        pass

    @QPSLObjectBase.log_decorator()
    def setupLogic(self):
        connect_blocked(self.sig_worker_delete, self.m_worker.to_delete)

        # reconstruction sample img data
        connect_direct(
            self.box_reconstruction_get_sample_input.sig_path_changed[str],
            self.load_dcimg_sample)
        connect_queued(self.sig_to_get_dcimg_sample_data,
                       self.m_worker.on_get_sample_dcimg_filename)
        connect_queued(self.m_worker.sig_get_dcimg_sample_data,
                       self.on_get_dcimg_sample_data)
        connect_direct(self.btn_reconstruction_show_sample_image.sig_clicked,
                       self.on_show_sample_dcimg)

        # reconstruction sample img points
        connect_direct(
            self.btn_reconstruction_delete_sample_point.sig_clicked,
            self.list_reconstruction_sample_points.remove_selected_item)
        connect_direct(self.btn_reconstruction_clear_sample_points.sig_clicked,
                       self.list_reconstruction_sample_points.clear)

        # reconstruction input files
        connect_queued(
            self.box_reconstruction_get_input_path.sig_path_changed[str],
            self.m_worker.on_get_dcimg_input_dir)
        connect_queued(self.m_worker.sig_get_dcimg_input_files,
                       self.on_get_dcimg_input_files)

        # reconstruction work
        connect_direct(self.btn_reconstruction_switch.sig_open,
                       self.click_start_reconstruction)
        connect_direct(self.btn_reconstruction_switch.sig_close,
                       self.click_stop_reconstruction)
        connect_direct(self.m_worker.sig_reconstruction_started,
                       self.btn_reconstruction_switch.set_opened)
        connect_direct(self.m_worker.sig_reconstruction_stopped,
                       self.btn_reconstruction_switch.set_closed)
        connect_queued(self.sig_start_reconstruction_work,
                       self.m_worker.on_reconstruction_work)
        connect_queued(self.m_worker.sig_reconstruction_report,
                       self.on_receive_reconstruction_report)
        connect_queued(self.m_worker.sig_reconstruction_stopped,
                       self.on_reconstruction_stopped)

        # calibration tiff img data
        connect_direct(self.box_get_calibration_input.sig_path_changed[str],
                       self.load_tiff)
        connect_queued(self.sig_to_get_tiff_data,
                       self.m_worker.on_get_tiff_filename)
        connect_queued(self.m_worker.sig_get_tiff_data, self.on_get_tiff_data)
        connect_direct(self.btn_show_calibration_image.sig_clicked,
                       self.on_show_tiff_image)

        # calibration points
        connect_direct(self.btn_delete_calibration_point.sig_clicked,
                       self.list_calibration_points.remove_selected_item)
        connect_direct(self.btn_clear_calibration_points.sig_clicked,
                       self.list_calibration_points.clear)

        # calibration work
        connect_direct(self.btn_calibration_switch.sig_open,
                       self.click_start_calibration)
        connect_direct(self.btn_calibration_switch.sig_close,
                       self.click_stop_calibration)
        connect_direct(self.m_worker.sig_calibration_started,
                       self.btn_calibration_switch.set_opened)
        connect_direct(self.m_worker.sig_calibration_stopped,
                       self.btn_calibration_switch.set_closed)
        connect_queued(self.sig_start_calibration_work,
                       self.m_worker.on_calibration_work)
        connect_queued(self.m_worker.sig_calibration_report,
                       self.on_receive_calibration_report)
        connect_queued(self.m_worker.sig_calibration_stopped,
                       self.on_calibration_stopped)

        # division tiff img data
        connect_direct(self.box_get_division_path.sig_path_changed[str],
                       self.load_tiff_division)
        connect_queued(self.sig_to_get_tiff_division_data,
                       self.m_worker.on_get_tiff_division_filename)
        connect_queued(self.m_worker.sig_get_tiff_division_data,
                       self.on_get_tiff_division_data)
        connect_direct(self.btn_division.sig_clicked,
                       self.on_division_show_tiff_image)
        connect_queued(self.m_worker.sig_divide_all_over,
                       self.show_division_result)

        # flatten input
        connect_queued(self.box_get_flatten_input_path.sig_path_changed[str],
                       self.m_worker.on_get_flatten_input_dir)
        connect_queued(self.m_worker.sig_get_flatten_input_files,
                       self.on_get_flatten_input_files)

        # flatten work
        connect_direct(self.btn_flatten_switch.sig_open,
                       self.click_start_flatten)
        connect_direct(self.btn_flatten_switch.sig_close,
                       self.click_stop_flatten)
        connect_direct(self.m_worker.sig_flatten_started,
                       self.btn_flatten_switch.set_opened)
        connect_direct(self.m_worker.sig_flatten_stopped,
                       self.btn_flatten_switch.set_closed)
        connect_queued(self.sig_start_flatten_work,
                       self.m_worker.on_flatten_work)
        connect_queued(self.m_worker.sig_flatten_report,
                       self.on_receive_flatten_report)
        connect_direct(self.m_worker.sig_flatten_stopped,
                       self.on_flatten_stopped)

        # flatten show
        connect_direct(self.btn_flatten_show.sig_clicked,
                       self.click_flatten_show)
        connect_queued(self.sig_to_get_flatten_data,
                       self.m_worker.on_get_flatten_input_save_dirs)
        connect_queued(self.m_worker.sig_get_flatten_data,
                       self.on_get_flatten_images)

        # reconstruction2
        connect_direct(self.btn_add_table_row.sig_clicked,
                       self.on_add_reconstruction2_table_row)

        # reconstruction2 work
        connect_direct(self.btn_reconstruction2_switch.sig_open,
                       self.click_start_reconstruction2)
        connect_direct(self.btn_reconstruction2_switch.sig_close,
                       self.click_stop_reconstruction2)
        connect_direct(self.m_worker.sig_reconstruction2_started,
                       self.btn_reconstruction2_switch.set_opened)
        connect_direct(self.m_worker.sig_reconstruction2_stopped,
                       self.btn_reconstruction2_switch.set_closed)
        connect_queued(self.sig_start_reconstruction2_work,
                       self.m_worker.on_reconstruction2_work)
        connect_queued(self.m_worker.sig_reconstruction2_report,
                       self.on_receive_reconstruction2_report)
        connect_direct(self.m_worker.sig_reconstruction2_stopped,
                       self.on_reconstruction2_stopped)

    @QPSLObjectBase.log_decorator()
    def load_dcimg_sample(self, dcimg_sample_file: str):
        self.sig_to_get_dcimg_sample_data.emit(dcimg_sample_file)
        self.m_waiting = QPSLWaitingDialog(None,
                                           object_name="waiting",
                                           size=QSize(200, 200))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) - QPoint(100, 100))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_get_dcimg_sample_data(self, sample_image_data: np.ndarray):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        self.m_dcimg_sample_img_data = sample_image_data

    @QPSLObjectBase.log_decorator()
    def on_get_dcimg_input_files(self, input_files: List[str]):
        self.list_reconstruction_input_files.clear()
        for file in input_files:
            file = '/'.join(
                (self.box_reconstruction_get_input_path.get_path(), file))
            self.list_reconstruction_input_files.add_item(file)

    @QPSLObjectBase.log_decorator()
    def on_show_sample_dcimg(self):
        if self.m_dcimg_sample_img_data is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3d(
            None,
            object_name="image3d",
            window_title=self.box_reconstruction_get_sample_input.get_path())
        image3d.set_image_data(image_data=self.m_dcimg_sample_img_data)
        image3d.show()
        connect_direct(image3d.sig_mouse_click, self.add_dcimg_point)

    @QPSLObjectBase.log_decorator()
    def add_dcimg_point(self, point: QPoint):
        self.list_reconstruction_sample_points.add_item_scroll(
            "%d, %d" % (point.x(), point.y()))

    @QPSLObjectBase.log_decorator()
    def prepare_construction_work(self) -> bool:
        parameters = dict()
        parameters["block_num"] = self.spin_reconstruction_block_num.value()
        parameters[
            "save_path"] = self.box_reconstruction_get_save_path.get_path()
        parameters["name_pre"] = self.edit_reconstruction_name_prefix.text()
        parameters["OverLapX"] = self.spin_reconstruction_overlap_x.value()
        parameters["OverLapY"] = self.spin_reconstruction_overlap_y.value()
        parameters["scaleX"] = self.spin_reconstruction_scale_x.value()
        parameters["scaleY"] = self.spin_reconstruction_scale_y.value()
        parameters["resolveX"] = self.spin_reconstruction_resolve_x.value()
        parameters["resolveY"] = self.spin_reconstruction_resolve_y.value()
        parameters["zspacing"] = self.spin_reconstruction_zspacing.value()
        parameters["input_files"] = [
            e.text()
            for e in self.list_reconstruction_input_files.selectedItems()
        ]
        parameters["stateController"] = self.m_reconstruction_state_controller
        self.m_reconstruction_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def click_start_reconstruction(self):
        if self.prepare_construction_work():
            self.m_reconstruction_state_controller.set_continue()
            self.m_reconstruction_progress = QPSLProgressDialog(
                None,
                object_name="progress",
                title="reconstruction progress",
                min=0,
                max=len(self.m_reconstruction_parameters["input_files"]))
            connect_direct(self.m_reconstruction_progress.canceled,
                           self.click_stop_reconstruction)
            self.m_reconstruction_progress.setLabelText(
                self.m_reconstruction_parameters["input_files"][0])
            self.m_reconstruction_progress.show()
            self.sig_start_reconstruction_work.emit(
                self.m_reconstruction_parameters)

    @QPSLObjectBase.log_decorator()
    def click_stop_reconstruction(self):
        self.m_reconstruction_state_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_receive_reconstruction_report(self, handled: int):
        if self.m_reconstruction_progress is not None:
            self.m_reconstruction_progress.setValue(handled)
            if handled < len(self.m_reconstruction_parameters["input_files"]):
                self.m_reconstruction_progress.setLabelText(
                    self.m_reconstruction_parameters["input_files"][handled])

    @QPSLObjectBase.log_decorator()
    def on_reconstruction_stopped(self):
        self.m_reconstruction_progress.deleteLater()
        self.m_reconstruction_progress = None

    @QPSLObjectBase.log_decorator()
    def load_tiff(self, tiff_file_path: str):
        self.sig_to_get_tiff_data.emit(tiff_file_path)
        self.m_waiting = QPSLWaitingDialog(None,
                                           object_name="waiting",
                                           size=QSize(200, 200))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) - QPoint(100, 100))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_get_tiff_data(self, tiff_data: np.ndarray):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        self.m_calibration_img_data = tiff_data

    @QPSLObjectBase.log_decorator()
    def on_show_tiff_image(self):
        if self.m_calibration_img_data is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3d(
            None,
            object_name="image3d",
            window_title=self.box_get_calibration_input.get_path())
        image3d.set_image_data(image_data=self.m_calibration_img_data)
        image3d.show()
        connect_direct(image3d.sig_mouse_click, self.add_tiff_point)

    @QPSLObjectBase.log_decorator()
    def add_tiff_point(self, point: QPoint):
        self.list_calibration_points.add_item_scroll("%d, %d" %
                                                     (point.x(), point.y()))

    @QPSLObjectBase.log_decorator()
    def prepare_calibration_work(self) -> bool:
        parameters = dict()
        parameters["stateController"] = self.m_calibration_state_controller
        self.m_calibration_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def click_start_calibration(self):
        if self.prepare_calibration_work():
            self.m_calibration_state_controller.set_continue()
            self.m_calibration_progress = QPSLProgressDialog(
                None,
                object_name="progress",
                title="calibration progress",
                min=0,
                max=100)
            connect_direct(self.m_calibration_progress.canceled,
                           self.click_stop_calibration)
            self.m_calibration_progress.show()
            self.sig_start_calibration_work.emit(self.m_calibration_parameters)

    @QPSLObjectBase.log_decorator()
    def click_stop_calibration(self):
        self.m_calibration_state_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_receive_calibration_report(self, handled: int):
        if self.m_calibration_progress is not None:
            self.m_calibration_progress.setValue(handled)

    @QPSLObjectBase.log_decorator()
    def on_calibration_stopped(self):
        self.m_calibration_progress.deleteLater()
        self.m_calibration_progress = None

    @QPSLObjectBase.log_decorator()
    def load_tiff_division(self, tiff_file_path: str):
        self.sig_to_get_tiff_division_data.emit(tiff_file_path)
        self.m_waiting = QPSLWaitingDialog(None,
                                           object_name="waiting",
                                           size=QSize(200, 200))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) - QPoint(100, 100))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_get_tiff_division_data(self, tiff_data: np.ndarray):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        self.m_division_img_data = tiff_data

    @QPSLObjectBase.log_decorator()
    def on_division_show_tiff_image(self):
        if self.m_division_img_data is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3dDivision(
            None,
            object_name="image3d",
            window_title=self.box_get_division_path.get_path())
        connect_queued(image3d.sig_to_divide, self.m_worker.on_divide_image)
        connect_queued(self.m_worker.sig_division_image,
                       image3d.get_divide_result)
        connect_queued(image3d.sig_to_divide_all,
                       self.m_worker.divide_all_images)
        connect_queued(self.m_worker.sig_divide_all_over,
                       image3d.on_divide_all_over)
        image3d.set_image_data(image_data=self.m_division_img_data)
        image3d.call_divide()
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def show_division_result(self, division_res: np.ndarray):
        img1 = self.m_division_img_data
        img2 = division_res
        if img1 is None or img2 is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3dCompare(None,
                                     object_name="image3d",
                                     window_title="division result")
        image3d.set_image_data(image_data1=img1, image_data2=img2)
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_input_files(self, input_files: List[str]):
        self.list_flatten_input_files.clear()
        for file in input_files:
            file = '/'.join((self.box_get_flatten_input_path.get_path(), file))
            self.list_flatten_input_files.add_item(file)
        self.list_flatten_input_files.item(0).setSelected(True)

    @QPSLObjectBase.log_decorator()
    def prepare_flatten_work(self) -> bool:
        parameters = dict()
        parameters["thickness"] = self.spin_flatten_thickness.value()
        parameters["Zsize"] = self.spin_flatten_zsize.value()
        parameters["up_plane"] = self.box_flatten_use_up_plane.current_index(
        ) == 0
        parameters["input_path"] = self.list_flatten_input_files.selectedItems(
        )[0].text()
        parameters["save_path"] = "{0}/{1}.tif".format(
            self.box_get_flatten_save_path.get_path(),
            self.edit_flatten_name_prefix.text())
        parameters["stateController"] = self.m_flatten_state_controller
        self.m_flatten_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def click_start_flatten(self):
        if self.prepare_flatten_work():
            self.m_flatten_state_controller.set_continue()
            self.m_flatten_progress = QPSLProgressDialog(
                None,
                object_name="progress",
                title="flatten progress",
                min=0,
                max=100)
            connect_direct(self.m_flatten_progress.canceled,
                           self.click_stop_flatten)
            self.m_flatten_progress.show()
            self.sig_start_flatten_work.emit(self.m_flatten_parameters)

    @QPSLObjectBase.log_decorator()
    def click_stop_flatten(self):
        self.m_flatten_state_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_receive_flatten_report(self, handled: int):
        if self.m_flatten_progress is not None:
            self.m_flatten_progress.setValue(handled)

    @QPSLObjectBase.log_decorator()
    def on_flatten_stopped(self):
        self.m_flatten_progress.deleteLater()
        self.m_flatten_progress = None

    @QPSLObjectBase.log_decorator()
    def click_flatten_show(self):
        path1 = self.m_flatten_parameters["input_path"]
        path2 = self.m_flatten_parameters["save_path"]
        self.sig_to_get_flatten_data.emit(path1, path2)
        self.m_waiting = QPSLWaitingDialog(None,
                                           object_name="waiting",
                                           size=QSize(200, 200))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) - QPoint(100, 100))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_images(self, img1: np.ndarray, img2: np.ndarray):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        if img1 is None or img2 is None:
            return self.add_error("no valid image data")
        path1 = self.m_flatten_parameters["input_path"]
        path2 = self.m_flatten_parameters["save_path"]
        image3d = QPSLImage3dCompare(None,
                                     object_name="image3d",
                                     window_title="{0}; {1}".format(
                                         path1, path2))
        image3d.set_image_data(image_data1=img1, image_data2=img2)
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def on_add_reconstruction2_table_row(self):
        row = self.table_reconstruction2.rowCount()
        self.table_reconstruction2.setRowCount(row + 1)
        self.table_reconstruction2.setVerticalHeaderLabels(
            map(str, range(row + 1)))

    @QPSLObjectBase.log_decorator()
    def prepare_construction2_work(self) -> bool:
        parameters = dict()
        parameters["block_num"] = self.spin_reconstruction_block_num.value()
        parameters[
            "save_path"] = self.box_reconstruction_get_save_path.get_path()
        parameters["name_pre"] = self.edit_reconstruction_name_prefix.text()
        parameters["OverLapX"] = self.spin_reconstruction_overlap_x.value()
        parameters["OverLapY"] = self.spin_reconstruction_overlap_y.value()
        parameters["scaleX"] = self.spin_reconstruction_scale_x.value()
        parameters["scaleY"] = self.spin_reconstruction_scale_y.value()
        parameters["resolveX"] = self.spin_reconstruction_resolve_x.value()
        parameters["resolveY"] = self.spin_reconstruction_resolve_y.value()
        parameters["zspacing"] = self.spin_reconstruction_zspacing.value()
        parameters["input_files"] = [
            e.text()
            for e in self.list_reconstruction_input_files.selectedItems()
        ]
        parameters["stateController"] = self.m_reconstruction2_state_controller
        self.m_reconstruction2_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def click_start_reconstruction2(self):
        if self.prepare_construction2_work():
            self.m_reconstruction2_state_controller.set_continue()
            self.m_reconstruction2_progress = QPSLProgressDialog(
                None,
                object_name="progress",
                title="reconstruction2 progress",
                min=0,
                max=100)
            connect_direct(self.m_reconstruction2_progress.canceled,
                           self.click_stop_reconstruction2)
            self.m_reconstruction2_progress.show()
            self.sig_start_reconstruction2_work.emit(
                self.m_reconstruction2_parameters)

    @QPSLObjectBase.log_decorator()
    def click_stop_reconstruction2(self):
        self.m_reconstruction2_state_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_receive_reconstruction2_report(self, handled: int):
        if self.m_reconstruction2_progress is not None:
            self.m_reconstruction2_progress.setValue(handled)

    @QPSLObjectBase.log_decorator()
    def on_reconstruction2_stopped(self):
        self.m_reconstruction2_progress.deleteLater()
        self.m_reconstruction2_progress = None

    @property
    def tab_reconstruction(self) -> QPSLVerticalGroupList:
        return self.get_tab(0)

    @property
    def tab_pretreatment(self) -> QPSLVerticalGroupList:
        return self.get_tab(1)

    @property
    def tab_reconstruction2(self) -> QPSLVerticalGroupList:
        return self.get_tab(2)

    @property
    def box_reconstruction_points(self) -> QPSLGridGroupList:
        return self.tab_reconstruction.get_widget(0)

    @property
    def box_reconstruction_parameters(self) -> QPSLVerticalGroupList:
        return self.tab_reconstruction.get_widget(1)

    @property
    def box_calibration(self) -> QPSLGridGroupList:
        return self.tab_pretreatment.get_widget(0)

    @property
    def box_division(self) -> QPSLHorizontalGroupList:
        return self.tab_pretreatment.get_widget(1)

    @property
    def box_flatten(self) -> QPSLVerticalGroupList:
        return self.tab_pretreatment.get_widget(2)

    @property
    def box_reconstruction_get_sample_input(self) -> QPSLGetOpenFileBox:
        return self.box_reconstruction_points.get_widget(0)

    @property
    def list_reconstruction_sample_points(self) -> QPSLTextListWidget:
        return self.box_reconstruction_points.get_widget(1)

    @property
    def btn_reconstruction_show_sample_image(self) -> QPSLPushButton:
        return self.box_reconstruction_points.get_widget(2)

    @property
    def btn_reconstruction_delete_sample_point(self) -> QPSLPushButton:
        return self.box_reconstruction_points.get_widget(3)

    @property
    def btn_reconstruction_clear_sample_points(self) -> QPSLPushButton:
        return self.box_reconstruction_points.get_widget(4)

    @property
    def edit_reconstruction_name_prefix(self) -> QPSLTextLineEdit:
        return self.box_reconstruction_parameters.get_widget(0)

    @property
    def box_reconstruction_parameters_xy(self) -> QPSLGridGroupList:
        return self.box_reconstruction_parameters.get_widget(1)

    @property
    def spin_reconstruction_block_num(self) -> QPSLSpinBox:
        return self.box_reconstruction_parameters.get_widget(2)

    @property
    def spin_reconstruction_zspacing(self) -> QPSLSpinBox:
        return self.box_reconstruction_parameters.get_widget(3)

    @property
    def box_reconstruction_get_input_path(self) -> QPSLGetDirectoryBox:
        return self.box_reconstruction_parameters.get_widget(4)

    @property
    def box_reconstruction_get_save_path(self) -> QPSLGetDirectoryBox:
        return self.box_reconstruction_parameters.get_widget(5)

    @property
    def list_reconstruction_input_files(self) -> QPSLTextListWidget:
        return self.box_reconstruction_parameters.get_widget(6)

    @property
    def spin_reconstruction_overlap_x(self) -> QPSLSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(0)

    @property
    def spin_reconstruction_scale_x(self) -> QPSLDoubleSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(1)

    @property
    def spin_reconstruction_resolve_x(self) -> QPSLDoubleSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(2)

    @property
    def spin_reconstruction_overlap_y(self) -> QPSLSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(3)

    @property
    def spin_reconstruction_scale_y(self) -> QPSLDoubleSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(4)

    @property
    def spin_reconstruction_resolve_y(self) -> QPSLDoubleSpinBox:
        return self.box_reconstruction_parameters_xy.get_widget(5)

    @property
    def btn_reconstruction_switch(self) -> QPSLToggleButton:
        return self.box_reconstruction_parameters.get_widget(7)

    @property
    def box_get_calibration_input(self) -> QPSLGetOpenFileBox:
        return self.box_calibration.get_widget(0)

    @property
    def list_calibration_points(self) -> QPSLTextListWidget:
        return self.box_calibration.get_widget(1)

    @property
    def btn_show_calibration_image(self) -> QPSLPushButton:
        return self.box_calibration.get_widget(2)

    @property
    def btn_delete_calibration_point(self) -> QPSLPushButton:
        return self.box_calibration.get_widget(3)

    @property
    def btn_clear_calibration_points(self) -> QPSLPushButton:
        return self.box_calibration.get_widget(4)

    @property
    def btn_calibration_switch(self) -> QPSLToggleButton:
        return self.box_calibration.get_widget(5)

    @property
    def box_get_division_path(self) -> QPSLGetOpenFileBox:
        return self.box_division.get_widget(0)

    @property
    def btn_division(self) -> QPSLPushButton:
        return self.box_division.get_widget(1)

    @property
    def spin_flatten_thickness(self) -> QPSLSpinBox:
        return self.box_flatten.get_widget(0)

    @property
    def spin_flatten_zsize(self) -> QPSLDoubleSpinBox:
        return self.box_flatten.get_widget(1)

    @property
    def box_flatten_use_up_plane(self) -> QPSLHChoiceGroup:
        return self.box_flatten.get_widget(2)

    @property
    def box_get_flatten_input_path(self) -> QPSLGetDirectoryBox:
        return self.box_flatten.get_widget(3)

    @property
    def box_get_flatten_save_path(self) -> QPSLGetDirectoryBox:
        return self.box_flatten.get_widget(4)

    @property
    def edit_flatten_name_prefix(self) -> QPSLTextLineEdit:
        return self.box_flatten.get_widget(5)

    @property
    def list_flatten_input_files(self) -> QPSLTextListWidget:
        return self.box_flatten.get_widget(6)

    @property
    def box_flatten_control(self) -> QPSLHorizontalGroupList:
        return self.box_flatten.get_widget(7)

    @property
    def btn_flatten_switch(self) -> QPSLToggleButton:
        return self.box_flatten_control.get_widget(0)

    @property
    def btn_flatten_show(self) -> QPSLPushButton:
        return self.box_flatten_control.get_widget(1)

    @property
    def box_reconstruction2_get_path(self) -> QPSLGetOpenFileBox:
        return self.tab_reconstruction2.get_widget(0)

    @property
    def edit_reconstruction2_name_prefix(self) -> QPSLTextLineEdit:
        return self.tab_reconstruction2.get_widget(1)

    @property
    def edit_reconstruction2_name_suffix(self) -> QPSLTextLineEdit:
        return self.tab_reconstruction2.get_widget(2)

    @property
    def box_reconstruction2_choice(self) -> QPSLHChoiceGroup:
        return self.tab_reconstruction2.get_widget(3)

    @property
    def table_reconstruction2(self) -> QPSLTableWidget:
        return self.tab_reconstruction2.get_widget(4)

    @property
    def btn_add_table_row(self) -> QPSLPushButton:
        return self.tab_reconstruction2.get_widget(5)

    @property
    def btn_reconstruction2_switch(self) -> QPSLToggleButton:
        return self.tab_reconstruction2.get_widget(6)


MainWidget = OpticalImagePluginUI
