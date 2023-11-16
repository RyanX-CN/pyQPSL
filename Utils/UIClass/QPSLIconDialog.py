from QPSLClass.Base import *
from Utils.UIClass.QPSLLabel import QPSLLabel
from Utils.UIClass.QPSLDialog import QPSLDialog


class QPSLIconDialog(QPSLDialog):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        size = json.get("size")
        speed = json.get("speed")
        path = json.get("path")
        if size is None:
            size = self.default_size()
        if speed is None:
            speed = self.default_speed()
        if path is None:
            path = self.default_path()
        self.resize(size)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QGridLayout()
        self.setLayout(layout)
        self.label = QPSLLabel().load_attr()
        layout.addWidget(self.label)
        self.set_path(path=path)
        self.label.movie().setScaledSize(size)
        self.label.movie().setCacheMode(QMovie.CacheMode.CacheAll)
        self.set_speed(speed=speed)
        self.start_movie()

    def to_json(self):
        res: Dict = super().to_json()
        if self.size() != self.default_size():
            res.update({"size": self.size()})
        if self.get_speed() != self.default_speed():
            res.update({"speed": self.get_speed()})
        if self.m_path != self.default_path():
            res.update({"path": self.m_path})
        return res

    def __init__(self):
        super().__init__()
        self.m_path = self.default_path()

    def load_attr(self,
                  size: Optional[QSize] = None,
                  speed: Optional[int] = None,
                  path: Optional[str] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(window_title=window_title,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if size is None:
            size = self.default_size()
        if speed is None:
            speed = self.default_speed()
        if path is None:
            path = self.default_path()
        self.resize(size)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QGridLayout()
        self.setLayout(layout)
        self.label = QPSLLabel().load_attr()
        layout.addWidget(self.label)
        self.set_path(path=path)
        self.label.movie().setScaledSize(size)
        self.label.movie().setCacheMode(QMovie.CacheMode.CacheAll)
        self.set_speed(speed=speed)
        self.start_movie()
        return self

    @classmethod
    def default_size(cls):
        return QSize(200, 200)

    @classmethod
    def default_speed(cls):
        return 200

    @classmethod
    def default_path(cls):
        return "{0}/Resources/loading.gif".format(QPSL_Working_Directory)

    def set_path(self, path: str):
        self.m_path = path
        self.label.setMovie(QMovie(self.m_path))

    def get_speed(self):
        return self.label.movie().speed()

    def set_speed(self, speed):
        self.label.movie().setSpeed(speed)

    def start_movie(self):
        self.label.movie().start()

    def stop_movie(self):
        self.label.movie().stop()