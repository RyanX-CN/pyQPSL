from PyQt5.QtWidgets import QSizePolicy
from .EnumManager import EnumManager

size_policy_enum_manager = EnumManager(
    names=[
        "Fixed", "Minimum", "Maximum", "Preferred", "MinimumExpanding",
        "Expanding", "Ignored"
    ],
    values=[
        QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum,
        QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred,
        QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Ignored
    ])
