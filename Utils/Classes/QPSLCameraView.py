from QPSLClass.Base import *
from QPSLClass.Base import Optional, QFrame, QSizePolicy, Qt
from ..Enum import *
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLVFrameList
from ..UIClass.QPSLLabel import QPSLLabel, QPSLTrackedScalePixmapLabel
from ..UIClass.QPSLMdiArea import QPSLMdiArea,QPSLSubWindow
from ..UIClass.QPSLSpinBox import QPSLSpinBox, QPSLDoubleSpinBox

import napari
import imagej

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
        self.m_view_mode = "none" # "napari" or "imagej" or "none"
        return self
    
    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        # self.setup_ui()

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

    def startup_napari(self):
        self.napari = napari.Viewer()
        self.subwindow_view = QPSLSubWindow()
        # self.subwindow_view.setWindowIcon(QIcon("./resources/camera.png"))
        self.addSubWindow(self.subwindow_view)
        self.subwindow_view.setWidget(self.napari.window._qt_window)

        layer_control = self.napari.window._qt_viewer.dockLayerControls
        layer_list = self.napari.window._qt_viewer.dockLayerList
        self.napari.window.add_dock_widget(layer_control, area="right")
        self.napari.window.add_dock_widget(layer_list, area="right")
        
        self.subwindow_view.show()

    def startup_imagej(self):
        self.ij = imagej.init()
        self.ij.ui().showUI()

    # def resizeEvent(self, event):
    #     geo = self.geometry()
    #     self.subwindow_view.setGeometry(
    #         0, 
    #         0, 
    #         int(geo.width()), 
    #         int(geo.width()))
    # #     self.subwindow_setting.setGeometry(
    # #         geo.width() - int(geo.width() * 0.2), 
    # #         0, 
    # #         int(geo.width() * 0.2), 
    #         # geo.height())
    #     super().resizeEvent(event)
