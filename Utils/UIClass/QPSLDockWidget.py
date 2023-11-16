from QPSLClass.Base import *
from ..BaseClass import *


class QPSLDockWidget(QDockWidget, QPSLWidgetBase):
    sig_dockwidget_closed = pyqtSignal()
    sig_dockwidget_closed_of = pyqtSignal(QDockWidget)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        if "widget" in json:
            self.setWidget(QPSLObjectBase.from_json(json.get("widget")))

    def to_json(self):
        res = super().to_json()
        if self.widget is not None:
            res.update({"widget": self.widget.to_json()})
        return res

    def to_delete(self):
        if self.widget is not None:
            self.widget.to_delete()
        self.sig_dockwidget_closed.emit()
        self.sig_dockwidget_closed_of.emit(self)
        return super().to_delete()

    def hide_title_bar(self):
        if self.titleBarWidget() is None:
            self.setTitleBarWidget(QWidget())

    def show_title_bar(self):
        if self.titleBarWidget() is not None:
            self.titleBarWidget().deleteLater()

    @property
    def widget(self) -> QPSLWidgetBase:
        return super().widget()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.to_delete()
        return super().closeEvent(event)
