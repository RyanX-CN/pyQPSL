from QPSLClass.Base import *
from ..BaseClass import *
from ..UIClass.QPSLDockWidget import QPSLDockWidget
from ..UIClass.QPSLMenuBar import QPSLMenuBar


class QPSLMainWindow(QMainWindow, QPSLWidgetBase):
    sig_plugin_closed = pyqtSignal()
    sig_plugin_closed_of = pyqtSignal(QPSLDockWidget)

    def __init__(self):
        super().__init__()
        self.m_is_single_plugin: bool = init_config_getset(
            keys=("plugin_mode", "is_single_plugin"), value=False)
        self.setup_logic()

    def setup_logic(self):
        self.setMenuBar(QPSLMenuBar())
        if not self.m_is_single_plugin:
            self.add_menu_plugins()
        self.add_menu_settings()
        add_global_single_choice_box(QPSL_App_Style_Choice_Box)
        QPSL_App_Style_Choice_Box.call()
        add_global_single_choice_box(QPSL_Log_Level_Choice_Box)
        if QPSL_Dark_Light_Style_Choice_Box is not None:
            add_global_single_choice_box(QPSL_Dark_Light_Style_Choice_Box)
            QPSL_Dark_Light_Style_Choice_Box.call()
        add_global_toggle_box(box=QPSL_UI_Load_Path_Box)
        if QPSL_Material_Themes_Choice_PopBox is not None:
            add_global_single_choice_popbox(QPSL_Material_Themes_Choice_PopBox)
            QPSL_Dark_Light_Style_Choice_Box.call()
        QPSL_App_Mode_PopBox.set_choice_list(
            choices=["Multi Plugins"] +
            QPSLMainWindow.get_plugin_module_list(),
            callback=self.set_plugin_mode)
        if self.m_is_single_plugin:
            QPSL_App_Mode_PopBox.set_choice_as(
                choice=init_config_get(keys=("plugin_mode",
                                             "single_plugin_module")),
                with_callback=False)
        else:
            QPSL_App_Mode_PopBox.set_choice_as(choice="Multi Plugins",
                                               with_callback=False)
        add_global_single_choice_popbox(box=QPSL_App_Mode_PopBox)
        action = QAction("reboot")
        connect_direct(action.triggered, self.reboot)
        add_global_action(action)
        connect_direct(self.sig_plugin_closed_of, self.remove_widget_in_dock)
        if self.m_is_single_plugin:
            single_plugin_module = init_config_getset(
                keys=(
                    "plugin_mode",
                    "single_plugin_module",
                ),
                value="Plugins.Simple.DemoPlugin")
            self.set_single_plugin_central_widget(
                module_path=single_plugin_module)
            single_plugin_size = str_to_int_tuple(
                init_config_getset(keys=(
                    "plugin_mode",
                    "single_plugin_size",
                ),
                                   value="1000; 500"))
            self.resize(*single_plugin_size)
            self.setWindowTitle(single_plugin_module.split('.')[-1])
            # self.menuBar().hide()
        else:
            self.resize(1000, 500)
            self.setWindowTitle("QPSL-pyQt-{0}.{1}".format(
                init_config_get(keys=("version", "main_version")),
                init_config_get(keys=("version", "sub_version"))))

    @staticmethod
    def _get_plugin_module_list(sub_dir: str) -> List[str]:
        dir_name = "Plugins/{0}".format(sub_dir)
        abs_name = "{0}/{1}".format(QPSL_Working_Directory, dir_name)
        res = []
        for dir in os.listdir(abs_name):
            fullname = os.path.join("{0}/{1}".format(abs_name, dir))
            if os.path.isdir(fullname) and "cache" not in dir:
                module_path = "{0}/{1}".format(dir_name, dir).replace('/', '.')
                res.append(module_path)
        return res

    @staticmethod
    def get_plugin_module_list():
        return QPSLMainWindow._get_plugin_module_list(
            sub_dir="Simple") + QPSLMainWindow._get_plugin_module_list(
                sub_dir="Developer")

    def reboot(self):
        self.close()
        os.system("start /b {0} Main.py".format(sys.executable))

    def set_plugin_mode(self, option: str):
        if option == "Multi Plugins":
            init_config_set(keys=(
                "plugin_mode",
                "is_single_plugin",
            ),
                            value=False)
        else:
            init_config_set(keys=(
                "plugin_mode",
                "is_single_plugin",
            ),
                            value=True)
            init_config_set(keys=(
                "plugin_mode",
                "single_plugin_module",
            ),
                            value=option)
        self.reboot()

    def make_sub_plugin_menu(self, action_name: str, sub_dir: str):
        menu = QMenu(action_name)
        dict.update(self.action_dict, {action_name: menu})
        module_list = self._get_plugin_module_list(sub_dir=sub_dir)
        for module_path in module_list:

            def wrap(path: str):

                def callback():
                    self.on_module_clicked(module_path=path)

                return callback

            menu.addAction(module_path.split('.')[-1], wrap(path=module_path))
        return menu

    def add_menu_plugins(self):
        menu = self.menuBar().addMenu("plugins")
        # menu.addMenu(
        #     self.make_plugin_action_menu(action_name="python plugins.",
        #                                  dir_name="Plugins/Plugins"))
        # menu.addMenu(
        #     self.make_plugin_action_menu(action_name="external plugins.",
        #                                  dir_name="Plugins/Externals"))
        # menu.addMenu(
        #     self.make_plugin_action_menu(action_name="combined plugins.",
        #                                  dir_name="Plugins/Combines"))
        menu.addMenu(
            self.make_sub_plugin_menu(action_name="simple plugins.",
                                      sub_dir="Simple"))
        menu.addMenu(
            self.make_sub_plugin_menu(action_name="combined plugins.",
                                      sub_dir="Combine"))
        menu.addMenu(
            self.make_sub_plugin_menu(action_name="developer plugins.",
                                      sub_dir="Developer"))
        menu.addMenu(
            self.make_sub_plugin_menu(action_name="analysis plugins.",
                                      sub_dir="Analysis"))

    def add_menu_settings(self):
        action = self.menuBar().addAction("settings")
        menu = QMenu()
        action.setMenu(menu)
        self = weakref.proxy(self)

        def callback():
            menu.clear()
            for name, act in dict.items(get_global_settings()):
                action_attach_to_menu(act=act, menu=menu)

        connect_direct(action.menu().aboutToShow, callback)

    def add_widget_in_dock(self, widget: QPSLWidgetBase) -> QPSLDockWidget:
        name = auto_generate_plugin_name(widget.__class__.__name__)
        dock_widget = QPSLDockWidget()
        dock_widget.setWidget(widget)
        dock_widget.setWindowTitle(name)
        if any(get_opened_plugins()):
            self.tabifyDockWidget(next(get_opened_plugins()), dock_widget)
        else:
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,
                               dock_widget)
        QTimer.singleShot(0, self.move_to_center_of_desktop)
        add_opened_plugins(dock_widget)
        return dock_widget

    def remove_widget_in_dock(self, dock_widget: QPSLDockWidget):
        remove_opened_plugins(dock_widget)
        dock_widget.deleteLater()

    def make_plugin_widget(self, module_path: str):
        mod = module_path.split('.')[-1]
        self.add_debug(msg="load module {0} ...".format(mod))
        _class = getattr(
            importlib.import_module("{0}.{1}".format(module_path, mod)),
            "MainWidget")
        widget: QPSLWidgetBase = _class()
        try:
            widget.load_attr()
            return widget
        except BaseException as e:
            widget.to_delete()
            widget.deleteLater()
            raise e

    def on_module_clicked(self, module_path: str):
        widget = self.make_plugin_widget(module_path=module_path)
        if widget is None: return
        dock_widget = self.add_widget_in_dock(widget=widget)
        dock_widget.show()
        dock_widget.raise_()
        connect_direct(dock_widget.sig_dockwidget_closed,
                       self.sig_plugin_closed)
        connect_direct(dock_widget.sig_dockwidget_closed_of,
                       self.sig_plugin_closed_of)
        return dock_widget

    @QPSLObjectBase.log_decorator()
    def set_single_plugin_central_widget(self, module_path: str):
        widget = self.make_plugin_widget(module_path=module_path)
        if widget is None: return
        if self.centralWidget() is not None:
            widget: QPSLWidgetBase = self.centralWidget()
            widget.to_delete()
        self.setCentralWidget(widget)
        QTimer.singleShot(0, self.move_to_center_of_desktop)

    def move_to_center_of_desktop(self):
        desktop = QApplication.desktop()
        self.move((desktop.width() - self.width()) // 2,
                  (desktop.height() - self.height()) // 2)

    def closeEvent(self, event: QCloseEvent):
        if self.m_is_single_plugin:
            if self.centralWidget() is not None:
                widget = self.centralWidget()
                if isinstance(widget, QPSLObjectBase):
                    widget.to_delete()
        self.showMinimized()
        for tab in list(get_opened_plugins()):
            tab.close()
        return super().closeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.m_is_single_plugin:
            init_config_set(keys=("plugin_mode", "single_plugin_size"),
                            value=tuple_to_str(
                                (event.size().width(), event.size().height())))
        return super().resizeEvent(event)