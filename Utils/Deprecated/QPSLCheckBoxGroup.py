from QPSLClass.Base import *
from Utils.BaseClass import *
from Utils.UIClass.QPSLGroupList import QPSLLinearGroupList


class QPSLCheckBoxGroup(QPSLLinearGroupList):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 orientation: Qt.Orientation,
                 texts: Iterable[str] = [],
                 title: str = ""):
        super().__init__(parent=parent,
                         object_name=object_name,
                         orientation=orientation,
                         title=title)
        self.set_options(texts=texts)

    def set_options(self, texts: List[str]):
        self.clear_widgets()
        for opt in texts:
            self.add_widget(widget=QPSLCheckBox(
                self, text=opt, object_name="opt_{0}".format(opt)))


class QPSLCheckBoxHGroup(QPSLCheckBoxGroup):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 texts: Iterable[str] = [],
                 title: str = ""):
        super().__init__(parent=parent,
                         object_name=object_name,
                         orientation=Qt.Orientation.Horizontal,
                         texts=texts,
                         title=title)


class QPSLCheckBoxVGroup(QPSLCheckBoxGroup):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 texts: Iterable[str] = [],
                 title: str = ""):
        super().__init__(parent=parent,
                         object_name=object_name,
                         orientation=Qt.Orientation.Vertical,
                         texts=texts,
                         title=title)