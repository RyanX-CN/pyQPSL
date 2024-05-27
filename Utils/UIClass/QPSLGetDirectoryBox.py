from QPSLClass.Base import *
from .QPSLFrameList import QPSLHFrameList
from .QPSLIconLabel import QPSLIconLabel
from .QPSLLabel import QPSLLabel
from .QPSLPushButton import QPSLPushButton


class QPSLGetDirectoryBox(QPSLHFrameList):
    sig_path_changed = pyqtSignal(str)
    sig_path_set = pyqtSignal()
    sig_path_setnull = pyqtSignal()

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        path = json.get("path")
        if path is None:
            path = self.default_path()
        self.m_path = path
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        if self.get_path() != self.default_path():
            res.update({"path": self.get_path()})
        return res

    def __init__(self):
        super().__init__()
        self.m_key_text = self.default_key_text()
        self.m_path = self.default_path()
        
    def load_attr(self,
                  key_text: Optional[str] = None,
                  path: Optional[str] = None,
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
        if key_text is None:
            key_text = self.default_key_text()
        if path is None:
            path = self.default_path()
        self.add_widget(QPSLLabel().load_attr(text=key_text))
        self.add_widget(QPSLPushButton().load_attr(text="select"))
        self.add_widget(QPSLIconLabel().load_attr())
        self.set_stretch(sizes=(3, 6, 1))
        self.m_key_text = key_text
        self.m_path = path
        self.setup_logic()
        return self

    @classmethod
    def default_key_text(cls):
        return "path:"

    @classmethod
    def default_path(cls):
        return "."

    def setup_logic(self):
        self.label_key: QPSLLabel = self.get_widget(index=0).remove_type()
        self.button_select: QPSLPushButton = self.get_widget(
            index=1).remove_type()
        self.label_icon: QPSLIconLabel = self.get_widget(index=2).remove_type()
        self.set_path(path=self.m_path)
        self.set_icon_unchecked()
        connect_direct(self.button_select.sig_clicked, self.on_select_clicked)

    def on_select_clicked(self):
        res = QFileDialog.getExistingDirectory(None, directory=self.m_path)
        self.set_path(path=res)

    def set_path(self, path: str):
        self.m_path = path
        if path:
            self.button_select.set_tooltip_enable()
            self.button_select.setToolTip(path)
            self.sig_path_changed.emit(path)
            self.sig_path_set.emit()
        else:
            self.button_select.set_tooltip_disable()
            self.sig_path_setnull.emit()

    def get_path(self):
        return self.m_path

    def set_icon_checked(self):
        self.label_icon.set_static_picture(
            path="{0}/Resources/checked.png".format(QPSL_Working_Directory))

    def set_icon_loading(self):
        self.label_icon.set_movie_path(
            path="{0}/Resources/loading.gif".format(QPSL_Working_Directory))
        self.label_icon.start_movie()

    def set_icon_unchecked(self):
        self.label_icon.set_static_picture(
            path="{0}/Resources/unchecked.png".format(QPSL_Working_Directory))