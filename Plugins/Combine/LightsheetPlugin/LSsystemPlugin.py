from Tool import *

#os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .LSsystemAPI import *

class LSsystemPluginWorker(QPSLWorker):
    pass

class LSsystemPluginUI(QPSLHFrameList,QPSLPluginBase):
    pass