from QPSLClass.Base import *
from QPSLClass.Base import Dict
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLHFrameList, QPSLVFrameList
from ..UIClass.QPSLLabel import QPSLTrackedScalePixmapLabel


class QPSLDCAMView(QPSLVFrameList):
    sig_hovered_pos = pyqtSignal(QPoint)

    # def to_json(self):
    #     return super().to_json()
    
    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.load_attr()
    
    def __init__(self):
        super().__init__()
        self.m_image: np.ndarray = None
        self.m_mutex = QMutex()
        self.m_tasks = deque()

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
        self.setup_ui()
        self.setup_logic()
        return self

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
        # self.add_widget(widget=QPSLVFrameList().load_attr(
        #     spacing=5, margins=(10,0,0,0)))
        # self.box_view: QPSLVFrameList = self.get_widget(0).remove_type()
        self.add_widget(widget=QPSLTrackedScalePixmapLabel().load_attr(
            aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio))
        self.label_image:QPSLTrackedScalePixmapLabel = self.get_widget(
            0).remove_type()

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        connect_direct(self.label_image.sig_hovered_pos,
                       self.on_show_hover_position)
        
    @QPSLObjectBase.log_decorator()
    def on_show_hover_position(self):
        pass
        
    @QPSLObjectBase.log_decorator()
    def on_show_image(self, img: np.ndarray):
        print("a")
        qimg = QImage(img.data,img.shape[1], img.shape[0],
                      img.shape[1] * self.m_byte_width, self.m_image_format)
        print("b")
        # print(qimg.width(),qimg.height())
        pixmap = QPixmap.fromImage(qimg)
        print(pixmap.width(),pixmap.height())
        print("c")
        # self.label_image.set_pixmap(pixmap)
        # print("d")
    
    @QPSLObjectBase.log_decorator()
    def on_show_pixmap(self,pixmap):
        self.label_image.set_pixmap(pixmap)
        
    @QPSLObjectBase.log_decorator()
    def on_show_current_frame(self):
        if self.m_image is None:
            return
        
        def send_image():
            self.m_mutex.lock()
    
        QThreadPool.globalInstance().start(send_image)