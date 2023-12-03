from Tool import *
from .Logics.api import Reconstruction_Read_Sample_Dcimg, Reconstruction_Work
from .Logics.api import Pretreatment_Read_TIFF_img, Calibration_Work
from .Logics.api import Pretreatment_Read_TIFF_Division_img
from .Logics.api import Pretreatment_Read_Flatten_img, Flatten_Work
from .Logics.api import Reconstruction2_Work
from .OpticalImageDivisor import OpticalImageDivisorUI


class OpticalImagesWorker(QPSLWorker):
    sig_to_query_sample_dcimg_data, sig_query_sample_dcimg_data, sig_answer_sample_dcimg_data = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(np.ndarray)
    sig_to_query_reconstruction_files, sig_query_reconstruction_files, sig_answer_reconstruction_files = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(list)
    sig_to_reconstruction, sig_reconstruction = pyqtSignal(dict), pyqtSignal(
        dict)
    sig_reconstruction_started, sig_reconstruction_stopped, sig_reconstruction_report = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int)
    sig_to_query_sample_tiff_data, sig_query_sample_tiff_data, sig_answer_sample_tiff_data = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(np.ndarray)
    sig_to_calibration, sig_calibration = pyqtSignal(dict), pyqtSignal(dict)
    sig_calibration_started, sig_calibration_stopped, sig_calibration_report = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int)
    sig_to_query_division_tiff_data, sig_query_division_tiff_data, sig_answer_division_tiff_data = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(np.ndarray)
    sig_to_query_flatten_files, sig_query_flatten_files, sig_answer_flatten_files = pyqtSignal(
        str), pyqtSignal(str), pyqtSignal(list)
    sig_to_flatten, sig_flatten = pyqtSignal(dict), pyqtSignal(dict)
    sig_flatten_started, sig_flatten_stopped, sig_flatten_report = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int)
    sig_to_query_flatten_result, sig_query_flatten_result, sig_answer_flatten_result = pyqtSignal(
        str, str), pyqtSignal(str, str), pyqtSignal(np.ndarray, np.ndarray)
    
    sig_to_reconstruction2, sig_reconstruction2 = pyqtSignal(dict), pyqtSignal(
        dict)
    sig_reconstruction2_started, sig_reconstruction2_stopped, sig_reconstruction2_report = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_query_sample_dcimg_data,
                                 self.sig_query_sample_dcimg_data,
                                 self.on_load_sample_dcimg_data)
        connect_asynch_and_synch(self.sig_to_query_reconstruction_files,
                                 self.sig_query_reconstruction_files,
                                 self.on_query_reconstruction_files)
        connect_asynch_and_synch(self.sig_to_reconstruction,
                                 self.sig_reconstruction,
                                 self.on_reconstruction_work)
        connect_asynch_and_synch(self.sig_to_query_sample_tiff_data,
                                 self.sig_query_sample_tiff_data,
                                 self.on_load_sample_tiff_data)
        connect_asynch_and_synch(self.sig_to_calibration, self.sig_calibration,
                                 self.on_calibration_work)
        connect_asynch_and_synch(self.sig_to_query_division_tiff_data,
                                 self.sig_query_division_tiff_data,
                                 self.on_load_division_tiff_data)
        connect_asynch_and_synch(self.sig_to_query_flatten_files,
                                 self.sig_query_flatten_files,
                                 self.on_query_flatten_files)
        connect_asynch_and_synch(self.sig_to_flatten, self.sig_flatten,
                                 self.on_flatten_work)
        connect_asynch_and_synch(self.sig_to_query_flatten_result,
                                 self.sig_query_flatten_result,
                                 self.on_query_flatten_result)
        connect_asynch_and_synch(self.sig_to_reconstruction2,
                                 self.sig_reconstruction2,
                                 self.on_reconstruction2_work)

    @QPSLObjectBase.log_decorator()
    def on_load_sample_dcimg_data(self, file_path: str):
        if not file_path:
            self.add_error("no valid input path")
            self.sig_answer_sample_dcimg_data.emit(None)
        else:
            Reconstruction_Read_Sample_Dcimg(
                img_path=file_path,
                report_signal=self.sig_answer_sample_dcimg_data)

    @QPSLObjectBase.log_decorator()
    def on_query_reconstruction_files(self, dir_path: str):
        if not dir_path:
            self.add_error("no valid input path")
            self.sig_answer_reconstruction_files.emit(None)
        else:
            self.sig_answer_reconstruction_files.emit(
                list(listdir_file(dir_path)))

    @QPSLObjectBase.log_decorator()
    def on_reconstruction_work(self, parameters: Dict):
        Reconstruction_Work(parameters=parameters,
                            start_signal=self.sig_reconstruction_started,
                            report_signal=self.sig_reconstruction_report,
                            stop_signal=self.sig_reconstruction_stopped)

    @QPSLObjectBase.log_decorator()
    def on_load_sample_tiff_data(self, file_path: str):
        if not file_path:
            self.add_error("no valid input path")
            self.sig_answer_sample_tiff_data.emit(None)
        else:
            Pretreatment_Read_TIFF_img(
                img_path=file_path,
                report_signal=self.sig_answer_sample_tiff_data)

    @QPSLObjectBase.log_decorator()
    def on_calibration_work(self, parameters: Dict):
        Calibration_Work(parameters=parameters,
                         start_signal=self.sig_calibration_started,
                         report_signal=self.sig_calibration_report,
                         stop_signal=self.sig_calibration_stopped)

    @QPSLObjectBase.log_decorator()
    def on_load_division_tiff_data(self, file_path: str):
        if not file_path:
            self.add_error("no valid input path")
            self.sig_answer_division_tiff_data.emit(None)
        else:
            Pretreatment_Read_TIFF_Division_img(
                img_path=file_path,
                report_signal=self.sig_answer_division_tiff_data)

    @QPSLObjectBase.log_decorator()
    def on_query_flatten_files(self, dir_path: str):
        if not dir_path:
            self.add_error("no valid input path")
            self.sig_answer_flatten_files.emit(None)
        else:
            self.sig_answer_flatten_files.emit(list(listdir_file(dir_path)))

    @QPSLObjectBase.log_decorator()
    def on_flatten_work(self, parameters: Dict):
        Flatten_Work(parameters=parameters,
                     start_signal=self.sig_flatten_started,
                     report_signal=self.sig_flatten_report,
                     stop_signal=self.sig_flatten_stopped)

    @QPSLObjectBase.log_decorator()
    def on_query_flatten_result(self, input_path: str, save_path: str):
        Pretreatment_Read_Flatten_img(
            input_path=input_path,
            save_path=save_path,
            report_signal=self.sig_answer_flatten_result)

    @QPSLObjectBase.log_decorator()
    def on_reconstruction2_work(self, parameters: Dict):
        Reconstruction2_Work(parameters=parameters,
                             start_signal=self.sig_reconstruction2_started,
                             report_signal=self.sig_reconstruction2_report,
                             stop_signal=self.sig_reconstruction2_stopped)


class OpticalImagesUI(QPSLTabWidget, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()
        self.m_worker = OpticalImagesWorker()
        self.m_dcimg_data: np.ndarray = None
        self.m_reconstruction_controller = SharedStateController()
        self.m_tiff_data: np.ndarray = None
        self.m_calibration_controller = SharedStateController()
        self.m_division_tiff_data: np.ndarray = None
        self.m_division_controller = SharedStateController()
        self.m_flatten_controller = SharedStateController()
        self.m_reconstruction2_controller = SharedStateController()

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
        self.box_reconstruction_get_sample_dcimg_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_reconstruction_get_sample_dcimg_path")
        self.list_reconstruction_sample_points: QPSLListWidget = self.findChild(
            QPSLListWidget, "list_reconstruction_sample_points")
        self.button_reconstruction_show_sample_image: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reconstruction_show_sample_image")
        self.button_reconstruction_delete_points: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reconstruction_delete_points")
        self.button_reconstruction_clear_points: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reconstruction_clear_points")
        self.combo_edit_reconstruction_name_prefix: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_reconstruction_name_prefix")
        self.spin_overlap_x: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_overlap_x")
        self.spin_scale_x: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_scale_x")
        self.spin_resolve_x: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_resolve_x")
        self.spin_overlap_y: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_overlap_y")
        self.spin_scale_y: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_scale_y")
        self.spin_resolve_y: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_resolve_y")
        self.spin_block_num: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_block_num")
        self.spin_z_spacing: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_z_spacing")
        self.box_reconstruction_get_input_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_reconstruction_get_input_path")
        self.box_reconstruction_get_save_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_reconstruction_get_save_path")
        self.list_reconstruction_input_files: QPSLListWidget = self.findChild(
            QPSLListWidget, "list_reconstruction_input_files")
        self.toggle_button_reconstruction: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_reconstruction")
        self.box_calibration_get_sample_tiff_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_calibration_get_sample_tiff_path")
        self.list_calibration_sample_points: QPSLListWidget = self.findChild(
            QPSLListWidget, "list_calibration_sample_points")
        self.button_calibration_show_sample_image: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_calibration_show_sample_image")
        self.button_calibration_delete_points: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_calibration_delete_points")
        self.button_calibration_clear_points: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_calibration_clear_points")
        self.toggle_button_calibration: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_calibration")
        self.box_division_get_input_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_division_get_input_path")
        self.spin_flatten_thickness: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_flatten_thickness")
        self.spin_flatten_zsize: QPSLDoubleSpinBox = self.findChild(
            QPSLDoubleSpinBox, "spin_flatten_zsize")
        self.button_flatten_use_up_plane: QPSLRadioButton = self.findChild(
            QPSLRadioButton, "button_flatten_use_up_plane")
        self.button_flatten_not_use_up_plane: QPSLRadioButton = self.findChild(
            QPSLRadioButton, "button_flatten_not_use_up_plane")
        self.box_flatten_get_input_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_flatten_get_input_path")
        self.box_flatten_get_save_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_flatten_get_save_path")
        self.box_flattern_get_save_path: QPSLLabel = self.findChild(
            QPSLLabel, "box_flattern_get_save_path")
        self.combo_edit_flatten_name_prefix: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_flatten_name_prefix")
        self.list_flatten_input_files: QPSLListWidget = self.findChild(
            QPSLListWidget, "list_flatten_input_files")
        self.toggle_button_flatten: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_flatten")
        self.button_show_flatten_result: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_show_flatten_result")
        self.box_reconstruction2_get_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_reconstruction2_get_path")
        self.combo_box_reconstruction2_name_prefix: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_box_reconstruction2_name_prefix")
        self.combo_box_reconstruction2_name_suffix: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_box_reconstruction2_name_suffix")
        self.spin_start_read_number: QPSLSpinBox = self.findChild(QPSLSpinBox,
                                                                        "spin_start_read_number")
        self.button_first_time: QPSLRadioButton = self.findChild(
            QPSLRadioButton, "button_first_time")
        self.button_not_first_time: QPSLRadioButton = self.findChild(
            QPSLRadioButton, "button_not_first_time")
        self.combo_box_stitch_direction: QPSLComboBox =self.findChild(
            QPSLComboBox, "combo_box_stitch_direction")
        self.combo_box_reconstruction2_save_name: QPSLComboLineEdit =self.findChild(
            QPSLComboLineEdit, "combo_box_reconstruction2_save_name")
        self.table_reconstruction2: QPSLTableWidget = self.findChild(
            QPSLTableWidget, "table_reconstruction2")
        self.buttun_ascending_sort_table_reconstruction2: QPSLRadioButton = self.findChild(
            QPSLRadioButton,"button_ascending_sort_table_reconstruction2")
        self.buttun_descending_sort_table_reconstruction2: QPSLRadioButton = self.findChild(
            QPSLRadioButton,"button_descending_sort_table_reconstruction2")
        self.button_reconstruction2_add_row: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reconstruction2_add_row")
        self.toggle_button_reconstruction2: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_reconstruction2")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()

        def setup_tab1():
            # sample dcimg
            connect_direct(
                self.box_reconstruction_get_sample_dcimg_path.sig_path_changed,
                self.on_get_sample_dcimg_path)
            connect_queued(self.m_worker.sig_answer_sample_dcimg_data,
                           self.on_get_sample_dcimg_data)
            connect_direct(
                self.button_reconstruction_show_sample_image.sig_clicked,
                self.on_show_sample_dcimg)
            connect_direct(
                self.button_reconstruction_delete_points.sig_clicked,
                self.list_reconstruction_sample_points.remove_selected_items)
            connect_direct(self.button_reconstruction_clear_points.sig_clicked,
                           self.list_reconstruction_sample_points.clear)

            # overlap
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
            self.spin_overlap_x.setToolTip(OverLap_tip)
            self.spin_overlap_y.setToolTip(OverLap_tip)

            # reconstruction path
            connect_direct(
                self.box_reconstruction_get_input_path.sig_path_changed,
                self.on_get_reconstruction_input_dir)
            connect_direct(self.m_worker.sig_answer_reconstruction_files,
                           self.on_get_reconstruction_input_files)
            connect_direct(
                self.box_reconstruction_get_save_path.sig_path_changed,
                self.box_reconstruction_get_save_path.set_icon_checked)

            # reconstruction
            connect_direct(self.toggle_button_reconstruction.sig_open,
                           self.on_click_reconstruction)
            connect_direct(self.toggle_button_reconstruction.sig_close,
                           self.on_click_stop_reconstruction)
            connect_queued(self.m_worker.sig_reconstruction_started,
                           self.toggle_button_reconstruction.set_opened)
            connect_queued(self.m_worker.sig_reconstruction_report,
                           self.on_reconstruction_reported)
            connect_queued(self.m_worker.sig_reconstruction_stopped,
                           self.on_reconstruction_stopped)

        def setup_tab2():
            # sample tiff
            connect_direct(
                self.box_calibration_get_sample_tiff_path.sig_path_changed,
                self.on_get_sample_tiff_path)
            connect_queued(self.m_worker.sig_answer_sample_tiff_data,
                           self.on_get_sample_tiff_data)
            connect_direct(
                self.button_calibration_show_sample_image.sig_clicked,
                self.on_show_sample_tiff)
            connect_direct(
                self.button_calibration_delete_points.sig_clicked,
                self.list_calibration_sample_points.remove_selected_items)
            connect_direct(self.button_calibration_clear_points.sig_clicked,
                           self.list_calibration_sample_points.clear)

            #calibration
            connect_direct(self.toggle_button_calibration.sig_open,
                           self.on_click_calibration)
            connect_direct(self.toggle_button_calibration.sig_close,
                           self.on_click_stop_calibration)
            connect_queued(self.m_worker.sig_calibration_started,
                           self.toggle_button_calibration.set_opened)
            connect_queued(self.m_worker.sig_calibration_report,
                           self.on_calibration_reported)
            connect_queued(self.m_worker.sig_calibration_stopped,
                           self.on_calibration_stopped)

            # division
            connect_direct(self.box_division_get_input_path.sig_path_changed,
                           self.on_get_division_input_file)
            connect_queued(self.m_worker.sig_answer_division_tiff_data,
                           self.on_get_division_tiff_data)

            # flatten path
            connect_direct(self.box_flatten_get_input_path.sig_path_changed,
                           self.on_get_flatten_input_dir)
            connect_direct(self.m_worker.sig_answer_flatten_files,
                           self.on_get_flatten_input_files)
            connect_direct(self.box_flatten_get_save_path.sig_path_changed,
                           self.box_flatten_get_save_path.set_icon_checked)

            # flatten
            connect_direct(self.toggle_button_flatten.sig_open,
                           self.on_click_flatten)
            connect_direct(self.toggle_button_flatten.sig_close,
                           self.on_click_stop_flatten)
            connect_queued(self.m_worker.sig_flatten_started,
                           self.toggle_button_flatten.set_opened)
            connect_queued(self.m_worker.sig_flatten_report,
                           self.on_flatten_reported)
            connect_queued(self.m_worker.sig_flatten_stopped,
                           self.on_flatten_stopped)
            connect_direct(self.button_show_flatten_result.sig_clicked,
                           self.on_click_show_flatten_result)
            connect_queued(self.m_worker.sig_answer_flatten_result,
                           self.on_get_flatten_result)

        def setup_tab3():
            connect_direct(self.box_reconstruction2_get_path.sig_path_changed,
                           self.box_reconstruction2_get_path.set_icon_checked)
            # reconstruction2
            connect_direct(self.toggle_button_reconstruction2.sig_open,
                           self.on_click_reconstruction2)
            connect_direct(self.toggle_button_reconstruction2.sig_close,
                           self.on_click_stop_reconstruction2)
            connect_queued(self.m_worker.sig_reconstruction2_started,
                           self.toggle_button_reconstruction2.set_opened)
            connect_queued(self.m_worker.sig_reconstruction2_report,
                           self.on_reconstruction2_reported)
            connect_queued(self.m_worker.sig_reconstruction2_stopped,
                           self.on_reconstruction2_stopped)
            connect_direct(self.buttun_ascending_sort_table_reconstruction2.clicked,
                           lambda: self.table_reconstruction2.sortByColumn(0,Qt.SortOrder.AscendingOrder))
            connect_direct(self.buttun_descending_sort_table_reconstruction2.clicked,
                           lambda: self.table_reconstruction2.sortByColumn(0,Qt.SortOrder.DescendingOrder))
            connect_direct(self.button_reconstruction2_add_row.clicked,
                           lambda: self.table_reconstruction2.setRowCount(self.table_reconstruction2.rowCount()+1))

            self.table_reconstruction2.setHorizontalHeaderLabels(
                ("Slice Number 1", "Slice Section Number 1","Slice Number 2", "Slice Section Number 2"))
            self.table_reconstruction2.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)
            self.table_reconstruction2.verticalHeader().setVisible(False)

        setup_tab1()
        setup_tab2()
        setup_tab3()

        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_get_sample_dcimg_path(self, file_path: str):
        self.m_dcimg_data = None
        self.box_reconstruction_get_sample_dcimg_path.set_icon_loading()
        self.m_worker.sig_to_query_sample_dcimg_data.emit(file_path)

    @QPSLObjectBase.log_decorator()
    def on_get_sample_dcimg_data(self, dcimg_data: np.ndarray):
        if dcimg_data is None:
            self.box_reconstruction_get_sample_dcimg_path.set_icon_unchecked()
        else:
            self.m_dcimg_data = dcimg_data
            self.box_reconstruction_get_sample_dcimg_path.set_icon_checked()

    @QPSLObjectBase.log_decorator()
    def on_show_sample_dcimg(self):
        if self.m_dcimg_data is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3d().load_attr(
            bit_width=8, image_format=QImage.Format.Format_Grayscale8)
        image3d.setWindowTitle(
            self.box_reconstruction_get_sample_dcimg_path.get_path())
        image3d.set_image_data(image_data=self.m_dcimg_data)
        image3d.set_axis_z()
        image3d.setParent(self, Qt.WindowType.Window)
        image3d.resize(450, 500)
        connect_direct(image3d.sig_clicked_pos, self.on_add_sample_dcimg_point)
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def on_add_sample_dcimg_point(self, point: QPoint):
        self.list_reconstruction_sample_points.addItem("%d, %d" %
                                                       (point.x(), point.y()))
        self.list_reconstruction_sample_points.scrollToBottom()

    @QPSLObjectBase.log_decorator()
    def on_get_reconstruction_input_dir(self, dir_path: str):
        self.box_reconstruction_get_input_path.set_icon_loading()
        self.m_worker.sig_to_query_reconstruction_files.emit(dir_path)

    @QPSLObjectBase.log_decorator()
    def on_get_reconstruction_input_files(self, files: List[str]):
        if files is None:
            self.box_reconstruction_get_input_path.set_icon_unchecked()
        else:
            self.box_reconstruction_get_input_path.set_icon_checked()
            self.list_reconstruction_input_files.clear()
            self.list_reconstruction_input_files.addItems(files)

    @QPSLObjectBase.log_decorator()
    def on_click_reconstruction(self):
        if self.prepare_construction_work():
            self.m_reconstruction_progress = QPSLProgressDialog().load_attr(
                title="reconstruction progress",
                _range=(0,
                        len(self.m_reconstruction_parameters["input_files"])))
            connect_direct(self.m_reconstruction_progress.canceled,
                           self.on_click_stop_reconstruction)
            self.m_reconstruction_progress.setLabelText(
                self.m_reconstruction_parameters["input_files"][0])
            self.m_reconstruction_progress.show()
            self.m_worker.sig_to_reconstruction.emit(
                self.m_reconstruction_parameters)

    @QPSLObjectBase.log_decorator()
    def on_click_stop_reconstruction(self):
        self.m_reconstruction_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_reconstruction_reported(self, index: int):
        self.m_reconstruction_progress.setValue(index)
        if index < len(self.m_reconstruction_parameters["input_files"]):
            self.m_reconstruction_progress.setLabelText(
                self.m_reconstruction_parameters["input_files"][index])
        else:
            self.m_reconstruction_progress.setLabelText("over")

    @QPSLObjectBase.log_decorator()
    def on_reconstruction_stopped(self):
        self.toggle_button_reconstruction.set_closed()
        QTimer.singleShot(1000, self.m_reconstruction_progress.deleteLater)

    @QPSLObjectBase.log_decorator()
    def on_get_sample_tiff_path(self, file_path: str):
        self.m_tiff_data = None
        self.box_calibration_get_sample_tiff_path.set_icon_loading()
        self.m_worker.sig_to_query_sample_tiff_data.emit(file_path)

    @QPSLObjectBase.log_decorator()
    def on_get_sample_tiff_data(self, tiff_data: np.ndarray):
        if tiff_data is None:
            self.box_calibration_get_sample_tiff_path.set_icon_unchecked()
        else:
            self.m_tiff_data = tiff_data
            self.box_calibration_get_sample_tiff_path.set_icon_checked()

    @QPSLObjectBase.log_decorator()
    def on_show_sample_tiff(self):
        if self.m_tiff_data is None:
            return self.add_error("no valid image data")
        image3d = QPSLImage3d().load_attr(
            bit_width=8, image_format=QImage.Format.Format_Grayscale8)
        image3d.setWindowTitle(
            self.box_calibration_get_sample_tiff_path.get_path())
        image3d.set_image_data(image_data=self.m_tiff_data)
        image3d.set_axis_z()
        image3d.setParent(self, Qt.WindowType.Window)
        image3d.resize(450, 500)
        connect_direct(image3d.sig_clicked_pos, self.on_add_sample_tiff_point)
        image3d.show()


    @QPSLObjectBase.log_decorator()
    def on_add_sample_tiff_point(self, point: QPoint):
        self.list_calibration_sample_points.addItem("%d, %d" %
                                                    (point.x(), point.y()))
        self.list_calibration_sample_points.scrollToBottom()

    @QPSLObjectBase.log_decorator()
    def on_click_calibration(self):
        # if self.prepare_calibration_work():
        #     self.m_calibration_progress = QPSLProgressDialog().load_attr(
        #         title="rotation progress", _range=(0, 100))
        #     connect_direct(self.m_calibration_progress.canceled,
        #                    self.on_click_stop_calibration)
        #     self.m_calibration_progress.show()
        #     self.m_worker.sig_to_calibration.emit(
        #         self.m_calibration_parameters)
            
        res = []
        for i in range(0,self.m_tiff_data.shape[0]):
            matrix = self.m_tiff_data[i].reshape(self.m_tiff_data[i].size)[::-1]
            matrix = matrix.reshape(self.m_tiff_data[i].shape)
            matrix = matrix.transpose(1,0)[::-1]
            res.append(matrix)
        self.m_tiff_data = np.stack(res, axis= 0)
        self.on_show_sample_tiff()

    @QPSLObjectBase.log_decorator()
    def on_click_stop_calibration(self):
        self.m_calibration_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_calibration_reported(self, index: int):
        self.m_calibration_progress.setValue(index)

    @QPSLObjectBase.log_decorator()
    def on_calibration_stopped(self):
        self.toggle_button_calibration.set_closed()
        QTimer.singleShot(1000, self.m_calibration_progress.deleteLater)

    @QPSLObjectBase.log_decorator()
    def on_get_division_input_file(self, file_path: str):
        self.m_division_tiff_data = None
        self.box_division_get_input_path.set_icon_loading()
        self.m_worker.sig_to_query_division_tiff_data.emit(file_path)

    @QPSLObjectBase.log_decorator()
    def on_get_division_tiff_data(self, tiff_data: np.ndarray):
        if tiff_data is None:
            self.box_division_get_input_path.set_icon_unchecked()
        else:
            self.m_division_tiff_data = tiff_data
            self.box_division_get_input_path.set_icon_checked()
        division = OpticalImageDivisorUI().load_attr()
        division.setWindowTitle("image division")
        division.set_image_data(image_data=self.m_division_tiff_data)
        division.set_axis_z()
        division.setParent(self, Qt.WindowType.Window)
        division.resize(1000, 400)
        division.show()

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_input_dir(self, dir_path: str):
        self.box_flatten_get_input_path.set_icon_loading()
        self.m_worker.sig_to_query_flatten_files.emit(dir_path)

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_input_files(self, files: List[str]):
        if files is None:
            self.box_flatten_get_input_path.set_icon_unchecked()
        else:
            self.box_flatten_get_input_path.set_icon_checked()
            self.list_flatten_input_files.clear()
            self.list_flatten_input_files.addItems(files)

    @QPSLObjectBase.log_decorator()
    def on_click_flatten(self):
        if self.prepare_flatten_work():
            self.m_flatten_progress = QPSLProgressDialog().load_attr(
                title="flatten progress")
            connect_direct(self.m_flatten_progress.canceled,
                           self.on_click_stop_flatten)
            self.m_flatten_progress.show()
            self.m_worker.sig_to_flatten.emit(self.m_flatten_parameters)

    @QPSLObjectBase.log_decorator()
    def on_click_stop_flatten(self):
        self.m_flatten_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_flatten_reported(self, index: int):
        self.m_flatten_progress.setValue(index)

    @QPSLObjectBase.log_decorator()
    def on_flatten_stopped(self):
        self.toggle_button_flatten.set_closed()
        QTimer.singleShot(1000, self.m_flatten_progress.deleteLater)

    @QPSLObjectBase.log_decorator()
    def on_click_show_flatten_result(self):
        input_path = self.m_flatten_parameters["input_path"]
        save_path = self.m_flatten_parameters["save_path"]
        self.m_worker.sig_to_query_flatten_result.emit(input_path, save_path)

    @QPSLObjectBase.log_decorator()
    def on_get_flatten_result(self, input_image: np.ndarray,
                              save_image: np.ndarray):
        if input_image is None or save_image is None:
            return self.add_error("no valid image data")
        input_path = self.m_flatten_parameters["input_path"]
        save_path = self.m_flatten_parameters["save_path"]
        image3d = QPSLImageCompare3d().load_attr(
            bit_width=16, image_format=QImage.Format.Format_Grayscale16)
        image3d.setWindowTitle("{0}; {1}".format(input_path, save_path))
        image3d.set_image_data(image1_data=input_image, image2_data=save_image)
        image3d.set_axis_z()
        image3d.setParent(self, Qt.WindowType.Window)
        image3d.resize(900, 500)
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def on_click_reconstruction2(self):
        if self.prepare_construction2_work():
            self.m_reconstruction2_progress = QPSLProgressDialog().load_attr(
                title="reconstruction2 progress", _range=(0, 100))
            connect_direct(self.m_reconstruction2_progress.canceled,
                           self.on_click_stop_reconstruction2)
            self.m_reconstruction2_progress.show()
            self.m_worker.sig_to_reconstruction2.emit(
                self.m_reconstruction2_parameters)
            print("start stitching...")

    @QPSLObjectBase.log_decorator()
    def on_click_stop_reconstruction2(self):
        self.m_reconstruction2_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_reconstruction2_reported(self, index: int):
        self.m_reconstruction2_progress.setValue(index)

    @QPSLObjectBase.log_decorator()
    def on_reconstruction2_stopped(self):
        self.toggle_button_reconstruction2.set_closed()
        QTimer.singleShot(1000, self.m_reconstruction2_progress.deleteLater)

    @QPSLObjectBase.log_decorator()
    def prepare_construction_work(self) -> bool:
        parameters = dict()
        parameters["block_num"] = self.spin_block_num.value()
        parameters[
            "save_path"] = self.box_reconstruction_get_save_path.get_path()
        parameters[
            "name_pre"] = self.combo_edit_reconstruction_name_prefix.value_text(
            )
        parameters["OverLapX"] = self.spin_overlap_x.value()
        parameters["OverLapY"] = self.spin_overlap_y.value()
        parameters["scaleX"] = self.spin_scale_x.value()
        parameters["scaleY"] = self.spin_scale_y.value()
        parameters["resolveX"] = self.spin_resolve_x.value()
        parameters["resolveY"] = self.spin_resolve_y.value()
        parameters["zspacing"] = self.spin_z_spacing.value()
        parameters["input_files"] = [
            e.text()
            for e in self.list_reconstruction_input_files.selectedItems()
        ]
        parameters["stateController"] = self.m_reconstruction_controller
        self.m_reconstruction_controller.set_continue()
        self.m_reconstruction_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def prepare_calibration_work(self) -> bool:
        parameters = dict()
        parameters["stateController"] = self.m_calibration_controller
        self.m_calibration_controller.set_continue()
        self.m_calibration_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def prepare_flatten_work(self) -> bool:
        parameters = dict()
        parameters["thickness"] = self.spin_flatten_thickness.value()
        parameters["Zsize"] = self.spin_flatten_zsize.value()
        parameters["up_plane"] = self.button_flatten_use_up_plane.isChecked()
        parameters["input_path"] = self.list_flatten_input_files.selectedItems(
        )[0].text()
        parameters["save_path"] = "{0}/{1}.tif".format(
            self.box_flatten_get_save_path.get_path(),
            self.combo_edit_flatten_name_prefix.value_text())
        parameters["stateController"] = self.m_flatten_controller
        self.m_flatten_controller.set_continue()
        self.m_flatten_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        return True

    @QPSLObjectBase.log_decorator()
    def prepare_construction2_work(self) -> bool:
        parameters = dict()
        parameters["read_path"] = self.box_reconstruction2_get_path.get_path()
        parameters[
            "name_prefix"] = self.combo_box_reconstruction2_name_prefix.value_text(
            )
        parameters[
            "name_suffix"] = self.combo_box_reconstruction2_name_suffix.value_text(
            )
        parameters["start_read_number"] = self.spin_start_read_number.value()
        parameters["First_time"] = self.button_first_time.isChecked()
        parameters["stitch_direction"] = self.combo_box_stitch_direction.currentText()
        parameters["save_name"] = self.combo_box_reconstruction2_save_name.value_text()
        table = []
        for i in range(self.table_reconstruction2.rowCount()):
            a, b = self.table_reconstruction2.item(
                i, 0), self.table_reconstruction2.item(i, 1)
            table.append((a.text() if a is not None else None,
                          b.text() if b is not None else None))
        parameters["table"] = tuple(table)
        parameters["stateController"] = self.m_reconstruction2_controller
        self.m_reconstruction2_parameters = parameters
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v))) 
        return True


MainWidget = OpticalImagesUI