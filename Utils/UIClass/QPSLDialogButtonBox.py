from QPSLClass.Base import *
from QPSLClass.Base import Dict
from ..BaseClass import *


class QPSLDialogButtonBox(QDialogButtonBox, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        buttons = json.get("buttons")
        orientation = json.get("orientation")
        if buttons is None:
            buttons = self.default_buttons()
        if orientation is None:
            orientation = self.default_orientation()
        self.setStandardButtons(buttons)
        self.setOrientation(orientation)
        return self

    def to_json(self):
        res: Dict = super().to_json()
        if self.standardButtons() != self.default_buttons():
            res.update({"buttons": self.standardButtons()})
        if self.orientation() != self.default_orientation():
            res.update({"orientation": self.orientation()})
        return res

    def load_attr(
            self,
            buttons: Optional[Union[QDialogButtonBox.StandardButtons,
                                    QDialogButtonBox.StandardButton]] = None,
            orientation: Optional[Qt.Orientation] = None,
            h_size_policy: Optional[QSizePolicy.Policy] = None,
            v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if buttons is None:
            buttons = self.default_buttons()
        if orientation is None:
            orientation = self.default_orientation()
        self.setStandardButtons(buttons)
        self.setOrientation(orientation)
        return self

    @classmethod
    def default_buttons(
        cls
    ) -> Union[QDialogButtonBox.StandardButtons,
               QDialogButtonBox.StandardButton]:
        return QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal
