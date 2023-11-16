from Tool import *


class AGADPLoginBox(QPSLVDialogList, QPSLPluginBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        username = json.get("username")
        password = json.get("password")
        size = json.get("size")
        if username is None:
            username = self.default_username()
        if password is None:
            password = self.default_password()
        self.m_username = username
        self.m_password = password
        self.resize(*str_to_int_tuple(size))
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        if self.m_username != self.default_username():
            res.update({"username": self.m_username})
        if self.m_password != self.default_password():
            res.update({"password": self.m_password})
        res.update({"size": tuple_to_str((self.width(), self.height()))})
        return res

    def __init__(self):
        super().__init__()
        self.m_log_in_keys: dict[str, str] = {"admin": "admin"}
        self.m_username = self.default_username()
        self.m_password = self.default_password()

    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self

    def to_delete(self):
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()

    @classmethod
    def default_username(cls):
        return "admin"

    @classmethod
    def default_password(cls):
        return "admin"

    def get_named_widgets(self):
        self.label_image: QPSLScalePixmapLabel = self.findChild(
            QPSLScalePixmapLabel, "label_image")
        self.combo_edit_username: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_username")
        self.combo_edit_password: QPSLComboLineEdit = self.findChild(
            QPSLComboLineEdit, "combo_edit_password")
        self.button_login: QPSLPushButton = self.findChild(
            QPSLPushButton, "button_login")

    def setup_logic(self):
        self.get_named_widgets()
        self.label_image.set_pixmap(
            QPixmap("./{0}/resources/eyes.png".format(
                __package__.replace('.', '/'))))
        self.combo_edit_username.set_value_text(text=self.m_username)
        self.combo_edit_password.set_value_text(text=self.m_password)
        self.combo_edit_password.set_echo_mode(echo_mode=QLineEdit.Password)

        connect_direct(self.button_login.sig_clicked, self.check_login_info)
        connect_direct(self.combo_edit_password.sig_return_pressed,
                       self.button_login.animateClick)
        connect_direct(self.combo_edit_username.sig_editing_finished_at,
                       self.change_username)
        connect_direct(self.combo_edit_password.sig_editing_finished_at,
                       self.change_password)

    @QPSLObjectBase.log_decorator()
    def change_username(self, username: str):
        self.m_username = username

    @QPSLObjectBase.log_decorator()
    def change_password(self, password: str):
        self.m_password = password

    @QPSLObjectBase.log_decorator()
    def check_login_info(self):
        username = self.combo_edit_username.value_text()
        password = self.combo_edit_password.value_text()
        if username not in self.m_log_in_keys:
            message = QPSLMessageBox().load_attr(text="User not found",
                                                 window_title="login failed")
            message.resize(400, 200)
            self.add_error(msg="User not found")
            message.exec()
            return
        if password != self.m_log_in_keys[username]:
            message = QPSLMessageBox().load_attr(text="Wrong password",
                                                 window_title="login failed")
            message.resize(400, 200)
            self.add_error(msg="Wrong password")
            message.exec()
            return
        self.add_warning(msg="%s log in" % username)
        self.accept()
