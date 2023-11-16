from QPSLClass.Base import *
from ..Hooks import *


class QPSLPluginBase:

    def __init__(self) -> None:
        super().__init__()
        ui_load_config = init_config_getset(keys=("ui", "UI load path"),
                                            value="always ask")

        if ui_load_config == "Conf/ui.json":
            self.m_ui_file = QPSL_UI_Config_Path
        elif ui_load_config == "Plugin/*/ui.json":
            self.m_ui_file = "{0}/{1}/ui.json".format(
                QPSL_Working_Directory,
                '/'.join(self.__module__.split('.')[:-1]))
        else:
            res = QFileDialog.getOpenFileName(None,
                                              directory=QPSL_Working_Directory,
                                              filter="json files(*.json)")
            self.m_ui_file = res[0]

        self.m_auto_save_box = ToggleBox(
            "auto save",
            default_value=init_config_getset(keys=("ui", "autosave",
                                                   self.__class__.__name__),
                                             value=False),
            callback=None,
            config_key=("ui", "autosave", self.__class__.__name__))
        dict.update(self.action_dict,
                    {self.m_auto_save_box.get_name(): self.m_auto_save_box})
        action = QAction("save into...")
        connect_direct(action.triggered, self.on_click_save_into)
        dict.update(self.action_dict, {action.text(): action})

    def auto_save(self):
        return self.m_auto_save_box.get_value()

    def get_json_file(self):
        return self.m_ui_file

    def save_into_json(self, json_path: str):
        if not os.path.exists(json_path):
            with open(json_path, "wt") as f:
                f.write("{}")
        with open(json_path, "rt") as f:
            json_dict: Dict = json.load(f)
        json_dict.update({self.__class__.__name__: self.to_json()})
        try:
            temp_path = os.path.join(QPSL_Temp_Directory,
                                     "ui.json").replace('\\', '/')
            with open(temp_path, "wt") as f:
                json.dump(json_dict, f, indent=4, sort_keys=True)
        except BaseException as e:
            raise e
        else:
            with open(json_path, "wt") as f:
                json.dump(json_dict, f, indent=4, sort_keys=True)

    def on_click_save_into(self):
        res = QFileDialog.getSaveFileName(
            None,
            directory=QPSL_Working_Directory,
            filter="json files(*.json)",
            options=QFileDialog.Option.DontConfirmOverwrite)
        if res[0]:
            self.save_into_json(json_path=res[0])
