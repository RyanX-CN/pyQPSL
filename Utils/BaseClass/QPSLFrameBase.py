from QPSLClass.Base import *
from ..Enum import *
from .QPSLWidgetBase import QPSLWidgetBase


class QPSLFrameBase(QFrame, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        frame_shape = json.get("frame_shape")
        frame_shadow = json.get("frame_shadow")
        if frame_shape is None:
            frame_shape = self.default_frame_shape()
        if frame_shadow is None:
            frame_shadow = self.default_frame_shadow()
        QFrame.setFrameShape(self, frame_shape)
        QFrame.setFrameShadow(self, frame_shadow)

    def to_json(self):
        res: Dict = super().to_json()
        if QFrame.frameShape(self) != self.default_frame_shape():
            res.update({"frame_shape": QFrame.frameShape(self)})
        if QFrame.frameShadow(self) != self.default_frame_shadow():
            res.update({"frame_shadow": QFrame.frameShadow(self)})
        return res

    @classmethod
    def default_frame_shape(cls):
        return QFrame.Shape.NoFrame

    @classmethod
    def default_frame_shadow(cls):
        return QFrame.Shadow.Plain

    def load_attr(self,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if frame_shape is None:
            frame_shape = self.default_frame_shape()
        if frame_shadow is None:
            frame_shadow = self.default_frame_shadow()
        QFrame.setFrameShape(self, frame_shape)
        QFrame.setFrameShadow(self, frame_shadow)
        return self

    @register_multi_comboboxes_attribute(action_name="set frame")
    def frame_attribute(self):

        def callback(names: Tuple[str, str]):
            self.setFrameShape(frame_shape_enum_manager.get_value(names[0]))
            self.setFrameShadow(frame_shadow_enum_manager.get_value(names[1]))

        return [
            frame_shape_enum_manager.get_name(self.frameShape()),
            frame_shadow_enum_manager.get_name(self.frameShadow())
        ], [
            frame_shape_enum_manager.m_s2v.keys(),
            frame_shadow_enum_manager.m_s2v.keys()
        ], "Set Frame", ["Frame Shape",
                         "Frame Shadow"], callback, QSize(400, 120)
