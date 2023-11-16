from PyQt5.QtCore import Qt
from .EnumManager import EnumManager

aspect_ratio_mode_enum_manager = EnumManager(
    names=[
        "KeepAspectRatio", "IgnoreAspectRatio", "KeepAspectRatioByExpanding"
    ],
    values=[
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding
    ])