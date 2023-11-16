from QPSLClass.Base import *
from ..BaseClass import *


class QPSLGroupBox(QGroupBox, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        title = json.get("title")
        if title is None:
            title = self.default_title()
        if title:
            self.setTitle(title)

    def to_json(self):
        res = super().to_json()
        if self.title() != self.default_title():
            res.update({"title": self.title()})
        return res

    def load_attr(self,
                  title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if title is None:
            title = self.default_title()
        if title:
            self.setTitle(title)
        return self

    @classmethod
    def default_title(cls):
        return ""

    @attribute_factory_decorator(cls_name="QPSLGroupBox",
                                 name="title...",
                                 window_title="Set Title")
    def title_edit_factory(self):
        box = QWidget()
        layout = QGridLayout()
        box.setLayout(layout)
        old_title = self.title()

        label = QLabel("title:")
        layout.addWidget(label, 0, 0)
        edit = QLineEdit(old_title)
        layout.addWidget(edit, 0, 1)

        def callback(title):
            self.setTitle(title)

        def reject_callback():
            self.setTitle(old_title)

        connect_direct(edit.textEdited, callback)
        return box, reject_callback