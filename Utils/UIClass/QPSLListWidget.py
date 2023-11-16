from PyQt5.QtWidgets import QWidget
from QPSLClass.Base import *
from QPSLClass.Base import Dict, Optional, QAbstractItemView, QFrame, QSizePolicy
from ..BaseClass import *
from ..Enum import *


class QPSLListWidget(QListWidget, QPSLFrameBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        selection_mode = json.get("selection_mode")
        vertical_scroll_mode = json.get("vertical_scroll_mode")
        if selection_mode is None:
            selection_mode = self.default_selection_mode()
        if vertical_scroll_mode is None:
            vertical_scroll_mode = self.default_vertical_scroll_mode()
        self.set_selection_mode(mode=selection_mode)
        self.set_scroll_mode(mode=vertical_scroll_mode)

    def to_json(self):
        res: Dict = super().to_json()
        if self.selectionMode() != self.default_selection_mode():
            res.update({"selection_mode": self.selectionMode()})
        if self.verticalScrollMode() != self.default_vertical_scroll_mode():
            res.update({"vertical_scroll_mode": self.verticalScrollMode()})
        return res

    def __init__(self):
        super().__init__()
        self.m_selection_mode_box = SingleChoiceBox(name="selection mode",
                                                    config_key=None)
        self.m_selection_mode_box.set_choice_list(
            choices=selection_mode_enum_manager.m_s2v.keys(),
            callback=self.set_selection_mode)
        dict.update(
            self.action_dict,
            {self.m_selection_mode_box.get_name(): self.m_selection_mode_box})

        self.m_scroll_mode_box = SingleChoiceBox(name="scroll mode",
                                                 config_key=None)
        self.m_scroll_mode_box.set_choice_list(
            choices=scroll_mode_enum_manager.m_s2v.keys(),
            callback=self.set_scroll_mode)
        dict.update(
            self.action_dict,
            {self.m_scroll_mode_box.get_name(): self.m_scroll_mode_box})

    def load_attr(
            self,
            selection_mode: Optional[QAbstractItemView.SelectionMode] = None,
            vertical_scroll_mode: Optional[
                QAbstractItemView.ScrollMode] = None,
            frame_shape: Optional[QFrame.Shape] = None,
            frame_shadow: Optional[QFrame.Shadow] = None,
            h_size_policy: Optional[QSizePolicy.Policy] = None,
            v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if selection_mode is None:
            selection_mode = self.default_selection_mode()
        if vertical_scroll_mode is None:
            vertical_scroll_mode = self.default_vertical_scroll_mode()
        self.set_selection_mode(mode=selection_mode)
        self.set_scroll_mode(mode=vertical_scroll_mode)
        return self

    @classmethod
    def default_selection_mode(cls):
        return QAbstractItemView.SelectionMode.SingleSelection

    @classmethod
    def default_vertical_scroll_mode(cls):
        return QAbstractItemView.ScrollMode.ScrollPerPixel

    @classmethod
    def default_frame_shape(cls):
        return QFrame.Shape.StyledPanel

    @classmethod
    def default_frame_shadow(cls):
        return QFrame.Shadow.Sunken

    def set_selection_mode(self, mode: Union[QAbstractItemView.SelectionMode,
                                             str]):
        if isinstance(mode, str):
            mode = selection_mode_enum_manager.get_value(mode)
        self.setSelectionMode(mode)
        self.m_selection_mode_box.set_choice_as(
            selection_mode_enum_manager.get_name(mode), False)

    def set_scroll_mode(self, mode: Union[QAbstractItemView.ScrollMode, str]):
        if isinstance(mode, str):
            mode = scroll_mode_enum_manager.get_value(mode)
        self.setVerticalScrollMode(mode)
        self.m_scroll_mode_box.set_choice_as(
            scroll_mode_enum_manager.get_name(mode), False)

    def remove_selected_items(self):
        rows = [self.row(item) for item in self.selectedItems()]
        for row in sorted(rows, reverse=True):
            self.takeItem(row)
