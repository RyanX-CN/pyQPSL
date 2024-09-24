from Tool import *
from ...Simple.NIDAQmxAO.NIDAQmxAO import NIDAQmxAOPluginUI
from ...Simple.NIDAQmxDO.NIDAQmxDO import NIDAQmxDOPluginUI
from ...Simple.Stage_Thorlabs_MTS50.Stage_Thorlabs_MTS50 import Thorlabs_MTS50PluginUI
from PyQt5.QtCore import pyqtSignal


class NIDAQmxOutput_ThorlabsMTS50_PluginWorker(QPSLWorker):
    sig_task_started = pyqtSignal() 
    sig_task_stopped = pyqtSignal()

    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def to_delete(self):
        return super().to_delete()

    def setup_logic(self):
        pass


class NIDAQmxOutput_ThorlabsMTS50_PluginUI(QPSLVFrameList, QPSLPluginBase):

    class UIMode(enum.Enum):
        TabMode = 0
        CompositionMode = 1

    def load_by_json(self, _json: Dict):
        super().load_by_json(_json)
        ui_mode = _json.get("ui_mode")
        thorlabsmts50_json_path: str = _json.get("thorlabsmts50_json")
        nidaqmx_ao_json_path: str = _json.get("nidaqmx_ao_json")
        nidaqmx_do_json_path: str = _json.get("nidaqmx_do_json")
        tab_json: Dict = _json.get("tab_json")
        composition_json: Dict = _json.get("composition_json")
        if ui_mode is None:
            ui_mode = self.default_ui_mode()
        if thorlabsmts50_json_path is None:
            thorlabsmts50_json_path = self.default_thorlabsmts50_path()
        if nidaqmx_do_json_path is None:
            nidaqmx_do_json_path = self.default_nidaqmx_do_path()
        if nidaqmx_ao_json_path is None:
            nidaqmx_ao_json_path = self.default_nidaqmx_ao_path()

        with open(thorlabsmts50_json_path, "rt") as f:
            _json = json.load(f)
            self.thorlabsmts50_widget = Thorlabs_MTS50PluginUI()
            self.thorlabsmts50_widget.load_by_json(
                _json.get(Thorlabs_MTS50PluginUI.__name__))
        with open(nidaqmx_do_json_path, "rt") as f:
            _json = json.load(f)
            self.nidaqmx_do_widget = NIDAQmxDOPluginUI()
            self.nidaqmx_do_widget.load_by_json(
                _json.get(NIDAQmxDOPluginUI.__name__))
        with open(nidaqmx_ao_json_path, "rt") as f:
            _json = json.load(f)
            self.nidaqmx_ao_widget = NIDAQmxAOPluginUI()
            self.nidaqmx_ao_widget.load_by_json(
                _json.get(NIDAQmxAOPluginUI.__name__))
        self.m_ui_mode = ui_mode
        self.m_tab_json = tab_json
        self.m_composition_json = composition_json
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        if "widgets" in res:
            res.pop("widgets")
        if self.m_ui_mode != self.default_ui_mode():
            res.update({"ui_mode": self.m_ui_mode.name})
        res.update({"tab_json": self.m_tab_json})
        res.update({"composition_json": self.m_composition_json})
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = NIDAQmxOutput_ThorlabsMTS50_PluginWorker()
        self.m_ui_mode = self.default_ui_mode()
        self.m_tab_json = dict()
        self.m_composition_json = dict()
        self.m_ui_mode_box = SingleChoiceBox(name="ui mode", config_key=None)
        self.m_ui_mode_box.set_choice_list(
            choices=NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode._member_names_,
            callback=self.set_ui_mode)
        self.m_ui_mode_box.set_choice_as(choice=self.m_ui_mode.name,
                                         with_callback=False)
        dict.update(self.action_dict,
                    {self.m_ui_mode_box.get_name(): self.m_ui_mode_box})

    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self

    def to_delete(self):
        self.m_worker.stop_thread()
        self.m_worker.to_delete()
        self.thorlabsmts50_widget.to_delete()
        self.nidaqmx_do_widget.to_delete()
        self.nidaqmx_ao_widget.to_delete()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()

    def save_into_json(self, json_path: str):
        if self.m_ui_mode == NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode.TabMode:
            self.m_tab_json = self.get_widgets()[-1].to_json()
        else:
            self.m_composition_json = self.get_widgets()[-1].to_json()
        return super().save_into_json(json_path)

    @classmethod
    def default_ui_mode(cls):
        return NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode.TabMode

    @classmethod
    def default_thorlabsmts50_path(cls):
        return "{0}/Conf/ui.json".format(QPSL_Working_Directory)

    @classmethod
    def default_nidaqmx_do_path(cls):
        return "{0}/Conf/ui.json".format(QPSL_Working_Directory)

    @classmethod
    def default_nidaqmx_ao_path(cls):
        return "{0}/Conf/ui.json".format(QPSL_Working_Directory)

    @QPSLObjectBase.log_decorator()
    def get_named_widgets(self):
        self.thorlabsmts50_wrap: QPSLFrameWrap = self.findChild(
            QPSLFrameWrap, "thorlabsmts50_wrap")
        self.nidaqmx_do_wrap: QPSLFrameWrap = self.findChild(
            QPSLFrameWrap, "nidaqmx_do_wrap")
        self.nidaqmx_ao_wrap: QPSLFrameWrap = self.findChild(
            QPSLFrameWrap, "nidaqmx_ao_wrap")
        self.thorlabsmts50_wrap.set_inner_widget(widget=self.thorlabsmts50_widget)
        self.nidaqmx_do_wrap.set_inner_widget(widget=self.nidaqmx_do_widget)
        self.nidaqmx_ao_wrap.set_inner_widget(widget=self.nidaqmx_ao_widget)
        self.btn_init_total: QPSLPushButton = self.findChild(
            QPSLPushButton, "btn_init_total")
        self.btn_start_total: QPSLToggleButton = self.findChild(
            QPSLToggleButton, "btn_start_total")
        self.btn_reset_total: QPSLPushButton = self.findChild(
            QPSLPushButton, "btn_reset_total")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.m_worker.load_attr()
        self.set_ui_mode(self.m_ui_mode)
        self.m_worker.start_thread()
        #combined task
        connect_direct(self.btn_init_total.sig_clicked,
                       self.init_total_task)
        connect_direct(self.btn_start_total.sig_open,
                       self.start_total_task)
        connect_queued(self.m_worker.sig_task_started,
                       self.btn_start_total.set_opened)
        connect_direct(self.btn_start_total.sig_close,
                       self.stop_total_task)
        connect_queued(self.m_worker.sig_task_stopped,
                       self.btn_start_total.set_closed)
        connect_direct(self.btn_reset_total.sig_clicked,
                       self.reset_total_task)

    @QPSLObjectBase.log_decorator()
    def setup_tab_mode(self):
        self.m_ui_mode = NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode.TabMode
        self.m_ui_mode_box.set_choice_as(self.m_ui_mode.name, False)
        self.add_widget(widget=QPSLObjectBase.from_json(self.m_tab_json))
        self.get_named_widgets()

    @QPSLObjectBase.log_decorator()
    def setup_composition_mode(self):
        self.m_ui_mode = NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode.CompositionMode
        self.m_ui_mode_box.set_choice_as(self.m_ui_mode.name, False)
        self.add_widget(
            widget=QPSLObjectBase.from_json(self.m_composition_json))
        self.get_named_widgets()

    @QPSLObjectBase.log_decorator()
    def set_ui_mode(self, mode: Union['NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode',
                                      str]):
        if isinstance(mode, str):
            mode = NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode._member_map_[mode]
        if self.get_widgets():
            self.remove_widget_and_delete(self.get_widget(0))
        if mode == NIDAQmxOutput_ThorlabsMTS50_PluginUI.UIMode.TabMode:
            self.setup_tab_mode()
        else:
            self.setup_composition_mode()
    
    @QPSLObjectBase.log_decorator()
    def init_total_task(self):
        self.thorlabsmts50_widget.init_scan()
        self.nidaqmx_do_widget.on_click_init_task()
        self.nidaqmx_ao_widget.on_click_init_task()

    @QPSLObjectBase.log_decorator()
    def clear_total_task(self):
        pass
        
    @QPSLObjectBase.log_decorator()
    def start_total_task(self):
        self.thorlabsmts50_widget.start_scan()
        self.nidaqmx_do_widget.m_worker.on_start_task()
        self.nidaqmx_ao_widget.m_worker.on_start_task()
        self.m_worker.sig_task_started.emit()
        
    @QPSLObjectBase.log_decorator()
    def stop_total_task(self):
        self.thorlabsmts50_widget.m_worker.on_stop_scan()
        self.nidaqmx_do_widget.m_worker.on_stop_task()
        self.nidaqmx_ao_widget.m_worker.on_stop_task()
        self.m_worker.sig_task_stopped.emit()

    @QPSLObjectBase.log_decorator()
    def reset_total_task(self):
        self.thorlabsmts50_widget.m_worker.home_all()
        self.nidaqmx_do_widget.m_worker.reset()
        self.nidaqmx_ao_widget.m_worker.reset()


MainWidget = NIDAQmxOutput_ThorlabsMTS50_PluginUI