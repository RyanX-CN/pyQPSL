from Tool import *

class ImageKPluginWorker(QPSLWorker):

    def tifs2tif(self,folder,name,downrate,outfolder=None,flipx=None,flipy=None):
        length = len(os.listdir(folder+'/'+name))
        shape_img = tifffile.imread(folder+'/'+name+'/'+name[:5]+'0.tif')
        #print()
        res = np.zeros([1,int(length/downrate),1,int(np.shape(shape_img)[0]/downrate),int(np.shape(shape_img)[1]/downrate),1])
        for i in range(int(length/downrate)):
            tmp = tifffile.imread(folder+'/'+name+'/'+name[:5]+str(i*downrate)+'.tif')[::downrate,::downrate]
            if flipx ==True:
                tmp = np.flip(tmp,axis=0)
            if flipy ==True:
                tmp = np.flip(tmp,axis=1)
            res[0,i,0,:,:,0] = tmp
            #print('\r',i,end = '')
        res = res.astype(np.uint16)
        if outfolder == None:
            tifffile.imwrite(folder+'/'+name+'.tif',res,bigtiff=True,imagej=True,metadata={'axes':'TZCYXS'})
        else:
            if not os.path.exists(folder+'/'+outfolder):
                os.mkdir(folder+'/'+outfolder)
            tifffile.imwrite(folder+'/'+outfolder+'/'+name+'.tif',res,bigtiff=True,imagej=True,metadata={'axes':'TZCYXS'})
        print(name+' done ')

class ImageKPluginUI(QPSLVFrameList,QPSLPluginBase):
    sig_image_show = pyqtSignal(str)

    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_logic()
        self.setup_style()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = ImageKPluginWorker().load_attr()

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
        self.view_image : QPSLScalePixmapLabel = self.findChild(QPSLScalePixmapLabel, "view_image")
        self.btn_image_folder : QPSLPushButton = self.findChild(QPSLPushButton, "btn_image_folder")
        self.btn_camera_folder : QPSLPushButton = self.findChild(QPSLPushButton, "btn_camera_folder")
        self.line_out_name : QPSLLineEdit = self.findChild(QPSLLineEdit, "line_out_name")
        self.sbox_down_sample : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_down_sample")
        self.cbox_flip_x : QPSLCheckBox = self.findChild(QPSLCheckBox, "cbox_flip_x")
        self.cbox_flip_y : QPSLCheckBox = self.findChild(QPSLCheckBox, "cbox_flip_y")
        self.btn_start_convert : QPSLPushButton = self.findChild(QPSLPushButton, "btn_start_convert")
    
    def setup_style(self):
        self.sbox_down_sample.setSpecialValueText("No")

    def setup_logic(self):
        self.get_named_widgets()
        connect_direct(self.btn_image_folder.sig_clicked,
                       self.choose_image_folder)
        connect_direct(self.btn_camera_folder.sig_clicked,
                       self.choose_camera_folder)
        connect_direct(self.sig_image_show,
                       self.first_image_show)
        connect_direct(self.btn_start_convert.sig_clicked,
                       self.start_convert)
    
    @QPSLObjectBase.log_decorator()
    def choose_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder != "":
            self.btn_image_folder.setText(folder)
        self.image_folder = folder

    @QPSLObjectBase.log_decorator()
    def choose_camera_folder(self):
        image_folder = self.image_folder
        folder = QFileDialog.getExistingDirectory(self, "Select Directory",image_folder)
        if folder != "":
            self.camera_folder = folder
            self.btn_camera_folder.setText(os.path.basename(folder))
        self.camera_folder = folder
        # self.sig_camera_floder.emit()
        self.sig_image_show.emit(folder)

    @QPSLObjectBase.log_decorator()
    def choose_out_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder != "":
            self.btn_out_folder.setText(folder)
        self.out_folder = folder

    @QPSLObjectBase.log_decorator()
    def first_image_show(self,folder_path):
        files = os.listdir(folder_path)
        tiff_files = [f for f in files if f.lower().endswith(('.tif', '.tiff'))]
        if not tiff_files:
            print("文件夹中没有找到TIFF图像文件")
        else:
            # 读取第一张TIFF图片
            first_tiff_path = os.path.join(folder_path, tiff_files[0])
            image = tifffile.imread(first_tiff_path)*20
            qimg = QImage(image.data,image.shape[1], image.shape[0],
                            image.shape[1] * 2, QImage.Format.Format_Grayscale16)
            pixmap = QPixmap.fromImage(qimg)
        self.view_image.setPixmap(pixmap)
    
    @QPSLObjectBase.log_decorator()
    def start_convert(self):
        folder = self.image_folder
        name = os.path.basename(self.camera_folder)
        out_file_name = self.line_out_name.text()
        downsamplerate = self.sbox_down_sample.value()
        if self.cbox_flip_x.isChecked():
            flipx = True
        else:
            flipx = False
        if self.cbox_flip_y.isChecked():
            flipy = True
        else:
            flipy = False
        self.m_worker.tifs2tif(folder=folder,name=name,downrate=downsamplerate,
                               outfolder=out_file_name,flipx=flipx,flipy=flipy)
MainWidget = ImageKPluginUI