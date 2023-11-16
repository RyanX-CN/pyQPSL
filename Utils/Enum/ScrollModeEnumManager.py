from PyQt5.QtWidgets import QAbstractItemView
from .EnumManager import EnumManager

scroll_mode_enum_manager = EnumManager(
    names=["ScrollPerItem", "ScrollPerPixel"],
    values=[
        QAbstractItemView.ScrollMode.ScrollPerItem,
        QAbstractItemView.ScrollMode.ScrollPerPixel
    ])