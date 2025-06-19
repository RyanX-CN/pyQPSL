from QPSLClass.Base import *
from ..BaseClass import *
from ..Enum import *


class QPSLComboBox(QComboBox, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        size_adjust_policy = json.get("size_adjust_policy")
        if size_adjust_policy is None:
            size_adjust_policy = self.default_size_adjust_policy()
        self.setSizeAdjustPolicy(size_adjust_policy)
        self.cur_text = json.get("cur_text")
        if self.cur_text is not None:
            self.setCurrentText(self.cur_text)

    def to_json(self):
        res: Dict = super().to_json()
        if self.sizeAdjustPolicy() != self.default_size_adjust_policy():
            res.update({"size_adjust_policy": self.sizeAdjustPolicy()})
        res.update({"cur_text": self.currentText()})
        return res

    def load_attr(
            self,
            size_adjust_policy: Optional[QComboBox.SizeAdjustPolicy] = None,
            h_size_policy: Optional[QSizePolicy.Policy] = None,
            v_size_policy: Optional[QSizePolicy.Policy] = None,
            cur_text: Optional[str] = None,):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if size_adjust_policy is None:
            size_adjust_policy = self.default_size_adjust_policy()
        self.setSizeAdjustPolicy(size_adjust_policy)
        if cur_text is not None:
            self.setCurrentText(cur_text)
        return self

    @classmethod
    def default_size_adjust_policy(cls):
        return QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon

    @register_single_combobox_attribute(action_name="set size adjust policy")
    def size_adjust_policy_attribute(self):

        def callback(policy: str):
            self.setSizeAdjustPolicy(
                combobox_size_adjust_policy_enum_manager.get_value(policy))

        return combobox_size_adjust_policy_enum_manager.get_name(
            self.sizeAdjustPolicy(
            )), combobox_size_adjust_policy_enum_manager.m_s2v.keys(
            ), "Set Size Adjust Policy", "Size Adjust Policy", callback, QSize(
                400, 80)
