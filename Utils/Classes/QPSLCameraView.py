from QPSLClass.Base import *
from QPSLClass.Base import Optional, QFrame, QSizePolicy, Qt
from ..Enum import *
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLVFrameList
from ..UIClass.QPSLLabel import QPSLLabel, QPSLTrackedScalePixmapLabel
from ..UIClass.QPSLMdiArea import QPSLMdiArea,QPSLSubWindow
from ..UIClass.QPSLSpinBox import QPSLSpinBox, QPSLDoubleSpinBox

class QPSLCameraView(QPSLMdiArea, QPSLWidgetBase):
    sig_hovered_pos = pyqtSignal(QPointF)
    sig_report_ratio = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.m_image: np.ndarray = None
        self.m_pixmap: QPixmap = None
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
        return self
    
    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_ui()

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
    def set_bit_width_and_image_format(self, bit_width:int, image_format:QImage.Format):
        pass

    def setup_ui(self):
        geo = self.geometry()
        self.subwindow_view = QPSLSubWindow()
        self.subwindow_view.setGeometry(
            0, 
            0, 
            int(geo.height() // 2), 
            int(geo.height() // 2))
        self.subwindow_view.setWindowIcon(QIcon("./resources/camera.png"))
        self.subwindow_setting = QPSLSubWindow()
        self.subwindow_setting.setGeometry(
            0 + int(geo.width()), 
            0, 
            int(geo.width() * 0.2), 
            geo.height())
        self.subwindow_setting.setWindowFlags(Qt.FramelessWindowHint)
        self.addSubWindow(self.subwindow_view)
        self.addSubWindow(self.subwindow_setting)
        self.subwindow_view.show()

        self.view_label = QPSLTrackedScalePixmapLabel().load_attr()
        self.subwindow_view.setWidget(self.view_label)

        self.frame_setting = QPSLVFrameList().load_attr(
            margins=(5,5,5,5))
        self.subwindow_setting.setWidget(self.frame_setting)
        
        self.sbox_ratio = QPSLDoubleSpinBox().load_attr(
            value=20)
        self.sbox_x0 = QPSLSpinBox().load_attr(
            prefix="x0: ", value=0)
        self.sbox_y0 = QPSLSpinBox().load_attr(
            prefix="y0: ",value=0)
        self.sbox_width = QPSLSpinBox().load_attr(
            prefix="width: ",value=2048)
        self.sbox_height = QPSLSpinBox().load_attr(
            prefix="height: ",value=2048)
        #add widgets
        self.frame_setting.add_widget(widget=QPSLLabel().load_attr(
            text="Display Options",alignment=Qt.AlignmentFlag.AlignCenter))
        self.frame_setting.add_widget(widget=QPSLLabel().load_attr(
            text="ratio:")) 
        self.frame_setting.add_widget(self.sbox_ratio)
        self.frame_setting.add_widget(widget=QPSLLabel().load_attr(
            text="")) 
        self.frame_setting.add_widget(widget=QPSLLabel().load_attr(
            text="ROI:",v_size_policy=QSizePolicy.Policy.Maximum)) 
        self.frame_setting.add_widget(self.sbox_x0)
        self.frame_setting.add_widget(self.sbox_y0)
        self.frame_setting.add_widget(self.sbox_width)
        self.frame_setting.add_widget(self.sbox_height)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.frame_setting.layout.addItem(spacer)

    def resizeEvent(self, event):
        geo = self.geometry()
        self.subwindow_view.setGeometry(
            0, 
            0, 
            int(geo.width() // 2), 
            int(geo.width() // 2))
        self.subwindow_setting.setGeometry(
            geo.width() - int(geo.width() * 0.2), 
            0, 
            int(geo.width() * 0.2), 
            geo.height())
        super().resizeEvent(event)
