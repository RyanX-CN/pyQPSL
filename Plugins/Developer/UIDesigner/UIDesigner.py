from PyQt5.QtCore import QEvent, QObject
from Tool import *
from Utils.UIClass.QPSLDialogList import QPSLVDialogList
from .UITreeModel import TreeModel


class UIDesigner(QPSLHSplitter, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        if "lru" in json:
            self.m_lru = json.get("lru")
        self.setup_logic()
        self.setSizes((660, 3000))

    def to_json(self):
        res: Dict = super().to_json()
        res.update({"lru": self.m_lru})
        return res

    def __init__(self):
        super().__init__()
        self.m_lru: List[str] = []
        self.m_blink_locks: Set[QPSLWidgetBase] = weakref.WeakSet()

    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self

    def to_delete(self):
        self.reject_remaining()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()

    def get_named_widgets(self):
        self.tab_edit_json: QPSLTabWidget = self.findChild(
            QPSLTabWidget, "tab_edit_json")
        self.tree_view: QPSLTreeView = self.findChild(QPSLTreeView,
                                                      "tree_view")
        self.scroll_attribute: QPSLVScrollArea = self.findChild(
            QPSLVScrollArea, "scroll_attribute")
        self.box_buttons: QPSLHFrameList = self.findChild(
            QPSLHFrameList, "box_buttons")
        self.button_add: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_add")
        self.button_insert: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_insert")
        self.button_copy: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_copy")
        self.button_remove: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_remove")
        self.checkbox_move_cursor: QPSLCheckBox = self.findChild(
            QPSLCheckBox, "checkbox_move_cursor")
        self.box_json: QPSLVFrameList = self.findChild(QPSLVFrameList,
                                                       "box_json")
        self.edit_of_json: QPSLTextEdit = self.findChild(
            QPSLTextEdit, "edit_of_json")
        self.button_load_json: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_load_json")
        self.box_show: QPSLHFrameList = self.findChild(QPSLHFrameList,
                                                       "box_show")

    def setup_logic(self):
        self.get_named_widgets()
        self.m_model = TreeModel(self.box_show)
        self.tree_view.setModel(self.m_model)
        for widget in self.box_show.yield_all_widgets():
            if widget != self.box_show:
                widget.installEventFilter(self)

        # model
        connect_direct(self.tree_view.selectionModel().selectionChanged,
                       self.on_tree_view_current_changed)

        connect_direct(self.button_add.sig_clicked, self.on_click_add)
        connect_direct(self.button_insert.sig_clicked, self.on_click_insert)
        connect_direct(self.button_copy.sig_clicked, self.on_click_copy)
        connect_direct(self.button_remove.sig_clicked, self.on_click_remove)

        # json
        connect_direct(self.tab_edit_json.sig_tab_changed_to,
                       self.on_tab_changed)
        connect_direct(self.button_load_json.sig_clicked,
                       self.on_click_load_json)

    def reject_remaining(self):
        if self.scroll_attribute.get_widgets():
            toolbox: QPSLToolBox = self.scroll_attribute.get_widget(
                0).remove_type()
            while toolbox.count():
                i = toolbox.count() - 1
                dialog: QDialog = toolbox.widget(i)
                dialog.finished.disconnect()
                dialog.reject()
                toolbox.removeItem(i)

    def reset_attribute_boxes(self, index: QModelIndex):
        if not index.isValid(): return
        self.reject_remaining()
        self.scroll_attribute.clear_widgets()
        toolbox = QPSLToolBox().load_attr()
        widget: QPSLWidgetBase = index.internalPointer()
        for attr in get_registered_class_attrs(widget):
            if widget.filter_of_attr(attr=attr):
                dialog = attr.make_dialog(widget)

                def wrap(toolbox_index: int, model_index: QModelIndex):

                    def finish_callback():
                        toolbox.removeItem(toolbox_index)
                        self.reset_attribute_boxes(index=model_index)

                    return finish_callback

                dialog.finished.connect(
                    wrap(toolbox_index=toolbox.count(), model_index=index))
                toolbox.addItem(dialog, dialog.windowTitle())
        self.scroll_attribute.add_widget(widget=toolbox)

    def blink_widget(self, widget: QPSLWidgetBase):
        old_palette = widget.palette()
        autofill = widget.autoFillBackground()

        # widget.setAutoFillBackground(True)

        def func():
            if widget in self.m_blink_locks: return
            self.m_blink_locks.add(widget)
            old_color = QColor("#000000")
            new_color = QColor("#ffffff")
            func_name = self.on_set_widget_color.__name__
            for i in range(40):
                now_color = QColor()
                i = min(i % 20, 20 - i % 20)
                now_color.setRed(
                    (old_color.red() * (10 - i) + new_color.red() * i) // 10)
                now_color.setGreen((old_color.green() *
                                    (10 - i) + new_color.green() * i) // 10)
                now_color.setBlue(
                    (old_color.blue() * (10 - i) + new_color.blue() * i) // 10)
                QMetaObject.invokeMethod(self, func_name,
                                         Q_ARG(QWidget, widget),
                                         Q_ARG(QColor, now_color))
                sleep_for(50)
            widget.setPalette(old_palette)
            self.m_blink_locks.remove(widget)

        QThreadPool.globalInstance().start(func)

    def on_tree_view_current_changed(self, selected: QItemSelection,
                                     deselected: QItemSelection):

        if not selected.indexes():
            return
        self.set_cursor(model_index=selected.indexes()[0])

    @pyqtSlot(QWidget, QColor)
    def on_set_widget_color(self, widget: QPSLWidgetBase, color: QColor):
        widget.update_background_palette(color=color)

    def on_click_add(self):
        if not self.tree_view.selectedIndexes():
            if self.box_show.get_widgets(): return
            parent_index = self.tree_view.rootIndex()
            parent_widget = self.box_show
        else:
            parent_index = self.tree_view.selectedIndexes()[0]
            parent_widget: QPSLWidgetBase = parent_index.internalPointer()
            if not parent_widget.is_container(): return
        self.widget_choices_factory(parent_index=parent_index,
                                    parent_widget=parent_widget,
                                    index=len(
                                        parent_widget.get_widgets())).exec()

    def on_click_insert(self):
        if not self.tree_view.selectedIndexes(): return
        cur_index = self.tree_view.selectedIndexes()[0]
        cur_widget: QPSLWidgetBase = cur_index.internalPointer()
        parent_index = cur_index.parent()
        if not parent_index.isValid(): return
        parent_widget: QPSLWidgetBase = parent_index.internalPointer()
        self.widget_choices_factory(
            parent_index=parent_index,
            parent_widget=parent_widget,
            index=parent_widget.index_of(cur_widget)).exec()

    def on_click_copy(self):
        if not self.tree_view.selectedIndexes(): return
        cur_index = self.tree_view.selectedIndexes()[0]
        cur_widget: QPSLWidgetBase = cur_index.internalPointer()
        clipboard_setText(text=json.dumps(cur_widget.to_json()))

    def on_click_remove(self):
        if not self.tree_view.selectedIndexes(): return
        self.reset_attribute_boxes(QModelIndex())
        index = self.tree_view.selectedIndexes()[0]
        widget: QPSLWidgetBase = index.internalPointer()
        parent_index = index.parent()
        parent_widget: QPSLWidgetBase = widget.qpsl_parent()
        row = index.row()
        self.m_model.beginRemoveRows(parent_index, row, row)
        widget.to_delete()
        parent_widget.remove_widget(widget=widget)
        self.m_model.endRemoveRows()

    def on_tab_changed(self, tab: QPSLWidgetBase):
        if tab == self.box_json and self.box_show.get_widgets():
            text = json.dumps(self.box_show.get_widget(0).to_json(),
                              indent=4,
                              sort_keys=True)
            self.edit_of_json.clear()
            self.edit_of_json.setText(text)

    def on_click_load_json(self):
        self.m_model.beginResetModel()
        self.box_show.clear_widgets()
        dic = json.loads(self.edit_of_json.document().toPlainText())
        if dic:
            widget = QPSLObjectBase.from_json(dic)
            self.box_show.add_widget(widget=widget)
        else:
            self.box_show.clear_widgets()
        self.m_model.endResetModel()

    def widget_choices_factory(self, parent_index: QModelIndex,
                               parent_widget: QPSLWidgetBase, index: int):
        dialog = QPSLVDialogList().load_attr(window_title="Select Widget")
        box = QPSLVScrollList().load_attr(margins=(15, 15, 15, 15),
                                          spacing=10,
                                          frame_shape=QFrame.Shape.StyledPanel)
        dialog.add_widget(widget=box)
        ui_classes: List[type] = []
        for cls in get_registered_classes().values():
            if "ui" in cls.__module__.lower():
                ui_classes.append(cls)
        from Utils.Classes.QPSLDCAMView import QPSLDCAMView
        ui_classes.append(QPSLDCAMView)
        # from Plugins.Simple.Thorlabs_MTS50Plugin.Thorlabs_MTS50Plugin import Thorlabs_MTS50PluginUI
        # ui_classes.append(Thorlabs_MTS50PluginUI)
        # from Plugins.Simple.NIDAQmxAOPlugin.NIDAQmxAOPlugin import NIDAQmxAOPluginUI
        # ui_classes.append(NIDAQmxAOPluginUI)
        self.m_lru = list(
            filter(lambda s: any(t.__name__ == s for t in ui_classes),
                   self.m_lru))

        def get_sort_key(t: type):
            try:
                index = self.m_lru.index(t.__name__)
            except:
                index = -1
            return -index, t.__name__

        ui_classes.sort(key=get_sort_key)

        for cls in ui_classes:

            def callback(name):
                widget_type: type[QPSLWidgetBase] = get_registered_class(
                    name=name)
                self.insert_widget_in_tree(parent_index=parent_index,
                                           parent_widget=parent_widget,
                                           widget=widget_type().load_attr(),
                                           index=index)
                if widget_type.__name__ in self.m_lru:
                    self.m_lru.remove(widget_type.__name__)
                self.m_lru.append(widget_type.__name__)
                dialog.accept()

            button = QPSLPushButton()
            button.load_attr(text=cls.__name__)
            connect_direct(button.sig_clicked_str, callback)
            box.add_widget(widget=button, ratio=0.2)

        def callback():
            widget_json = clipboard_getText()
            try:
                dic = json.loads(widget_json)
                try:
                    self.insert_widget_in_tree(
                        parent_index=parent_index,
                        parent_widget=parent_widget,
                        widget=QPSLObjectBase.from_json(dic),
                        index=index)
                    dialog.accept()
                    return
                except:
                    self.add_error("failed to build widget from json")
            except:
                self.add_error("failed to load json from clipboard")
            dialog.accept()

        button = QPSLPushButton().load_attr(text="clip board")
        button.setToolTip(clipboard_getText())
        connect_direct(button.sig_clicked, callback)
        dialog.add_widget(widget=button)
        dialog.set_stretch(sizes=(6, 1))
        dialog.resize(250, 500)
        return dialog

    def set_cursor(self, model_index: QModelIndex):
        self.reset_attribute_boxes(index=model_index)
        widget: QPSLWidgetBase = model_index.internalPointer()
        self.blink_widget(widget=widget)

    def insert_widget_in_tree(self, parent_index: QModelIndex,
                              parent_widget: QPSLWidgetBase,
                              widget: QPSLWidgetBase, index: int):
        for w in widget.yield_all_widgets():
            w.installEventFilter(self)
        row = len(parent_widget.get_widgets())
        self.m_model.beginInsertRows(parent_index, row, row)
        parent_widget.insert_widget(widget=widget, index=index)
        self.m_model.endInsertRows()
        child_index = parent_index.child(row, 0)
        if self.checkbox_move_cursor.isChecked():
            self.tree_view.setCurrentIndex(child_index)
        else:
            self.reset_attribute_boxes(self.tree_view.currentIndex())

    def eventFilter(self, obj: QPSLWidgetBase, ev: QEvent) -> bool:
        if ev.type() == QEvent.Type.MouseButtonPress:
            a = []
            while obj != self.box_show:
                p: QPSLWidgetBase = obj.qpsl_parent()
                if p.is_container():
                    a.append(p.index_of(obj))
                else:
                    a.append(0)
                obj = p
            model_index = QModelIndex()
            for idx in a[::-1]:
                model_index = self.m_model.index(idx, 0, model_index)
            self.tree_view.setCurrentIndex(model_index)
            self.set_cursor(model_index=model_index)
            return True
        return super().eventFilter(obj, ev)


MainWidget = UIDesigner