from Tool import *


class Export_MainWindow(QPSLMainWindow):

    def __init__(self, chosen: Iterable[str], banned: Iterable[str],
                 new_dir_path: str) -> None:
        """本界面窗口用于将项目加密导出到另外的文件夹

        Args:
            chosen (Iterable[str]):  chosen 的路径默认为选中。
            banned (Iterable[str]):  banned 的路径不会出现在树形图里。
            new_dir_path (str): 默认要导出的路径（也可手动点击按钮修改）
        """
        super().__init__(None)
        self.setWindowTitle("export")
        self.m_widget = QPSLHorizontalGroupList(self, "widget")
        banned = set(map(lambda s: os.path.abspath(s), banned))
        self.m_tree = QPSLFileTree(self.m_widget,
                                   object_name="tree",
                                   dir_path=".",
                                   header_label="choose file/files",
                                   filter=lambda s:
                                   ((s not in banned) and
                                    (not s.endswith("__pycache__"))))
        self.set_default_chosen(
            chosen=set(map(lambda s: os.path.abspath(s), chosen)))

        self.m_box_right = QPSLVerticalGroupList(self, "right")
        self.m_btn_choose_new_dir_path = QPSLChooseDirButton(
            self.m_box_right,
            object_name="choose",
            prefix="path: ",
            init_path=os.path.abspath(new_dir_path))
        self.m_btn_encode = QPSLToggleButton(self.m_box_right,
                                             object_name="encode",
                                             closed_text="do not encode",
                                             opened_text="encode")
        connect_direct(self.m_btn_encode.sig_open,
                       self.m_btn_encode.set_opened)
        connect_direct(self.m_btn_encode.sig_close,
                       self.m_btn_encode.set_closed)
        self.m_btn_clear = QPSLPushButton(self.m_box_right,
                                          object_name="btn_clear",
                                          text="clear old files")
        connect_direct(self.m_btn_clear.sig_clicked, self.clear_old_files)
        self.m_btn_export = QPSLPushButton(self.m_box_right,
                                           object_name="btn_export",
                                           text="export")
        connect_direct(self.m_btn_export.sig_clicked, self.export)
        self.m_box_right.add_widgets(widgets=(self.m_btn_choose_new_dir_path,
                                              self.m_btn_encode,
                                              self.m_btn_clear,
                                              self.m_btn_export))

        self.m_widget.add_widgets(widgets=(self.m_tree, self.m_box_right))
        self.m_widget.set_stretch(sizes=(1, 1))
        self.setCentralWidget(self.m_widget)

    def set_default_chosen(self, chosen: Set[str]):

        def dfs(item: QTreeWidgetItem, path: str):
            path = os.path.abspath(os.path.join(path, item.text(0)))
            if (path in chosen):
                item.setCheckState(0, 2)
                self.m_tree.push_down(item=item, column=0, push_up=False)
            else:
                for i in range(item.childCount()):
                    dfs(item=item.child(i), path=path)

        for i in range(self.m_tree.topLevelItemCount()):
            dfs(item=self.m_tree.topLevelItem(i), path='.')
        self.m_tree.push_up(0)
        self.setCentralWidget(self.m_tree)

    def clear_old_files(self):
        new_dir_path = self.m_btn_choose_new_dir_path.get_path()
        if not os.path.exists(new_dir_path):
            return
        remove_to_trash(new_dir_path)

    def get_cached_pyd_file(self, old_file: str):
        old_file = os.path.relpath(old_file).replace('\\', '/')
        c_dir = "Compile/c_{0}".format(sys.version.split()[0])
        pyd_dir = "Compile/pyd_{0}".format(sys.version.split()[0])
        ss = old_file.split('/')
        build_dir = pyd_dir
        for i in range(len(ss) - 1, 0, -1):
            if "__init__.py" not in os.listdir('/'.join(ss[:i])):
                build_dir = "{0}/{1}".format(pyd_dir, '/'.join(ss[:i]))
                break
        sys.argv.append("build_ext")
        distutils.core.setup(
            ext_modules=Cython.Build.cythonize(
                module_list=old_file,
                build_dir=c_dir,
                compiler_directives={'language_level': "3"}),
            options={"build": {
                "build_lib": build_dir,
            }},
        )
        sys.argv.pop()
        target_path = "{0}/{1}d".format(pyd_dir, old_file)
        dir = os.path.dirname(target_path)
        for file in os.listdir(dir):
            if file.split('.')[0] == old_file.split('/')[-1].split(
                    '.')[0] and file.endswith('pyd'):
                return '{0}/{1}'.format(dir, file)

    def export(self):
        to_encode = []

        def put_in_queue(p_old: str, p_new: str):
            if not self.m_btn_encode.get_state():
                copy_file(p_old, p_new)
            elif not p_old.endswith('py'):
                copy_file(p_old, p_new)
            elif p_old.endswith("Main.py"):
                copy_file(p_old, p_new)
            else:
                to_encode.append((p_old, p_new))

        def clear_queue():
            for p_old, p_new in tqdm.tqdm(to_encode):
                copy_file(
                    old_file_path=self.get_cached_pyd_file(old_file=p_old),
                    new_file_path=p_new + 'd')

        def dfs(cur: Dict[str, Tuple[str, Dict]], p_old: str, p_new: str):
            if os.path.isfile(p_old):
                return put_in_queue(p_old=p_old, p_new=p_new)
            else:
                if not os.path.exists(p_new):
                    os.mkdir(p_new)
                for path, (state, subs) in cur.items():
                    if state:
                        dfs(subs, os.path.abspath(os.path.join(p_old, path)),
                            os.path.abspath(os.path.join(p_new, path)))

        dfs(cur=self.m_tree.to_dict(absolute=False),
            p_old='.',
            p_new=self.m_btn_choose_new_dir_path.get_path())
        clear_queue()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Export_MainWindow(chosen=("AGADP", "QPSLClass", "resources",
                                            "Main.py", "requirement.txt",
                                            "run.bat", "Tool.py"),
                                    banned=(".git", ".vscode", "build",
                                            "Compile", ".gitattributes",
                                            ".gitignore"),
                                    new_dir_path="../pyQPSL0327")
    main_window.show()
    sys.exit(app.exec_())
