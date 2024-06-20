from Tool import *
from .CompressedSensingSystemAPI import *

class CompressedSensingSystemWorker(QPSLWorker):
    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def to_delete(self):
        return super().to_delete()

    def setup_logic(self):
        pass

class CompressedSensingSystemUI(QPSLVFrameList,QPSLPluginBase):
    
    class UIMode(enum.Enum):
        TabMode = 0
        CompositionMode = 1

    def __init__(self):
        super().__init__()
        self.m_worker = CompressedSensingSystemWorker().load_attr()
        self.m_shared_state = SharedStateController(
            value=SharedStateController.State.Stop)
    
    def load_attr(self):
        with open(self.get_json_file(), "rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self        

    def load_by_json(self, _json: Dict):
        super().load_by_json(_json)
        ui_mode = _json.get("ui_mode")
        if ui_mode is None:
            ui_mode = self.UIMode.TabMode
        self.ui_mode = ui_mode

        stage_thorlabs_json_path = os.path.join("Plugins/Simple/Stage_Thorlabs_MTS50/ui.json")
        cam_hamamatsu_json_path = os.path.join("Plugins/Simple/CAM_Hamamatsu/ui.json")
        
        with open(stage_thorlabs_json_path, "rt") as f:
            _json = json.load(f)
            self.stage_thorlabs_widget = Thorlabs_MTS50PluginUI()
            self.stage_thorlabs_widget.load_by_json(
                _json.get(Thorlabs_MTS50PluginUI.__name__))
        with open(cam_hamamatsu_json_path, "rt") as f:
            _json = json.load(f)
            self.cam_hamamatsu_widget = DoubleDCAMPluginUI()
            self.cam_hamamatsu_widget.load_by_json(
                _json.get(DoubleDCAMPluginUI.__name__))
        self.setup_logic()

    def setup_logic(self):
        pass

    def to_delete(self):
        self.stage_thorlabs_widget.to_delete()
        self.cam_hamamatsu_widget.to_delete()
        return super().to_delete()
    
    @QPSLObjectBase.log_decorator()
    def check_cam_state(self):
        pass

    
    

MainWidget = CompressedSensingSystemUI