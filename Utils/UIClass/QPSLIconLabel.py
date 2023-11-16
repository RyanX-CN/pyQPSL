from QPSLClass.Base import *
from Utils.UIClass.QPSLLabel import QPSLLabel


class QPSLIconLabel(QPSLLabel):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        dynamic = json.get("dynamic")
        speed = json.get("speed")
        path = json.get("path")
        if dynamic is None:
            dynamic = self.default_dynamic()
        if speed is None:
            speed = self.default_speed()
        if path is None:
            path = self.default_path()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if dynamic:
            self.set_movie_path(path=path)
            self.movie().setCacheMode(QMovie.CacheMode.CacheAll)
            self.set_speed(speed=speed)
        else:
            self.set_static_picture(path=path)

    def to_json(self):
        res: Dict = super().to_json()
        if self.m_dynamic != self.default_dynamic():
            res.update({"dynamic": self.m_dynamic})
        if self.m_dynamic and self.get_speed() != self.default_speed():
            res.update({"speed": self.get_speed()})
        if self.m_path != self.default_path():
            res.update({"path": self.m_path})
        return res

    def __init__(self):
        super().__init__()
        self.m_path = self.default_path()
        self.m_dynamic = self.default_dynamic()

    def load_attr(self,
                  dynamic: Optional[bool] = None,
                  speed: Optional[int] = None,
                  path: Optional[str] = None,
                  text: Optional[str] = None,
                  alignment: Optional[Qt.AlignmentFlag] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shape] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(text=text,
                          alignment=alignment,
                          frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if dynamic is None:
            dynamic = self.default_dynamic()
        if speed is None:
            speed = self.default_speed()
        if path is None:
            path = self.default_path()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if dynamic:
            self.set_movie_path(path=path)
            self.movie().setCacheMode(QMovie.CacheMode.CacheAll)
            self.set_speed(speed=speed)
        else:
            self.set_static_picture(path=path)
        return self

    @classmethod
    def default_dynamic(cls):
        return True

    @classmethod
    def default_speed(cls):
        return 200

    @classmethod
    def default_path(cls):
        return "{0}/Resources/loading.gif".format(QPSL_Working_Directory)

    @classmethod
    def default_h_size_policy(cls):
        return QSizePolicy.Policy.Ignored

    @classmethod
    def default_v_size_policy(cls):
        return QSizePolicy.Policy.Ignored

    def set_static_picture(self, path: str, size: Optional[QSize] = None):
        self.m_path = path
        self.m_dynamic = False
        if size is None:
            self.setPixmap(
                QPixmap(path).scaled(self.size(),
                                     Qt.AspectRatioMode.IgnoreAspectRatio))
        else:
            self.setPixmap(
                QPixmap(path).scaled(size,
                                     Qt.AspectRatioMode.IgnoreAspectRatio))

    def set_movie_path(self, path: str, size: Optional[QSize] = None):
        self.m_path = path
        self.m_dynamic = True
        self.setMovie(QMovie(self.m_path))
        if size is not None:
            self.movie().setScaledSize(size)
        else:
            self.movie().setScaledSize(self.size())

    def get_speed(self):
        return self.movie().speed()

    def set_speed(self, speed):
        self.movie().setSpeed(speed)

    def start_movie(self):
        self.movie().start()

    def stop_movie(self):
        self.movie().stop()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.m_dynamic:
            if self.movie() is not None:
                self.movie().setScaledSize(a0.size())
        else:
            self.setPixmap(
                QPixmap(self.m_path).scaled(
                    a0.size(), Qt.AspectRatioMode.IgnoreAspectRatio))
        return super().resizeEvent(a0)
