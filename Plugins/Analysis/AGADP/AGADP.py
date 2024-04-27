from Tool import *


class AGADPWorker(QPSLWorker):
    sig_upload, sig_to_upload = pyqtSignal(dict), pyqtSignal(dict)
    sig_upload_startted, sig_upload_stopped, sig_upload_result = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(dict)
    sig_diagnosis, sig_to_diagnosis = pyqtSignal(dict), pyqtSignal(dict)
    sig_diagnosis_startted, sig_diagnosis_stopped, sig_diagnosis_result = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(dict)

    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_upload, self.sig_upload,
                                 self.upload_work)
        connect_asynch_and_synch(self.sig_to_diagnosis, self.sig_diagnosis,
                                 self.diagnosis_work)

    @QPSLObjectBase.log_decorator()
    def upload_work(self, parameters: dict):
        warnings.filterwarnings('ignore')
        if self.is_virtual:
            self.sig_upload_startted.emit()
            sleep_for(200)
            self.sig_upload_stopped.emit()
            parameters.update({"patient_name": "Zou Yanfei"})
            parameters.update(
                {"patient_birth": datetime.datetime(1963, 10, 14, 0, 0, 0)})
            parameters.update({"patient_age": 30})
            parameters.update(
                {"exam_date": datetime.datetime(2017, 2, 16, 16, 41, 5)})
            parameters.update({"exam_time": 1})
            parameters.update({"eye": "Right eye (OD)"})
            self.sig_upload_result.emit(parameters)
        else:
            from .resources.compute_20221220 import up_load_work
            up_load_work(parameters=parameters,
                         start_signal=self.sig_upload_startted,
                         report_signal=self.sig_upload_result,
                         stop_signal=self.sig_upload_stopped)

    @QPSLObjectBase.log_decorator()
    def diagnosis_work(self, parameters: dict):
        warnings.filterwarnings('ignore')
        if self.is_virtual:
            self.sig_diagnosis_startted.emit()
            sleep_for(200)
            self.sig_diagnosis_stopped.emit()
            ans = dict()
            ans.update({"diagnosis_result": "positive"})
            ans.update({"positive_probility": 98.01})
            ans.update({"negitive_probility": 1.99})
            ans.update({
                "pic1":
                "./{0}/resources/result/cam_img_cpf.jpg".format(
                    __package__.replace('.', '/')),
                "pic2":
                "./{0}/resources/result/cam_img_vf.jpg".format(
                    __package__.replace('.', '/')),
                "pic3":
                "./{0}/resources/result/cfp.jpg".format(
                    __package__.replace('.', '/')),
                "pic4":
                "./{0}/resources/result/vf.jpg".format(
                    __package__.replace('.', '/'))
            })
            self.sig_diagnosis_result.emit(ans)
        else:
            from .resources.compute_20221220 import diagnosis_work
            diagnosis_work(parameters=parameters,
                           start_signal=self.sig_diagnosis_startted,
                           report_signal=self.sig_diagnosis_result,
                           stop_signal=self.sig_diagnosis_stopped)


class AGADPUI(QPSLTabWidget, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        from .AGADPLoginBox import AGADPLoginBox
        if AGADPLoginBox().load_attr().exec() != QDialog.DialogCode.Accepted:
            self.add_critical(msg="login failed")
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()
        self.m_worker = AGADPWorker()

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
        self.box_get_input_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_get_input_path")
        self.box_get_file_dir: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_file_dir")
        self.box_get_thre_dir: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_thre_dir")
        self.box_get_model_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_model_path")
        self.box_img_save_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_img_save_path")
        self.box_get_fname: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_fname")
        self.box_get_cpf_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_cpf_path")
        self.button_upload: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_upload")
        self.combo_edit_name: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_name")
        self.combo_edit_birth: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_birth")
        self.combo_edit_age: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_age")
        self.combo_edit_eye: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_eye")
        self.combo_edit_exam_date: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_exam_date")
        self.combo_edit_exam_time: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_exam_time")
        self.button_ai_diagnosis: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_ai_diagnosis")
        self.big_label: QPSLTabWidget = self.findChild(QPSLTabWidget,
                                                       "big_label")
        self.scroll_images: QPSLHScrollList = self.findChild(
            QPSLHScrollList, "scroll_images")
        self.combo_edit_postive: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_postive")
        self.combo_edit_negative: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_negative")
        self.combo_edit_diagnosis_result: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_diagnosis_result")
        self.box_compare_1: QPSLHFrameList = self.findChild(
            QPSLHFrameList, "box_compare_1")
        self.label_compare1_1: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_compare1_1")
        self.label_compare1_2: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_compare1_2")
        self.box_compare_2: QPSLHFrameList = self.findChild(
            QPSLHFrameList, "box_compare_2")
        self.label_compare2_1: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_compare2_1")
        self.label_compare2_2: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_compare2_2")

    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()
        self.combo_edit_exam_date.set_key_text(
            self.combo_edit_exam_date.key_text().replace('.', '\n'))
        self.combo_edit_exam_time.set_key_text(
            self.combo_edit_exam_time.key_text().replace('.', '\n'))
        self.combo_edit_postive.set_key_text(
            self.combo_edit_postive.key_text().replace('.', '\n'))
        self.combo_edit_negative.set_key_text(
            self.combo_edit_negative.key_text().replace('.', '\n'))
        self.combo_edit_diagnosis_result.set_key_text(
            self.combo_edit_diagnosis_result.key_text().replace('.', '\n'))

        # path
        connect_direct(self.box_get_input_path.sig_path_changed,
                       self.box_get_input_path.set_icon_checked)
        connect_direct(self.box_get_file_dir.sig_path_changed,
                       self.box_get_file_dir.set_icon_checked)
        connect_direct(self.box_get_thre_dir.sig_path_changed,
                       self.box_get_thre_dir.set_icon_checked)
        connect_direct(self.box_get_model_path.sig_path_changed,
                       self.box_get_model_path.set_icon_checked)
        connect_direct(self.box_img_save_path.sig_path_changed,
                       self.box_img_save_path.set_icon_checked)
        connect_direct(self.box_get_fname.sig_path_changed,
                       self.box_get_fname.set_icon_checked)
        connect_direct(self.box_get_cpf_path.sig_path_changed,
                       self.box_get_cpf_path.set_icon_checked)

        # upload
        connect_direct(self.button_upload.sig_clicked,
                       self.on_click_upload_data)
        connect_queued(self.m_worker.sig_upload_startted,
                       self.on_upload_started)
        connect_queued(self.m_worker.sig_upload_stopped,
                       self.on_upload_stopped)
        connect_queued(self.m_worker.sig_upload_result,
                       self.on_get_upload_answer)

        # diagnosis
        connect_direct(self.button_ai_diagnosis.sig_clicked,
                       self.on_click_diagnosis)
        connect_queued(self.m_worker.sig_diagnosis_startted,
                       self.on_diagnosis_started)
        connect_queued(self.m_worker.sig_diagnosis_stopped,
                       self.on_diagnosis_stopped)
        connect_queued(self.m_worker.sig_diagnosis_result,
                       self.on_get_diagnosis_result)

        self.setCurrentIndex(1)
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def on_click_upload_data(self):
        parameters = self.get_paramaters()
        self.m_worker.sig_to_upload.emit(parameters)

    @QPSLObjectBase.log_decorator()
    def on_upload_started(self):
        self.setEnabled(False)
        self.scroll_images.clear_widgets()
        self.big_label.clear_widgets()
        self.common_show = QPSLScalePixmapLabel().load_attr()
        self.big_label.add_tab(tab=self.common_show, title="")
        self.m_waiting = QPSLIconDialog().load_attr(
            path="{0}/Resources/loading.gif".format(QPSL_Working_Directory))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) -
            QPoint(self.m_waiting.width() // 2,
                   self.m_waiting.height() // 2))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_upload_stopped(self):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        self.setEnabled(True)

    @QPSLObjectBase.log_decorator()
    def on_get_upload_answer(self, upload_answer: dict):
        self.m_upload_answer = upload_answer
        self.combo_edit_name.set_value_text(upload_answer["patient_name"])
        self.combo_edit_birth.set_value_text(
            datetime.datetime.strptime(
                str(upload_answer["patient_birth"]),
                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"))
        self.combo_edit_age.set_value_text(str(upload_answer["patient_age"]))
        self.combo_edit_exam_date.set_value_text(
            datetime.datetime.strptime(
                str(upload_answer["exam_date"]),
                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"))
        self.combo_edit_exam_time.set_value_text(
            datetime.datetime.strptime(
                str(upload_answer["exam_date"]),
                "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S"))
        self.combo_edit_eye.set_value_text(str(upload_answer["eye"]))
        label, small_label = self.add_big_cpf_image()
        pdf, small_pdf = self.add_big_pdf()
        self.big_label.setCurrentWidget(label)
        self.setCurrentIndex(2)

    @QPSLObjectBase.log_decorator()
    def on_click_diagnosis(self):
        parameters = self.m_upload_answer
        self.m_worker.sig_to_diagnosis.emit(parameters)

    @QPSLObjectBase.log_decorator()
    def on_diagnosis_started(self):
        self.setEnabled(False)
        self.m_waiting = QPSLIconDialog().load_attr(
            path="{0}/Resources/waiting.gif".format(QPSL_Working_Directory))
        self.m_waiting.move(
            self.mapToGlobal(self.rect().center()) -
            QPoint(self.m_waiting.width() // 2,
                   self.m_waiting.height() // 2))
        self.m_waiting.exec()

    @QPSLObjectBase.log_decorator()
    def on_diagnosis_stopped(self):
        self.m_waiting.accept()
        self.m_waiting.deleteLater()
        del self.m_waiting
        self.setEnabled(True)

    @QPSLObjectBase.log_decorator()
    def on_get_diagnosis_result(self, diagnosis_answer: dict):
        self.combo_edit_diagnosis_result.set_value_text(
            diagnosis_answer["diagnosis_result"])
        self.combo_edit_postive.set_value_text(
            str(diagnosis_answer["positive_probility"]) + "%")
        self.combo_edit_negative.set_value_text(
            str(diagnosis_answer["negitive_probility"]) + "%")

        cam_img_cpf = QPixmap(diagnosis_answer["pic1"])
        cam_img_vf = QPixmap(diagnosis_answer["pic2"])
        cpf = QPixmap(diagnosis_answer["pic3"])
        vf = QPixmap(diagnosis_answer["pic4"])
        self.label_compare1_1.set_pixmap(cam_img_cpf)
        self.label_compare1_2.set_pixmap(cpf)
        self.label_compare2_1.set_pixmap(cam_img_vf)
        self.label_compare2_2.set_pixmap(vf)

        @weakref_local_function(self)
        def callback1_1(self: AGADPUI):
            self.common_show.set_pixmap(pixmap=self.label_compare1_1.m_pixmap)
            self.big_label.setCurrentWidget(self.common_show)

        @weakref_local_function(self)
        def callback1_2(self: AGADPUI):
            self.common_show.set_pixmap(pixmap=self.label_compare1_2.m_pixmap)
            self.big_label.setCurrentWidget(self.common_show)

        @weakref_local_function(self)
        def callback2_1(self: AGADPUI):
            self.common_show.set_pixmap(pixmap=self.label_compare2_1.m_pixmap)
            self.big_label.setCurrentWidget(self.common_show)

        @weakref_local_function(self)
        def callback2_2(self: AGADPUI):
            self.common_show.set_pixmap(pixmap=self.label_compare2_2.m_pixmap)
            self.big_label.setCurrentWidget(self.common_show)

        connect_direct(self.label_compare1_1.sig_touch, callback1_1)
        connect_direct(self.label_compare1_2.sig_touch, callback1_2)
        connect_direct(self.label_compare2_1.sig_touch, callback2_1)
        connect_direct(self.label_compare2_2.sig_touch, callback2_2)

    @QPSLObjectBase.log_decorator()
    def get_paramaters(self):
        parameters = dict()
        input_path = "./" + os.path.relpath(self.box_get_input_path.get_path())
        file_dir = "./" + os.path.relpath(self.box_get_file_dir.get_path())
        thre_dir = "./" + os.path.relpath(self.box_get_thre_dir.get_path())
        model_path = "./" + os.path.relpath(self.box_get_model_path.get_path())
        model_path = model_path[:model_path.rfind('.')]
        img_save_path = "./" + os.path.relpath(
            self.box_img_save_path.get_path())
        fname = get_pure_filename(self.box_get_fname.get_path())
        cpf_path = "./" + os.path.relpath(self.box_get_cpf_path.get_path())
        parameters["input_path"] = input_path
        parameters["fname"] = fname
        parameters["file_dir"] = file_dir
        parameters["thre_dir"] = thre_dir
        parameters["cpf_path"] = cpf_path
        parameters["model_path"] = model_path
        parameters["img_save_path"] = img_save_path
        return parameters

    @QPSLObjectBase.log_decorator()
    def add_image(self, pixmap: QPixmap):
        label = QPSLScalePixmapLabel().load_attr(
            h_size_policy=QSizePolicy.Policy.Ignored,
            v_size_policy=QSizePolicy.Policy.Ignored)
        label.set_pixmap(pixmap=pixmap)
        self.big_label.add_tab(tab=label, title="")
        small_label = QPSLScalePixmapLabel().load_attr()
        small_label.set_pixmap(pixmap=pixmap)
        small_label.setFrameShape(QFrame.Shape.StyledPanel)
        w, h = int(100 * pixmap.width() / pixmap.height()), 100
        small_label.setFixedSize(w, h)
        self.scroll_images.add_widget(widget=small_label, ratio=1)

        def callback():
            self.big_label.setCurrentWidget(label)

        connect_direct(small_label.sig_touch, callback)
        return label, small_label

    @QPSLObjectBase.log_decorator()
    def add_big_cpf_image(self):
        return self.add_image(pixmap=QPixmap(self.box_get_cpf_path.get_path()))

    @QPSLObjectBase.log_decorator()
    def add_big_pdf(self):
        pixmap = convert_pdf_page_to_image(
            pdf_path=self.box_get_fname.get_path(), page=0, zoom=4)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("#000000"), 20))
        painter.drawRect(10, 10, pixmap.width() - 20, pixmap.height() - 20)
        return self.add_image(pixmap=pixmap)


MainWidget = AGADPUI
