from PyQt5.QtWidgets import QComboBox
from .EnumManager import EnumManager

combobox_size_adjust_policy_enum_manager = EnumManager(
    names=[
        "AdjustToContents", "AdjustToContentsOnFirstShow",
        "AdjustToMinimumContentsLength",
        "AdjustToMinimumContentsLengthWithIcon"
    ],
    values=[
        QComboBox.SizeAdjustPolicy.AdjustToContents,
        QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow,
        QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLength,
        QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
    ])