from QPSLClass.Base import *
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLHFrameList, QPSLVFrameList
from ..UIClass.QPSLLabel import QPSLTrackedScalePixmapLabel
from ..UIClass.QPSLPushButton import QPSLPushButton
from ..UIClass.QPSLSpinBox import QPSLSpinBox
from ..UIClass.QPSLSlider import QPSLSlider


class QPSLImage3dBase(QPSLVFrameList):
    sig_clicked_pos = pyqtSignal(QPoint)

    def __init__(self):
        super().__init__()
        self.m_last_time: float = time.time()
        self.m_image: np.ndarray = None
        self.m_mutex = QMutex()
        self.m_tasks = deque()

    def load_attr(self,
                  bit_width: Optional[int] = None,
                  image_format: Optional[QImage.Format] = None,
                  spacing: Optional[int] = None,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(spacing=spacing,
                          margins=margins,
                          frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if bit_width is None:
            bit_width = self.default_bit_width()
        if image_format is None:
            image_format = self.default_image_format()
        self.m_bit_width = bit_width
        self.m_max_color = (1 << bit_width) - 1
        self.m_byte_width = bit_width // 8
        self.m_image_format = image_format
        self.setup_ui()
        self.setup_logic()
        return self

    @classmethod
    def default_bit_width(cls):
        return 16

    @classmethod
    def default_image_format(cls):
        return QImage.Format.Format_Grayscale16

    @classmethod
    def default_spacing(cls):
        return 5

    @QPSLObjectBase.log_decorator()
    def setup_ui(self):
        self.add_widget(widget=QPSLHFrameList().load_attr(
            spacing=10, margins=(10, 10, 10, 10)))
        self.box_images: QPSLHFrameList = self.get_widget(0).remove_type()
        self.add_widget(widget=QPSLHFrameList().load_attr(
            spacing=10, margins=(10, 0, 10, 0)))
        self.box_slider_control: QPSLHFrameList = self.get_widget(
            1).remove_type()
        self.box_slider_control.add_widget(widget=QPSLSlider().load_attr(
            orientation=Qt.Orientation.Horizontal))
        self.slider: QPSLSlider = self.box_slider_control.get_widget(
            0).remove_type()
        self.slider.set_tooltip_enable()
        self.box_slider_control.add_widget(widget=QPSLPushButton().load_attr(
            text="axis x"))
        self.button_axis: QPSLPushButton = self.box_slider_control.get_widget(
            1)
        self.box_slider_control.set_stretch(sizes=(8, 1))

        self.add_widget(widget=QPSLHFrameList().load_attr(
            spacing=5, margins=(10, 5, 10, 5)))
        self.box_settings: QPSLHFrameList = self.get_widget(2).remove_type()
        self.box_settings.add_widget(widget=QPSLSpinBox().load_attr(
            _range=(0, self.m_max_color), value=0, prefix="low: "))
        self.spin_low: QPSLSpinBox = self.box_settings.get_widget(
            0).remove_type()
        self.box_settings.add_widget(
            widget=QPSLSpinBox().load_attr(_range=(0, self.m_max_color),
                                           value=self.m_max_color,
                                           prefix="high: "))
        self.spin_high: QPSLSpinBox = self.box_settings.get_widget(
            1).remove_type()
        self.box_settings.add_widget(widget=QPSLSpinBox().load_attr(
            _range=(0, self.m_max_color), value=5, prefix="gray ratio: "))
        self.spin_gray_ratio: QPSLSpinBox = self.box_settings.get_widget(
            2).remove_type()
        self.set_stretch(sizes=(30, 3, 1))

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        connect_direct(self.button_axis.sig_clicked, self.on_change_axis)
        connect_direct(self.slider.valueChanged, self.on_show_frame)
        connect_direct(self.spin_low.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_high.sig_value_changed,
                       self.on_show_current_image)
        connect_direct(self.spin_gray_ratio.sig_value_changed,
                       self.on_show_current_image)

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
    def set_axis(self, axis: str):
        index = "zyx".index(axis)
        self.button_axis.set_text(text="axis {0}".format(axis))
        if self.m_image is not None:
            self.slider.setRange(0, self.m_image.shape[index] - 1)
        else:
            self.slider.setRange(0, 1)
        self.slider.setValue(0)
        self.on_show_current_image()

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
    def on_change_axis(self):
        index = "zyx".index(self.get_axis())
        self.set_axis("zyx"[(index + 2) % 3])

    @QPSLObjectBase.log_decorator()
    def on_show_frame(self, frame_index: int):
        pass

    @QPSLObjectBase.log_decorator()
    def on_show_current_image(self):
        self.on_show_frame(frame_index=self.slider.value())

    @QPSLObjectBase.log_decorator()
    def on_show_click_position(self, pos: QPointF):
        if self.m_image is None:
            return
        shape = self.get_shape_by_axis(axis=self.get_axis(),
                                       image=self.m_image)
        self.sig_clicked_pos.emit(
            QPoint(int((shape[1] - 1e-10) * pos.x()),
                   int((shape[0] - 1e-10) * pos.y())))

    def handle_image(self, label: QPSLTrackedScalePixmapLabel, img: np.ndarray,
                     timestamp: float, gray_low: int, gray_high: int,
                     gray_ratio: int):
        img = img.copy()
        if gray_low > 0 and gray_high < self.m_max_color:
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
                r = self.m_max_color // np.max(img[need_mask])
        else:
            if int(gray_ratio):
                r = int(gray_ratio)
            else:
                r = self.m_max_color // np.max(img)
        img *= r
        if timestamp < self.m_last_time: return
        qimg = QImage(img.data, img.shape[1], img.shape[0],
                      img.shape[1] * self.m_byte_width, self.m_image_format)
        if timestamp < self.m_last_time: return
        pixmap = QPixmap.fromImage(qimg)
        if timestamp < self.m_last_time: return
        self.m_mutex.lock()
        QMetaObject.invokeMethod(label, label.set_pixmap.__name__,
                                 Q_ARG(object, pixmap))
        self.m_mutex.unlock()

    def closeEvent(self, a0: QCloseEvent):
        self.to_delete()
        QTimer.singleShot(0, self.deleteLater)
        return super().closeEvent(a0)


class QPSLImage3d(QPSLImage3dBase):

    @QPSLObjectBase.log_decorator()
    def setup_ui(self):
        QPSLImage3dBase.setup_ui(self)
        self.box_images.add_widget(
            widget=QPSLTrackedScalePixmapLabel().load_attr(
                aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio))
        self.label_image: QPSLTrackedScalePixmapLabel = self.box_images.get_widget(
            0).remove_type()

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        QPSLImage3dBase.setup_logic(self)
        connect_direct(self.label_image.sig_clicked_pos,
                       self.on_show_click_position)

    @QPSLObjectBase.log_decorator()
    def set_image_data(self, image_data: np.ndarray):
        self.m_image = image_data

    @QPSLObjectBase.log_decorator()
    def on_show_frame(self, frame_index: int):
        if self.m_image is None:
            return
        self.m_mutex.lock()
        self.m_tasks.append(
            (self.get_axis(), frame_index, self.spin_low.value(),
             self.spin_high.value(), self.spin_gray_ratio.value()))
        self.m_mutex.unlock()
        self.slider.setToolTip("{0}".format(frame_index))

        def send_image():
            self.m_mutex.lock()
            if self.m_tasks:
                while self.m_tasks:
                    axis, frame_index, gray_low, gray_high, gray_ratio = self.m_tasks.popleft(
                    )
                timestamp = self.m_last_time = time.time()
                self.m_mutex.unlock()
                self.handle_image(label=self.label_image,
                                  img=self.get_frame_by_axis(
                                      axis=axis,
                                      image=self.m_image,
                                      frame_index=frame_index),
                                  timestamp=timestamp,
                                  gray_low=gray_low,
                                  gray_high=gray_high,
                                  gray_ratio=gray_ratio)
            else:
                self.m_mutex.unlock()

        QThreadPool.globalInstance().start(send_image)


class QPSLImageCompare3d(QPSLImage3dBase):

    def __init__(self):
        super().__init__()
        self.m_image2: np.ndarray = None

    @QPSLObjectBase.log_decorator()
    def setup_ui(self):
        QPSLImage3dBase.setup_ui(self)
        self.box_images.add_widget(
            widget=QPSLTrackedScalePixmapLabel().load_attr(
                aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio))
        self.box_images.add_widget(
            widget=QPSLTrackedScalePixmapLabel().load_attr(
                aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio))
        self.label_image1: QPSLTrackedScalePixmapLabel = self.box_images.get_widget(
            0).remove_type()
        self.label_image2: QPSLTrackedScalePixmapLabel = self.box_images.get_widget(
            1).remove_type()

    @QPSLObjectBase.log_decorator()
    def set_image_data(self, image1_data: np.ndarray, image2_data: np.ndarray):
        self.m_image = image1_data
        self.m_image2 = image2_data

    @QPSLObjectBase.log_decorator()
    def on_show_frame(self, frame_index: int):
        if self.m_image is None:
            return
        self.m_tasks.append(
            (self.get_axis(), frame_index, self.spin_low.value(),
             self.spin_high.value(), self.spin_gray_ratio.value()))
        self.slider.setToolTip("{0}".format(frame_index))

        def send_image():
            self.m_mutex.lock()
            if self.m_tasks:
                while self.m_tasks:
                    axis, frame_index, gray_low, gray_high, gray_ratio = self.m_tasks.popleft(
                    )
                timestamp = self.m_last_time = time.time()
                self.m_mutex.unlock()
                self.handle_image(label=self.label_image1,
                                  img=self.get_frame_by_axis(
                                      axis=axis,
                                      image=self.m_image,
                                      frame_index=frame_index),
                                  timestamp=timestamp,
                                  gray_low=gray_low,
                                  gray_high=gray_high,
                                  gray_ratio=gray_ratio)
                if timestamp < self.m_last_time: return
                self.handle_image(label=self.label_image2,
                                  img=self.get_frame_by_axis(
                                      axis=axis,
                                      image=self.m_image2,
                                      frame_index=frame_index),
                                  timestamp=timestamp,
                                  gray_low=gray_low,
                                  gray_high=gray_high,
                                  gray_ratio=gray_ratio)
            else:
                self.m_mutex.unlock()

        QThreadPool.globalInstance().start(send_image)
