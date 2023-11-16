from QPSLClass.Base import *
from .QPSLFrameList import QPSLHFrameList
from .QPSLIconLabel import QPSLIconLabel
from .QPSLLabel import QPSLLabel, QPSLScalePixmapLabel
from .QPSLPushButton import QPSLPushButton


class QPSLGetOpenFileBox(QPSLHFrameList):
    sig_path_changed = pyqtSignal(str)
    sig_path_set = pyqtSignal()
    sig_path_setnull = pyqtSignal()

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        path = json.get("path")
        _filter = json.get("filter")
        multi_file = json.get("multi_file")
        as_save = json.get("as_save")
        if path is None:
            path = self.default_path()
        if _filter is None:
            _filter = self.default_filter()
        if multi_file is None:
            multi_file = self.default_multi_file()
        if as_save is None:
            as_save = self.default_as_save()
        self.m_path = path
        self.m_filter = _filter
        self.set_multi_file(b=multi_file)
        self.set_as_save(b=as_save)
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        if self.get_path() != self.default_path():
            res.update({"path": self.get_path()})
        if self.m_filter != self.default_filter():
            if isinstance(self.m_filter, list):
                self.m_filter = "; ".join(self.m_filter)
            res.update({"filter": self.m_filter})
        if self.m_multi_file != self.default_multi_file():
            res.update({"multi_file": self.m_multi_file})
        if self.m_as_save != self.default_as_save():
            res.update({"as_save": self.m_as_save})
        return res

    def __init__(self):
        super().__init__()
        self.m_key_text = self.default_key_text()
        self.m_path = self.default_path()
        self.m_filter = self.default_filter()
        self.m_multi_file = self.default_multi_file()
        self.m_as_save = self.default_as_save()
        self.m_multi_file_box = ToggleBox(
            "multi file",
            default_value=self.default_multi_file(),
            callback=self.set_multi_file,
            config_key=None)
        dict.update(self.action_dict,
                    {self.m_multi_file_box.get_name(): self.m_multi_file_box})
        self.m_as_save_box = ToggleBox("as save",
                                       default_value=self.default_as_save(),
                                       callback=self.set_as_save,
                                       config_key=None)
        dict.update(self.action_dict,
                    {self.m_as_save_box.get_name(): self.m_as_save_box})

    def load_attr(self,
                  key_text: Optional[str] = None,
                  path: Optional[str] = None,
                  _filter: Optional[Union[str, Tuple[str]]] = None,
                  multi_file: Optional[bool] = None,
                  as_save: Optional[bool] = None,
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
        if _filter is None:
            _filter = self.default_filter()
        if multi_file is None:
            multi_file = self.default_multi_file()
        if as_save is None:
            as_save = self.default_as_save()
        self.add_widget(QPSLLabel().load_attr(text=key_text))
        self.add_widget(QPSLPushButton().load_attr(text="select"))
        self.add_widget(QPSLIconLabel().load_attr())
        self.set_stretch(sizes=(3, 6, 1))
        self.m_key_text = key_text
        self.m_path = path
        self.m_filter = _filter
        self.set_multi_file(b=multi_file)
        self.set_as_save(b=as_save)
        self.setup_logic()
        return self

    @classmethod
    def default_key_text(cls):
        return "path:"

    @classmethod
    def default_path(cls):
        return "."

    @classmethod
    def default_filter(cls):
        return ""

    @classmethod
    def default_multi_file(cls):
        return False

    @classmethod
    def default_as_save(cls):
        return False

    def setup_logic(self):
        self.label_key: QPSLLabel = self.get_widget(index=0).remove_type()
        self.button_select: QPSLPushButton = self.get_widget(
            index=1).remove_type()
        self.label_icon: QPSLIconLabel = self.get_widget(index=2).remove_type()
        self.set_path(path=self.m_path)
        self.set_icon_unchecked()
        connect_direct(self.button_select.sig_clicked, self.on_select_clicked)

    def get_filter(self):
        _filter = []
        if isinstance(self.m_filter, str):
            x = self.m_filter
            if x:
                _filter.append(f"{x} files(*.{x})")
            else:
                _filter.append(f"all files(*)")
        else:
            for x in self.m_filter:
                if x:
                    _filter.append(f"{x} files(*.{x})")
                else:
                    _filter.append(f"all files(*)")
        return ";;".join(_filter)

    def set_multi_file(self, b: bool):
        self.m_multi_file = b
        self.m_multi_file_box.set_value(value=b, with_callback=False)

    def set_as_save(self, b: bool):
        self.m_as_save = b
        self.m_as_save_box.set_value(value=b, with_callback=False)

    def on_select_clicked(self):
        if self.m_as_save:
            res = QFileDialog.getSaveFileName(None,
                                              directory=self.m_path,
                                              filter=self.get_filter())
        elif self.m_multi_file:
            res = QFileDialog.getOpenFileNames(None,
                                               directory=self.m_path,
                                               filter=self.get_filter())
        else:
            res = QFileDialog.getOpenFileName(None,
                                              directory=self.m_path,
                                              filter=self.get_filter())
        if isinstance(res[0], str):
            self.set_path(path=res[0])
        else:
            self.set_path(path=';'.join(res[0]))

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
