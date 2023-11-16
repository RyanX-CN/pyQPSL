from Tool import *


class CompilePluginUI(QPSLVFrameList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self

    def to_delete(self):
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return QPSLVFrameList.to_delete(self)

    def get_named_widgets(self):
        self.box_get_bin_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_get_bin_path")
        self.box_get_include_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_get_include_path")
        self.box_get_lib_path: QPSLGetDirectoryBox = self.findChild(
            QPSLGetDirectoryBox, "box_get_lib_path")
        self.box_get_libs_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_libs_path")
        self.box_get_source_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_source_path")
        self.box_get_target_path: QPSLGetOpenFileBox = self.findChild(
            QPSLGetOpenFileBox, "box_get_target_path")
        self.edit_compile_args: QPSLLineEdit = self.findChild(
            QPSLLineEdit, "edit_compile_args")
        self.button_auto_fill: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_auto_fill")
        self.edit_command: QPSLTextEdit = self.findChild(
            QPSLTextEdit, "edit_command")
        self.button_make_command: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_make_command")
        self.button_compile: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_compile")
        self.button_test: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_test")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.get_named_widgets()
        connect_direct(self.box_get_bin_path.sig_path_set,
                       self.box_get_bin_path.set_icon_checked)
        connect_direct(self.box_get_bin_path.sig_path_setnull,
                       self.box_get_bin_path.set_icon_unchecked)
        connect_direct(self.box_get_include_path.sig_path_set,
                       self.box_get_include_path.set_icon_checked)
        connect_direct(self.box_get_include_path.sig_path_setnull,
                       self.box_get_include_path.set_icon_unchecked)
        connect_direct(self.box_get_lib_path.sig_path_set,
                       self.box_get_lib_path.set_icon_checked)
        connect_direct(self.box_get_lib_path.sig_path_setnull,
                       self.box_get_lib_path.set_icon_unchecked)
        connect_direct(self.box_get_libs_path.sig_path_set,
                       self.box_get_libs_path.set_icon_checked)
        connect_direct(self.box_get_libs_path.sig_path_setnull,
                       self.box_get_libs_path.set_icon_unchecked)
        connect_direct(self.box_get_source_path.sig_path_set,
                       self.box_get_source_path.set_icon_checked)
        connect_direct(self.box_get_source_path.sig_path_setnull,
                       self.box_get_source_path.set_icon_unchecked)
        connect_direct(self.box_get_target_path.sig_path_set,
                       self.box_get_target_path.set_icon_checked)
        connect_direct(self.box_get_target_path.sig_path_setnull,
                       self.box_get_target_path.set_icon_unchecked)
        connect_direct(self.button_auto_fill.sig_clicked,
                       self.on_click_auto_fill)
        connect_direct(self.button_make_command.sig_clicked,
                       self.on_click_make_command)
        connect_direct(self.button_compile.sig_clicked, self.on_click_compile)
        connect_direct(self.button_test.sig_clicked, self.on_click_test)

    @QPSLObjectBase.log_decorator()
    def on_click_auto_fill(self):
        dialog = QPSLVDialogList().load_attr(window_title="Select Plugin")
        box = QPSLVScrollList().load_attr(margins=(15, 15, 15, 15),
                                          spacing=10,
                                          frame_shape=QFrame.Shape.StyledPanel)
        dialog.add_widget(widget=box)
        for plugin in QPSLMainWindow.get_plugin_module_list():

            def callback(name: str):
                for title, box in zip(
                    ("bin", "include", "lib"),
                    (self.box_get_bin_path, self.box_get_include_path,
                     self.box_get_lib_path)):
                    path = "{0}/{1}/{2}".format(QPSL_Working_Directory,
                                                name.replace('.', '/'), title)
                    if os.path.exists(path):
                        box.set_path(path=path)
                    else:
                        box.set_path(path="")
                if self.box_get_lib_path.get_path():
                    paths = list(
                        listdir(dir_path=self.box_get_lib_path.get_path()))
                    self.box_get_libs_path.set_path(path=";".join(paths))
                else:
                    self.box_get_libs_path.set_path(path="")
                source_dir = "{0}/{1}/source".format(QPSL_Working_Directory,
                                                     name.replace('.', '/'))
                if os.path.exists(source_dir) and any(
                        listdir(dir_path=source_dir)):
                    self.box_get_source_path.set_path(
                        path=next(listdir(dir_path=source_dir)))
                else:
                    self.box_get_source_path.set_path(path="")
                if self.box_get_bin_path.get_path():
                    if self.box_get_source_path.get_path():
                        self.box_get_target_path.set_path(
                            path="{0}/{1}/bin/{2}.dll".format(
                                QPSL_Working_Directory, name.replace(
                                    '.', '/'), '.'.join(
                                        os.path.basename(
                                            self.box_get_source_path.get_path(
                                            )).split('.')[:-1])))
                    else:
                        self.box_get_target_path.set_path(
                            path="{0}/{1}/bin/unnamed.dll".format(
                                QPSL_Working_Directory, name.replace('.',
                                                                     '/')))
                else:
                    self.box_get_target_path.set_path(path="{0}/{1}".format(
                        QPSL_Working_Directory, name.replace('.', '/')))
                    self.box_get_target_path.sig_path_setnull.emit()
                dialog.accept()

            button = QPSLPushButton().load_attr(text=plugin)
            connect_direct(button.sig_clicked_str, callback)
            box.add_widget(widget=button, ratio=0.2)
        dialog.resize(350, 600)
        dialog.exec()

    @QPSLObjectBase.log_decorator()
    def on_click_make_command(self):
        if not self.box_get_source_path.get_path():
            raise BaseException("no source file")
        if not self.box_get_target_path.get_path():
            raise BaseException("no target file")
        para = ["-shared", "-fPIC"]
        if self.box_get_include_path.get_path():
            para.append("-I{0}".format(self.box_get_include_path.get_path()))
        if self.box_get_lib_path.get_path():
            para.append("-L{0}".format(self.box_get_lib_path.get_path()))
        if self.box_get_libs_path.get_path():
            for lib in self.box_get_libs_path.get_path().split(';'):
                para.append("-l{0}".format('.'.join(
                    str.split(os.path.basename(lib), '.')[:-1])))
        para.append(self.edit_compile_args.text())
        source_file = self.box_get_source_path.get_path()
        target_file = self.box_get_target_path.get_path()
        self.edit_command.setText("g++ {0} -o {1} {2}".format(
            source_file, target_file, ' '.join(para)))

    @QPSLObjectBase.log_decorator()
    def on_click_compile(self):
        res = os.system(self.edit_command.document().toRawText())
        loading_info("compile res = {0}".format(res))

    @QPSLObjectBase.log_decorator()
    def on_click_test(self):
        if os.path.abspath(
                self.box_get_bin_path.get_path()) not in os_path_list():
            os_path_append(self.box_get_bin_path.get_path())
        try:
            name = os.path.basename(self.box_get_target_path.get_path())
            dll = load_dll(dll_file_path=name)
        except BaseException as e:
            loading_error("failed to load {0}, error = {1}".format(name, e))
        else:
            loading_info("made it to load {0}, {1}".format(name, dll))
            win32api.FreeLibrary(dll._handle)


MainWidget = CompilePluginUI
