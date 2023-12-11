from Tool import *
from ctypes import *

'''
    This Plugin is for Hamamatsu camera
'''

class HamamatsuCAMBase(QPSLWorker):
    pass

class HamamatsuCAMPluginWorker(QPSLWorker):
    def load_attr(self):
        super().load_attr()
        self.setup_logic()
        return self

    def to_delete(self):
        return super().to_delete()

    def setup_logic(self):
        pass

class HamamatsuCAMPluginUI(QPSLHFrameList,QPSLPluginBase):
    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_style()
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = HamamatsuCAMPluginWorker()

    def load_attr(self):
        with open(self.get_json_file(),"rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self
    
    def to_delete(self):
        self.m_worker.stop_thread()
        self.m_worker.to_delete()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()
    
    def get_named_widgets(self):
        pass

    def setup_style(self):
        pass
    
    def setup_logic(self):
        pass
