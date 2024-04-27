from QPSLClass.Base import *
from Utils.BaseClass import *
from Utils.Enum import *
from Utils.Classes import *
from Utils.UIClass import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .OpticalImageAPI import Divisor_16


class OpticalImageDivisorWorker(QPSLWorker):
    sig_to_divide_all, sig_divide_all = pyqtSignal(dict), pyqtSignal(dict)
    sig_divide_started, sig_divide_stopped, sig_divide_report, sig_divide_result = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(int), pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_divide_all, self.sig_divide_all,
                                 self.on_divide_all)

    @QPSLObjectBase.log_decorator()
    def on_divide_all(self, parameters: Dict):
        self.sig_divide_started.emit()
        tasks: List[Union[Tuple[np.ndarray, int, int, int],
                          Tuple[np.ndarray, np.ndarray]]] = parameters["tasks"]
        save_path: str = parameters["save_path"]
        controller: SharedStateController = parameters["controller"]
        self.sig_divide_report.emit(0)
        divisor: Optional[Divisor_16] = None
        res = []
        for i, task in enumerate(tasks):
            if len(task) == 4:
                img, divide_down_ratio, binary_threshold, radius = task
                if divisor is None:
                    divisor = Divisor_16()
                    divisor.set_buffer(*task[0].shape, divide_down_ratio)
                divisor.set_graph_data(img.copy())
                divisor.set_divide_down_ratio(
                    divide_down_ratio=divide_down_ratio)
                divisor.set_binary_thresh(binary_thresh=binary_threshold)
                divisor.set_radius(radius=radius)
                divisor.run()
                mask = divisor.get_mask()
            else:
                img, mask = task
            img[np.logical_not(mask)] = 0
            res.append(img)
            self.sig_divide_report.emit(i + 1)
            if controller.is_stop():
                break
        if len(res) == len(tasks):
            res = np.stack(res, axis=0)
            tifffile.imwrite(save_path, res)
            self.sig_divide_result.emit(res)
        self.sig_divide_stopped.emit()


class OpticalImageDivisorUI(QPSLHFrameList, QPSLPluginBase):

    class ShowMode(enum.Enum):
        MASK = 0
        EDGE = 1
        PIC = 2
        EDIT = 3

    ShowModeToolTip = ("根据参数动态计算；显示二值化后的 mask", "根据参数动态计算；显示二值化后的 mask 的边缘",
                       "根据参数动态计算；显示二值化后的 mask 应用于原图的效果",
                       "根据手动编辑的 mask 静态适用；显示应用于原图的效果")

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = OpticalImageDivisorWorker()
        self.m_image: np.ndarray = None
        self.m_tasks = deque()
        self.m_mutex = QMutex()
        self.m_last_time = time.time()
        self.m_segs: List[Union[Tuple[int, int, int, int],
                                Tuple[int, np.ndarray]]] = []
        self.m_show_mode = OpticalImageDivisorUI.ShowMode.MASK
        self.m_current_mask: np.ndarray = None
        self.m_division_controller = SharedStateController()

    @QPSLObjectBase.log_decorator()
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

    @QPSLObjectBase.log_decorator()
    def get_named_widgets(self):
        self.image_3d: QPSLVFrameList = self.findChild(QPSLVFrameList,
                                                       "image_3d")
        self.label_image1: QPSLTrackedScalePixmapLabel = self.findChild(
            QPSLTrackedScalePixmapLabel, "label_image1")
        self.label_image2: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_image2")
        self.slider: QPSLSlider = self.findChild(QPSLSlider, "slider")
        self.button_axis: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_axis")
        self.spin_low: QPSLSpinBox = self.findChild(QPSLSpinBox, "spin_low")
        self.spin_high: QPSLSpinBox = self.findChild(QPSLSpinBox, "spin_high")
        self.spin_gray_ratio: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_gray_ratio")
        self.spin_divide_down_ratio: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_divide_down_ratio")
        self.spin_binary_threshold: QPSLSpinBox = self.findChild(
            QPSLSpinBox, "spin_binary_threshold")
        self.spin_radius: QPSLSpinBox = self.findChild(QPSLSpinBox,
                                                       "spin_radius")
        self.button_mode: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_mode")
        self.box_edit: QPSLHFrameList = self.findChild(QPSLHFrameList,
                                                       "box_edit")
        self.slider_pen_radius: QPSLSlider = self.findChild(
            QPSLSlider, "slider_pen_radius")
        self.checkbox_reserve: QPSLCheckBox = self.findChild(
            QPSLCheckBox, "checkbox_reserve")
        self.list_segments: QPSLListWidget = self.findChild(
            QPSLListWidget, "list_segments")
        self.button_add_segment: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_add_segment")
        self.button_remove_segments: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_remove_segments")
        self.button_reset_segments: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_reset_segments")
        self.box_get_division_save_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_division_save_path")
        self.toggle_button_division: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "toggle_button_division")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()
        connect_direct(self.label_image1.sig_hovered_pos,
                       self.show_original_gray)
        connect_direct(self.button_axis.sig_clicked, self.on_change_axis)
        connect_direct(self.slider.valueChanged, self.on_show_frame)
        connect_direct(self.spin_low.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_high.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_gray_ratio.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_divide_down_ratio.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_binary_threshold.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_radius.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.button_mode.sig_clicked, self.on_change_show_mode)
        connect_direct(self.button_add_segment.sig_clicked,
                       self.on_add_segment)
        connect_direct(self.button_remove_segments.sig_clicked,
                       self.on_remove_segments)
        connect_direct(self.button_reset_segments.sig_clicked,
                       self.on_reset_segments)
        connect_direct(self.box_get_division_save_path.sig_path_changed,
                       self.on_division_path_changed)
        connect_direct(self.toggle_button_division.sig_open,
                       self.on_click_start_division_all)
        connect_direct(self.toggle_button_division.sig_close,
                       self.on_click_stop_division)
        connect_queued(self.m_worker.sig_divide_started,
                       self.toggle_button_division.set_opened)
        connect_queued(self.m_worker.sig_divide_stopped,
                       self.on_division_stopped)
        connect_queued(self.m_worker.sig_divide_report,
                       self.on_division_reported)
        connect_queued(self.m_worker.sig_divide_result,
                       self.on_division_result)
        self.spin_divide_down_ratio.setToolTip("设为 a 时，将把原图的 a*a 方块下采样为一个像素点")
        self.spin_binary_threshold.setToolTip("对下采样之后的图像进行二值化的灰度阈值")
        self.spin_radius.setToolTip("在二值化之后，要保留的图像的膨胀半径")
        self.slider_pen_radius.setToolTip("画笔宽度")
        self.checkbox_reserve.setToolTip("是否保留画笔划过的区域")
        self.m_show_mode = OpticalImageDivisorUI.ShowMode._member_map_.get(
            self.button_mode.text().split(":")[-1],
            OpticalImageDivisorUI.ShowMode.PIC)
        self.set_show_mode(show_mode=self.m_show_mode)
        if self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDIT:
            self.on_change_show_mode()
        self.m_worker.start_thread()

    def get_axis(self):
        return self.button_axis.text()[-1]

    @classmethod
    def get_frame_by_axis(cls, axis: str, image: np.ndarray,
                          frame_index: int) -> np.ndarray:
        if axis == 'x':
            return image[:, :, frame_index]
        elif axis == 'y':
            return image[:, frame_index, :]
        else:
            return image[frame_index, :, :]

    @classmethod
    def get_frame_copy_by_axis(cls, axis: str, image: np.ndarray,
                               frame_index: int) -> np.ndarray:
        if axis == 'x':
            img = np.copy(image[:, :, frame_index])
        elif axis == 'y':
            img = np.copy(image[:, frame_index, :])
        else:
            img = np.copy(image[frame_index, :, :])
        return img

    @classmethod
    def get_shape_by_axis(cls, axis: str, image: np.ndarray):
        shape: Tuple[int, int]
        if axis == 'x':
            shape = image.shape[:2]
        elif axis == 'y':
            shape = image.shape[0], image.shape[2]
        else:
            shape = image.shape[1:]
        return shape

    @classmethod
    def get_shape_by_axis(cls, axis: str, image: np.ndarray):
        shape: Tuple[int, int]
        if axis == 'x':
            shape = image.shape[:2]
        elif axis == 'y':
            shape = image.shape[0], image.shape[2]
        else:
            shape = image.shape[1:]
        return shape

    @QPSLObjectBase.log_decorator()
    def show_original_gray(self, pos: QPointF):
        frame = self.get_frame_by_axis(axis=self.get_axis(),
                                       image=self.m_image,
                                       frame_index=self.slider.value())
        shape = frame.shape
        x = int((shape[1] - 1e-10) * pos.x())
        y = int((shape[0] - 1e-10) * pos.y())
        self.label_image1.setToolTip("{0}".format(frame[y][x]))

    @QPSLObjectBase.log_decorator()
    def set_zero_mask(self):
        if self.m_image is None:
            return
        self.on_clear_segments()
        self.m_current_mask = np.zeros_like(self.get_frame_by_axis(
            axis=self.get_axis(), image=self.m_image, frame_index=0),
                                            dtype=np.uint16)
        self.m_segs.append((0, self.m_current_mask))
        self.fill_list_with_segments(current=0)

    @QPSLObjectBase.log_decorator()
    def set_axis(self, axis: str):
        index = "zyx".index(axis)
        self.button_axis.set_text(text="axis {0}".format(axis))
        if self.m_image is not None:
            self.slider.setRange(0, self.m_image.shape[index] - 1)
        else:
            self.slider.setRange(0, 1)
        self.slider.setValue(0)
        self.on_show_current_image()
        self.set_zero_mask()

    @QPSLObjectBase.log_decorator()
    def set_axis_x(self):
        return self.set_axis('x')

    @QPSLObjectBase.log_decorator()
    def set_axis_y(self):
        return self.set_axis('y')

    @QPSLObjectBase.log_decorator()
    def set_axis_z(self):
        return self.set_axis('z')

    @QPSLObjectBase.log_decorator()
    def set_show_mode(self, show_mode: ShowMode):
        if self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDIT:
            self.label_image2.removeEventFilter(self)
        self.m_show_mode = show_mode
        self.button_mode.set_text(text="Show Mode:{0}".format(show_mode.name))
        self.button_mode.setToolTip(
            OpticalImageDivisorUI.ShowModeToolTip[show_mode.value])
        self.on_show_current_image()
        if self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDIT:
            self.label_image2.installEventFilter(self)

    @QPSLObjectBase.log_decorator()
    def on_change_axis(self):
        index = "zyx".index(self.get_axis())
        self.set_axis("zyx"[(index + 2) % 3])

    @QPSLObjectBase.log_decorator()
    def on_change_show_mode(self):
        self.set_show_mode(
            show_mode=OpticalImageDivisorUI.ShowMode._value2member_map_[
                (self.m_show_mode.value + 1) % 4])

    @QPSLObjectBase.log_decorator()
    def set_image_data(self, image_data: np.ndarray):
        self.m_image = image_data

    @QPSLObjectBase.log_decorator()
    def on_show_frame(self, frame_index: int):
        if self.m_image is None:
            return
        self.m_tasks.append((self.get_axis(), frame_index))
        self.slider.setToolTip("{0}".format(frame_index))

        def send_image():
            self.m_mutex.lock()
            if self.m_tasks:
                while self.m_tasks:
                    axis, frame_index = self.m_tasks.popleft()
                timestamp = self.m_last_time = time.time()
                self.m_mutex.unlock()
                self.handle_image(label=self.label_image1,
                                  img=self.get_frame_copy_by_axis(
                                      axis=axis,
                                      image=self.m_image,
                                      frame_index=frame_index),
                                  timestamp=timestamp)
                if timestamp < self.m_last_time: return
                self.divide_image(img=self.get_frame_copy_by_axis(
                    axis=axis, image=self.m_image, frame_index=frame_index),
                                  timestamp=timestamp)
            else:
                self.m_mutex.unlock()

        QThreadPool.globalInstance().start(send_image)

    @QPSLObjectBase.log_decorator()
    def on_show_current_image(self):
        self.on_show_frame(frame_index=self.slider.value())

    @QPSLObjectBase.log_decorator()
    def on_add_segment(self):
        index = self.slider.value()
        divide_down_ratio = self.spin_divide_down_ratio.value()
        binary_thresh = self.spin_binary_threshold.value()
        radius = self.spin_radius.value()
        bigger_index = 0
        while bigger_index < len(
                self.m_segs) and self.m_segs[bigger_index][0] < index:
            bigger_index += 1
        if bigger_index < len(
                self.m_segs) and self.m_segs[bigger_index][0] == index:
            self.m_segs.pop(bigger_index)
        if self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDIT:
            self.m_segs.insert(bigger_index, (index, self.m_current_mask))
        else:
            self.m_segs.insert(
                bigger_index,
                (index, divide_down_ratio, binary_thresh, radius))
        self.fill_list_with_segments(current=bigger_index)

    @QPSLObjectBase.log_decorator()
    def on_remove_segments(self):
        indexes = []
        for item in self.list_segments.selectedItems():
            indexes.append(self.list_segments.row(item))
        for idx in sorted(indexes, reverse=True):
            self.m_segs.pop(idx)
        self.fill_list_with_segments(current=len(self.m_segs) - 1)

    @QPSLObjectBase.log_decorator()
    def on_clear_segments(self):
        self.m_segs.clear()
        self.list_segments.clear()

    @QPSLObjectBase.log_decorator()
    def on_reset_segments(self):
        self.on_clear_segments()
        self.set_zero_mask()

    @QPSLObjectBase.log_decorator()
    def on_division_path_changed(self, save_path: str):
        self.box_get_division_save_path.set_icon_checked()

    @QPSLObjectBase.log_decorator()
    def on_click_start_division_all(self):
        if self.prepare_divide_all():
            self.m_division_progress = QPSLProgressDialog().load_attr(
                title="division progress",
                _range=(0, len(self.m_division_parameters["tasks"])))
            connect_direct(self.m_division_progress.canceled,
                           self.on_click_stop_division)
            self.m_division_progress.show()
            self.m_worker.sig_to_divide_all.emit(self.m_division_parameters)

    @QPSLObjectBase.log_decorator()
    def on_click_stop_division(self):
        self.m_division_controller.set_stop()

    @QPSLObjectBase.log_decorator()
    def on_division_reported(self, index: int):
        self.m_division_progress.setValue(index)
        if index == len(self.m_division_parameters["tasks"]):
            self.m_division_progress.setLabelText("over")

    @QPSLObjectBase.log_decorator()
    def on_division_result(self, divided: np.ndarray):
        image3d = QPSLImageCompare3d().load_attr(
            bit_width=16, image_format=QImage.Format.Format_Grayscale16)
        image3d.setWindowTitle("division result")
        image3d.set_image_data(image1_data=self.m_image, image2_data=divided)
        image3d.set_axis(self.get_axis())
        image3d.setParent(self, Qt.WindowType.Window)
        image3d.resize(900, 500)
        image3d.show()

    @QPSLObjectBase.log_decorator()
    def on_division_stopped(self):
        self.toggle_button_division.set_closed()
        QTimer.singleShot(1000, self.m_division_progress.deleteLater)

    def handle_image(self, label: QPSLScalePixmapLabel, img: np.ndarray,
                     timestamp: float):
        img = img.copy()
        gray_low = self.spin_low.value()
        gray_high = self.spin_high.value()
        gray_ratio = self.spin_gray_ratio.value()
        if gray_low > 0 and gray_high < 65535:
            m1 = img >= gray_low
            if timestamp < self.m_last_time: return
            m2 = img <= gray_high
            if timestamp < self.m_last_time: return
            need_mask = np.logical_and(m1, m2)
            if timestamp < self.m_last_time: return
            not_need_mask = np.logical_or(np.logical_not(m1),
                                          np.logical_not(m2))
            if timestamp < self.m_last_time: return
            img[not_need_mask] = 0
            if timestamp < self.m_last_time: return
            if int(gray_ratio):
                r = int(gray_ratio)
            else:
                r = 65535 // np.max(img[need_mask])
        else:
            if int(gray_ratio):
                r = int(gray_ratio)
            else:
                r = 65535 // np.max(img)
        img *= r
        if timestamp < self.m_last_time: return
        qimg = QImage(img.data, img.shape[1], img.shape[0], img.shape[1] * 2,
                      QImage.Format.Format_Grayscale16)
        if timestamp < self.m_last_time: return
        pixmap = QPixmap.fromImage(qimg)
        if timestamp < self.m_last_time: return
        self.m_mutex.lock()
        QMetaObject.invokeMethod(label, label.set_pixmap.__name__,
                                 Q_ARG(object, pixmap))
        self.m_mutex.unlock()

    def handle_mask(self, mask: np.ndarray, timestamp: float):
        mask = mask.astype(dtype=np.uint8) * 255
        qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1],
                      QImage.Format.Format_Grayscale8)
        if timestamp < self.m_last_time: return
        pixmap = QPixmap.fromImage(qimg)
        if timestamp < self.m_last_time: return
        self.m_mutex.lock()
        QMetaObject.invokeMethod(self.label_image2,
                                 self.label_image2.set_pixmap.__name__,
                                 Q_ARG(object, pixmap))
        self.m_mutex.unlock()

    def handle_edge(self, edge: np.ndarray, timestamp: float):
        edge = edge.astype(dtype=np.uint8) * 255
        qimg = QImage(edge.data, edge.shape[1], edge.shape[0], edge.shape[1],
                      QImage.Format.Format_Grayscale8)
        if timestamp < self.m_last_time: return
        pixmap = QPixmap.fromImage(qimg)
        if timestamp < self.m_last_time: return
        self.m_mutex.lock()
        QMetaObject.invokeMethod(self.label_image2,
                                 self.label_image2.set_pixmap.__name__,
                                 Q_ARG(object, pixmap))
        self.m_mutex.unlock()

    def divide_image(self, img: np.ndarray, timestamp: float):
        if self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDIT:
            img[np.logical_not(self.m_current_mask)] = 0
            if timestamp < self.m_last_time: return
            self.handle_image(label=self.label_image2,
                              img=img,
                              timestamp=timestamp)
        else:
            divide_down_ratio = self.spin_divide_down_ratio.value()
            binary_thresh = self.spin_binary_threshold.value()
            radius = self.spin_radius.value()
            divisor = Divisor_16()
            divisor.set_buffer(*img.shape, divide_down_ratio)
            if timestamp < self.m_last_time: return
            divisor.set_graph_data(img.copy())
            if timestamp < self.m_last_time: return
            divisor.set_divide_down_ratio(divide_down_ratio=divide_down_ratio)
            divisor.set_binary_thresh(binary_thresh=binary_thresh)
            divisor.set_radius(radius=radius)
            if timestamp < self.m_last_time: return
            divisor.run()
            if timestamp < self.m_last_time: return
            self.m_current_mask = divisor.get_mask()
            if self.m_show_mode == OpticalImageDivisorUI.ShowMode.MASK:
                if timestamp < self.m_last_time: return
                self.handle_mask(mask=self.m_current_mask, timestamp=timestamp)
            elif self.m_show_mode == OpticalImageDivisorUI.ShowMode.EDGE:
                edge = divisor.get_edge_by_mask(mask=self.m_current_mask)
                if timestamp < self.m_last_time: return
                self.handle_edge(edge=edge, timestamp=timestamp)
            else:
                img[np.logical_not(self.m_current_mask)] = 0
                if timestamp < self.m_last_time: return
                self.handle_image(label=self.label_image2,
                                  img=img,
                                  timestamp=timestamp)

    def fill_list_with_segments(self, current: int):
        self.list_segments.clear()
        for i in range(len(self.m_segs)):
            if len(self.m_segs[i]) == 4:
                index, divide_down_ratio, binary_thresh, radius = self.m_segs[
                    i]
                L = index
                R = self.m_segs[i + 1][0] - 1 if i + 1 < len(
                    self.m_segs) else self.slider.maximum()
                self.list_segments.addItem(
                    "index [{0} ~ {1}], divide_down_ratio = {2}, binary_thresh = {3}, radius = {4}"
                    .format(L, R, divide_down_ratio, binary_thresh, radius))
            else:
                index, mask = self.m_segs[i]
                L = index
                R = self.m_segs[i + 1][0] - 1 if i + 1 < len(
                    self.m_segs) else self.slider.maximum()
                self.list_segments.addItem(
                    "index [{0} ~ {1}], mask = {2}".format(
                        L, R, simple_str(mask)))
        self.list_segments.scrollTo(
            self.list_segments.indexFromItem(self.list_segments.item(current)))

    def prepare_divide_all(self):
        if self.m_image is None:
            return False
        if len(self.m_segs) == 0 or self.m_segs[0][0] != 0:
            return False
        parameters = dict()
        axis = self.get_axis()
        tasks = []
        for i in range(len(self.m_segs)):
            L = self.m_segs[i][0]
            R = self.m_segs[i + 1][0] - 1 if i + 1 < len(
                self.m_segs) else self.slider.maximum()
            for j in range(L, R + 1):
                tasks.append((self.get_frame_copy_by_axis(axis=axis,
                                                          image=self.m_image,
                                                          frame_index=j),
                              *self.m_segs[i][1:]))
        parameters["tasks"] = tasks
        parameters["save_path"] = self.box_get_division_save_path.get_path()
        self.m_division_controller.set_continue()
        parameters["controller"] = self.m_division_controller
        self.add_warning("prepare parameters:")
        for k, v in parameters.items():
            self.add_warning("{0}: {1}".format(simple_str(k), simple_str(v)))
        self.m_division_parameters = parameters
        return True

    def eventFilter(self, obj: QPSLLabel, ev: QMouseEvent) -> bool:
        if obj == self.label_image2 and (
                ev.type() == QEvent.Type.MouseButtonPress
                or ev.type() == QEvent.Type.MouseMove):
            h, w = self.m_current_mask.shape
            ratio = obj.convert_position_to_ratio(ev.pos())
            r, c = int((h - 1e-10) * ratio.y()), int((w - 1e-10) * ratio.x())
            pr = self.slider_pen_radius.value()
            r0, r1 = max(0, r - pr), min(h - 1, r + pr)
            c0, c1 = max(0, c - pr), min(w - 1, c + pr)
            if self.checkbox_reserve.isChecked():
                self.m_current_mask[r0:r1 + 1, c0:c1 + 1] = True
            else:
                self.m_current_mask[r0:r1 + 1, c0:c1 + 1] = False
            self.on_show_current_image()
        return super().eventFilter(obj, ev)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.to_delete()
        self.deleteLater()
        return super().closeEvent(a0)