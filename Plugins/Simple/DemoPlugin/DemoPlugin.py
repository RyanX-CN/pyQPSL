from Tool import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .DemoAPI import *

'''
    This Plugin is for Test some function
'''

class DemoPluginWorker(QPSLWorker):
    
    def __init__(self):
        super().__init__()

    def load_attr(self):
        super().load_attr()
        self.m_test = DemoTest()