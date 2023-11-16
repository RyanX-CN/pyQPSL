from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLLineEdit(QLineEdit, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("text")
        if text is None:
            text = self.default_text()
        if text:
            self.setText(text)

    def to_json(self):
        res: Dict = super().to_json()
        if self.text() != self.default_text():
            res.update({"text": self.text()})
        return res

    def load_attr(self,
                  text: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if text:
            self.setText(text)
        return self

    @classmethod
    def default_text(cls):
        return ""
