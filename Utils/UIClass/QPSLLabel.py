from QPSLClass.Base import *
from QPSLClass.Base import Optional, QFrame, QSizePolicy, Qt
from ..Enum import *
from ..BaseClass import *


class QPSLLabel(QLabel, QPSLFrameBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("text")
        alignment = json.get("alignment")
        if text is None:
            text = self.default_text()
        if alignment is None:
            alignment = self.default_alignment()
        if text:
            self.setText(text)
        self.setAlignment(Qt.AlignmentFlag(alignment))

    def to_json(self):
        res: Dict = super().to_json()
        if self.text() != self.default_text():
            res.update({"text": self.text()})
        if self.alignment() != self.default_alignment():
            res.update({"alignment": int(self.alignment())})
        return res

    def load_attr(self,
                  text: Optional[str] = None,
                  alignment: Optional[Qt.AlignmentFlag] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shape] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if alignment is None:
            alignment = self.default_alignment()
        if text:
            self.setText(text)
        self.setAlignment(alignment)
        return self

    @classmethod
    def default_alignment(self):
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

    @classmethod
    def default_text(cls):
        return ""

    def convert_position_to_ratio(self, pos: QPoint):
        x = pos.x() / self.width()
        y = pos.y() / self.height()
        return QPointF(x, y)

    @register_multi_comboboxes_attribute(action_name="set alignment")
    def alignment_attribute(self):
        old_h_align = self.alignment() & Qt.AlignmentFlag.AlignHorizontal_Mask
        old_v_align = self.alignment() & Qt.AlignmentFlag.AlignVertical_Mask

        def callback(names: Tuple[str, str]):
            self.setAlignment(
                h_alignment_enum_manager.get_value(names[0])
                | v_alignment_enum_manager.get_value(names[1]))

        return [
            h_alignment_enum_manager.get_name(old_h_align),
            v_alignment_enum_manager.get_name(old_v_align)
        ], [
            h_alignment_enum_manager.m_s2v.keys(),
            v_alignment_enum_manager.m_s2v.keys()
        ], "Set Alignment", ["Horizontal Alignment",
                             "Vertical Alignment"], callback, QSize(400, 120)

    @register_single_text_attribute(action_name="set text")
    def text_attribute(self):
        return self.text(), "Set Text", "Text", self.setText, QSize(400, 80)


class QPSLScalePixmapLabel(QPSLLabel):
    sig_touch = pyqtSignal()
    sig_touch_of = pyqtSignal(QLabel)
    sig_touch_pixmap = pyqtSignal(QPixmap)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        aspect_ratio_mode = json.get("aspect_ratio_mode")
        if aspect_ratio_mode is None:
            aspect_ratio_mode = self.default_aspect_ratio_mode()
        self.set_aspect_ratio_mode(mode=aspect_ratio_mode)

    def to_json(self):
        res: Dict = super().to_json()
        if self.m_aspect_ratio_mode != self.default_aspect_ratio_mode():
            res.update({"aspect_ratio_mode": self.m_aspect_ratio_mode})
        return res

    def __init__(self):
        super().__init__()
        self.m_pixmap: QPixmap = None
        self.m_aspect_ratio_mode = self.default_aspect_ratio_mode()
        self.m_aspect_ratio_mode_box = SingleChoiceBox(
            name="aspect ratio mode", config_key=None)
        self.m_aspect_ratio_mode_box.set_choice_list(
            choices=aspect_ratio_mode_enum_manager.m_s2v.keys(),
            callback=self.set_aspect_ratio_mode)
        self.m_aspect_ratio_mode_box.set_choice_as(
            choice=aspect_ratio_mode_enum_manager.get_name(
                self.m_aspect_ratio_mode),
            with_callback=False)
        dict.update(self.action_dict, {
            self.m_aspect_ratio_mode_box.get_name():
            self.m_aspect_ratio_mode_box
        })

    def load_attr(self,
                  aspect_ratio_mode: Optional[Qt.AspectRatioMode] = None,
                  alignment: Optional[Qt.AlignmentFlag] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(alignment=alignment,
                          frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if aspect_ratio_mode is None:
            aspect_ratio_mode = self.default_aspect_ratio_mode()
        self.set_aspect_ratio_mode(mode=aspect_ratio_mode)
        return self

    @classmethod
    def default_alignment(self):
        return Qt.AlignmentFlag.AlignCenter

    @classmethod
    def default_aspect_ratio_mode(cls):
        return Qt.AspectRatioMode.KeepAspectRatio

    @classmethod
    def default_h_size_policy(cls):
        return QSizePolicy.Policy.Ignored

    @classmethod
    def default_v_size_policy(cls):
        return QSizePolicy.Policy.Ignored

    @pyqtSlot(object)
    def set_pixmap(self, pixmap: QPixmap):
        self.m_pixmap = pixmap
        self.setPixmap(
            pixmap.scaled(self.width(), self.height(),
                          self.m_aspect_ratio_mode))

    def set_aspect_ratio_mode(self, mode: Union[Qt.AspectRatioMode, str]):
        if isinstance(mode, str):
            mode = aspect_ratio_mode_enum_manager.get_value(mode)
        self.m_aspect_ratio_mode = mode
        self.m_aspect_ratio_mode_box.set_choice_as(
            aspect_ratio_mode_enum_manager.get_name(mode), False)
        if self.m_pixmap is not None:
            self.setPixmap(
                self.m_pixmap.scaled(self.width(), self.height(),
                                     self.m_aspect_ratio_mode))

    def resizeEvent(self, a0: QResizeEvent):
        if self.m_pixmap is not None:
            self.setPixmap(
                self.m_pixmap.scaled(self.width(), self.height(),
                                     self.m_aspect_ratio_mode))
        return super().resizeEvent(a0)

    def mousePressEvent(self, ev: QMouseEvent):
        self.sig_touch.emit()
        self.sig_touch_of.emit(self)
        if self.m_pixmap is not None:
            self.sig_touch_pixmap.emit(self.m_pixmap)
        return super().mousePressEvent(ev)


class QPSLTrackedScalePixmapLabel(QPSLScalePixmapLabel):
    sig_clicked_pos = pyqtSignal(QPointF)
    sig_hovered_pos = pyqtSignal(QPointF)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        if self.m_aspect_ratio_mode == Qt.AspectRatioMode.IgnoreAspectRatio:
            if event.button() == Qt.MouseButton.LeftButton:
                pos = self.convert_position_to_ratio(pos=event.pos())
                self.sig_clicked_pos.emit(pos)
        elif self.m_aspect_ratio_mode == Qt.AspectRatioMode.KeepAspectRatioByExpanding:
            if event.button() == Qt.MouseButton.LeftButton:
                pos = self.convert_position_to_ratio(pos=event.pos())
                self.sig_clicked_pos.emit(pos)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.m_aspect_ratio_mode == Qt.AspectRatioMode.IgnoreAspectRatio:
            pos = self.convert_position_to_ratio(pos=event.pos())
            self.sig_hovered_pos.emit(pos)
        return super().mouseMoveEvent(event)