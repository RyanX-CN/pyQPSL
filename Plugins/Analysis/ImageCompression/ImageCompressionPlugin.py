from Tool import *

class ImageCompression_Worker(QPSLWorker):
    sig_compression_start = pyqtSignal()
    sig_compression_finished = pyqtSignal()

    def __init__(self, image_path, algorithm):
        super().__init__()
        self.image_path = image_path
        self.algorithm = algorithm

    def compress(self):
        if self.algorithm == 'LZW':
            self.compress_with_lzw()
        elif self.algorithm == 'KLB':
            self.compress_with_klb()  # Placeholder for KLB algorithm
        else:
            raise ValueError("Unsupported algorithm selected")
        
    def decompress(self):
        pass

    pass

class ImageCompression_UI(QPSLHSplitter,QPSLPluginBase):
    pass