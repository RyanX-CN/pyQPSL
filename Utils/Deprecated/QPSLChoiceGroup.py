from QPSLClass.Base import *
from Utils.UIClass.QPSLRadioButton import QPSLRadioButton
from Utils.UIClass.QPSLGroupList import QPSLHGroupList, QPSLVGroupList


class QPSLHChoiceGroup(QPSLHGroupList):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 items: Iterable[str],
                 index=0,
                 title: str = ""):
        super().__init__(parent=parent, object_name=object_name, title=title)
        self.m_index = index
        for item in items:
            self.add_widget(
                QPSLRadioButton(self,
                                object_name="btn_{0}".format(item),
                                text=item))

        self.set_current_index(index=self.m_index)

    def current_index(self):
        return self.m_index

    def set_current_index(self, index):
        self.m_index = index
        self.radio_button(index=index).setChecked(True)

    def radio_button(self, index: int) -> QPSLRadioButton:
        return self.get_widget(index=index)


class QPSLVChoiceGroup(QPSLVGroupList):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 items: Iterable[str],
                 index=0,
                 title: str = ""):
        super().__init__(parent=parent, object_name=object_name, title=title)
        self.m_index = index
        for item in items:
            self.add_widget(
                QPSLRadioButton(self,
                                object_name="btn_{0}".format(item),
                                text=item))
        self.set_current_index(index=self.m_index)

    def current_index(self):
        return self.m_index

    def set_current_index(self, index):
        self.m_index = index
        self.radio_button(index=index).setChecked(True)

    def radio_button(self, index: int) -> QPSLRadioButton:
        return self.get_widget(index=index)
