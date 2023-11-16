from QPSLClass.Base import *
from ..BaseClass import *


class QPSLTabWidget(QTabWidget, QPSLWidgetBase):
    sig_index_changed_to = pyqtSignal(int)
    sig_label_changed_to = pyqtSignal(str)
    sig_tab_changed_to = pyqtSignal(QPSLWidgetBase)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        if "widgets" in json:
            if "titles" in json:
                for dic, title in zip(json.get("widgets"), json.get("titles")):
                    self.add_tab(tab=QPSLObjectBase.from_json(dic),
                                 title=title)
            else:
                for dic in json.get("widgets"):
                    self.add_widget(widget=QPSLObjectBase.from_json(dic))
        tabbar_visible = json.get("tabbar_visible")
        if tabbar_visible is None:
            tabbar_visible = self.default_tabbar_visible()
        self.set_tabbar_visible(tabbar_visible)

    def to_json(self):
        res = super().to_json()
        if self.get_widgets():
            res.update({
                "widgets": [widget.to_json() for widget in self.get_widgets()]
            })
            res.update({
                "titles":
                [self.tabText(i) for i in range(len(self.get_widgets()))]
            })
        if self.get_tabbar_visible() != self.default_tabbar_visible():
            res.update({"tabbar_visible": self.get_tabbar_visible()})
        return res

    def __init__(self):
        super().__init__()
        self.m_tabs: List[QPSLWidgetBase] = []
        self.m_tab_menu = QMenu("change tab...")
        self.m_tabbar_visible = self.default_tabbar_visible()
        dict.update(self.action_dict,
                    {self.m_tab_menu.title(): self.m_tab_menu})
        self.m_tabbar_visible_box = ToggleBox(
            "tabbar visible",
            default_value=self.default_tabbar_visible(),
            callback=self.set_tabbar_visible,
            config_key=None)
        dict.update(
            self.action_dict,
            {self.m_tabbar_visible_box.get_name(): self.m_tabbar_visible_box})
        connect_direct(self.m_tab_menu.aboutToShow, self.update_menu_tab)
        connect_direct(self.currentChanged, self.on_current_changed)

    def to_delete(self):

        return super().to_delete()

    def load_attr(self,
                  tabbar_visible: Optional[bool] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if tabbar_visible is None:
            tabbar_visible = self.default_tabbar_visible()
        self.set_tabbar_visible(tabbar_visible)
        return self

    @classmethod
    def is_container(cls):
        return True

    @classmethod
    def default_tabbar_visible(cls):
        return True

    def add_tab(self, tab: QPSLWidgetBase, title: str):
        self.addTab(tab, title)
        self.m_tabs.append(tab)

    def insert_tab(self, tab: QPSLWidgetBase, title: str, index: int):
        self.insertTab(index, tab, title)
        self.m_tabs.insert(index, tab)

    def remove_tab(self, tab: QPSLWidgetBase):
        self.removeTab(self.indexOf(tab))
        self.m_tabs.remove(tab)

    def remove_tabs(self, tabs: List[QPSLWidgetBase]):
        for tab in tabs:
            self.remove_tab(tab=tab)

    def remove_tab_and_delete(self, tab: QPSLWidgetBase):
        self.removeTab(self.indexOf(tab))
        self.m_tabs.remove(tab)
        tab.to_delete()
        tab.deleteLater()

    def remove_tabs_and_delete(self, tabs: List[QPSLWidgetBase]):
        for tab in tabs:
            self.remove_tab_and_delete(tab=tab)

    def get_tab(self, index: int):
        return self.m_tabs[index]

    def get_tabs(self):
        return self.m_tabs

    def add_widget(self, widget: QPSLWidgetBase):
        self.add_tab(tab=widget, title="")

    def add_widgets(self, widgets: Iterable[QPSLWidgetBase]):
        for widget in widgets:
            self.add_widget(widget=widget)

    def insert_widget(self, widget: QPSLWidgetBase, index: int):
        self.insert_tab(tab=widget, title="", index=index)

    def remove_widget(self, widget: QPSLWidgetBase):
        self.remove_tab(tab=widget)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        self.remove_tabs(tabs=widgets)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        self.remove_tab_and_delete(tab=widget)

    def remove_widgets_and_delete(self, widgets: List[QPSLWidgetBase]):
        self.remove_tabs_and_delete(tabs=widgets)

    def index_of(self, widget: QPSLWidgetBase):
        return self.indexOf(widget)

    def clear_widgets(self):
        self.remove_widgets_and_delete(widgets=self.m_tabs.copy())

    def get_widget(self, index: int):
        return self.get_tab(index=index)

    def get_widgets(self):
        return self.get_tabs()

    def on_current_changed(self, index: int):
        self.sig_index_changed_to.emit(self.currentIndex())
        self.sig_label_changed_to.emit(self.current_tab_label())
        self.sig_tab_changed_to.emit(self.currentWidget())

    def hide_tabbar(self):
        self.set_tabbar_visible(False)

    def show_tabbar(self):
        self.set_tabbar_visible(True)

    def set_tabbar_visible(self, b: bool):
        tabbar = self.findChild(QTabBar)
        tabbar.setVisible(b)
        self.m_tabbar_visible = b
        self.m_tabbar_visible_box.set_value(value=b, with_callback=False)

    def get_tabbar_visible(self):
        return self.m_tabbar_visible

    def current_tab_label(self):
        return self.tabText(self.currentIndex())

    def update_menu_tab(self):
        self.m_tab_menu.clear()

        def wrap(i):

            def inner():
                self.setCurrentIndex(i)

            return inner

        for i in range(len(self.get_widgets())):
            self.m_tab_menu.addAction(
                "tab {0}: {1}".format(i + 1, self.tabText(i)), wrap(i))

    @register_multi_texts_attribute(action_name="set label titles")
    def label_titles_attr(self):
        n = len(self.get_tabs())
        label_texts = [self.tabText(i) for i in range(n)]
        key_texts = ["No.{0}".format(i + 1) for i in range(n)]

        def callback(texts):
            for i, text in enumerate(texts):
                self.setTabText(i, text)

        return label_texts, "Set Label Titles", key_texts, callback, QSize(
            400, 40 * (n + 1))
