import subprocess

from QPSLClass.Base import *
from ..BaseClass import *
from ..UIClass.QPSLFrameList import QPSLVFrameList
from ..UIClass.QPSLLabel import QPSLLabel

class QPSLInitializationWindow(QPSLVFrameList, QPSLPluginBase):
    
    def __init__(self):
        super().__init__()
        self.get_current_branch_info()

    def load_attr(self):
        with open(QPSL_UI_Config_Path,"rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self
    
    def load_by_json(self, json: Dict):
        super().load_by_json(json)        
        self.setup_ui()
        self.setup_logic()
    
    def setup_ui(self):
        self.label_info: QPSLLabel = self.findChild(QPSLLabel, "label_info")
        self.label_info.setText(
            "\n  version: {0}\n  current Git branch: {1}\n  last Git commit time: {2}".format(
                self.version, self.git_branch, self.git_time))
    
    def setup_logic(self):
        return
    
    def get_current_branch_info(self):
        self.version = "{0}.{1}".format(init_config_get(keys=("version", "main_version")),
                init_config_get(keys=("version", "sub_version")))
        try:
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    check=True)
            self.git_branch = result.stdout.strip()
            result = subprocess.run(["git", "log", "-1", "--format=%cd", "--"],
                                     capture_output=True, 
                                     text=True)
            self.git_time = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while trying to get the current Git branch: {e.stderr}")
            return None

