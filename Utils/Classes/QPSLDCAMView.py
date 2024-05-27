from QPSLClass.Base import *
from QPSLClass.Base import Dict
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLHFrameList, QPSLVFrameList
from ..UIClass.QPSLSpinBox import QPSLSpinBox, QPSLDoubleSpinBox
from ..UIClass.QPSLLabel import QPSLLabel, QPSLTrackedScalePixmapLabel


class QPSLDCAMView(QPSLVFrameList):
    sig_hovered_pos = pyqtSignal(QPointF)
    sig_report_ratio = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.m_image: np.ndarray = None
        self.m_pixmap: QPixmap = None
        self.m_mutex = QMutex()
        self.m_tasks = deque()
        self.load_attr()
    
    def load_attr(self,
                  bit_width:Optional[int] = None,
                  image_format: Optional[QImage.Format] = None):
        super().load_attr()
        if bit_width is None:
            bit_width = self.default_bit_width()
        if image_format  is None:
            image_format = self.default_image_format()
        self.m_bit_width = bit_width
        self.m_max_color = (1 << bit_width) - 1
        self.m_byte_width = bit_width // 8
        self.m_image_format = image_format
        return self
    
    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_ui()
        self.set_stretch([10,0])
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    @classmethod
    def default_bit_width(cls):
        return 16
    
    @classmethod
    def default_image_format(cls):
        return QImage.Format.Format_Grayscale16
    
    @QPSLObjectBase.log_decorator()
    def set_bit_width_and_image_format(self):
        pass
    
    @QPSLObjectBase.log_decorator()
    def setup_ui(self):
        self.add_widget(widget=QPSLTrackedScalePixmapLabel().load_attr(
            aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        self.add_widget(widget=QPSLHFrameList().load_attr(
            spacing=5, margins=(0, 0, 0, 0)))
        self.add_widget(widget=QPSLLabel().load_attr())
        self.label_image:QPSLTrackedScalePixmapLabel = self.get_widget(0).remove_type()
        self.frame_image:QPSLHFrameList = self.get_widget(1).remove_type()
        self.label_info:QPSLLabel = self.get_widget(2).remove_type() 
        self.frame_image.add_widget(widget=QPSLLabel().load_attr(
            text="ratio:")) 
        self.frame_image.add_widget(widget=QPSLDoubleSpinBox().load_attr(
            value=20))
        self.frame_image.add_widget(widget=QPSLLabel().load_attr(
            text="ratio:")) 
        self.frame_image.add_widget(widget=QPSLDoubleSpinBox().load_attr(
            value=20))
        self.frame_image.add_widget(widget=QPSLSpinBox().load_attr(
            prefix="x0: ", value=0))
        self.frame_image.add_widget(widget=QPSLSpinBox().load_attr(
            prefix="y0: ",value=0))
        self.frame_image.add_widget(widget=QPSLSpinBox().load_attr(
            prefix="width: ",value=2048))
        self.frame_image.add_widget(widget=QPSLSpinBox().load_attr(
            prefix="height: ",value=2048))
        self.label_ratio_1:QPSLLabel = self.frame_image.get_widget(0).remove_type()
        self.label_ratio_1.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.sbox_ratio_1:QPSLDoubleSpinBox = self.frame_image.get_widget(1).remove_type()
        self.label_ratio_2:QPSLLabel = self.frame_image.get_widget(2).remove_type()
        self.label_ratio_2.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.sbox_ratio_2:QPSLDoubleSpinBox = self.frame_image.get_widget(3).remove_type()
        self.sbox_ROI_x0:QPSLSpinBox = self.frame_image.get_widget(4).remove_type()
        self.sbox_ROI_y0:QPSLSpinBox = self.frame_image.get_widget(5).remove_type()
        self.sbox_ROI_width:QPSLSpinBox = self.frame_image.get_widget(6).remove_type()
        self.sbox_ROI_height:QPSLSpinBox = self.frame_image.get_widget(7).remove_type()

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        connect_direct(self.label_image.sig_clicked_pos,
                       self.on_show_click_position)
        
    @QPSLObjectBase.log_decorator()
    def on_show_click_position(self, pos: QPointF):
        if self.m_pixmap == None:
            return
        pixmap_width = self.m_pixmap.width()
        pixmap_height = self.m_pixmap.height()
        qpoint = QPoint(int(pos.x() * (pixmap_width - 1e-10)), int(pos.y() * (pixmap_height - 1e-10)))
        # pixmap_x = int(pos.x() * (pixmap_width / self.width()))
        # pixmap_y = int(pos.y() * (pixmap_height / self.height()))
        image = self.m_pixmap.toImage()
        # image.convertTo(QImage.Format.Format_Grayscale16)
        pixel_color = QColor(image.pixel(qpoint.x(), qpoint.y()))
        # grayscale_value = pixel_color.lightness() / self.sbox_ratio_1.value()
        grayscale_value = pixel_color.lightness() * (1 << 8) / self.sbox_ratio_1.value()
        self.label_info.setText("pos:({0},{1}), {2}".format(qpoint.x(),qpoint.y(),grayscale_value))
        
        
    @QPSLObjectBase.log_decorator()
    def on_show_image(self, img: np.ndarray):
        print("a")
        qimg = QImage(img.data,img.shape[1], img.shape[0],
                      img.shape[1] * self.m_byte_width, self.m_image_format)
        print("b")
        # print(qimg.width(),qimg.height())
        pixmap = QPixmap.fromImage(qimg)
        print("c")
        # self.label_image.set_pixmap(pixmap)
        # print("d")
    
    @QPSLObjectBase.log_decorator()
    def on_show_pixmap(self,pixmap:QPixmap):
        pixmap = pixmap.copy(self.sbox_ROI_x0.value(),self.sbox_ROI_y0.value(),
                          self.sbox_ROI_width.value(),self.sbox_ROI_height.value())
        # pixmap_scaled = pixmap.scaled(pixmap.size()/4)
        # self.label_image.set_pixmap(pixmap_scaled)
        self.label_image.set_pixmap(pixmap)
        self.m_pixmap = pixmap
        
    @QPSLObjectBase.log_decorator()
    def on_show_current_frame(self):
        if self.m_image is None:
            return
        
        def send_image():
            self.m_mutex.lock()
    
        QThreadPool.globalInstance().start(send_image)