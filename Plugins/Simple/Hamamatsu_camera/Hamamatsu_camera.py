import imagej
import napari

from ctypes import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QElapsedTimer
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor 
from datetime import datetime as dt
from itertools import cycle
# from nvidia import nvcomp

from Utils.Classes.QPSLMainWindow import device_status_controller,task_status_controller
from Tool import *

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .DCAMAPI import *

'''
    This Plugin is for controll Hamamatsu CMOS camera ORCA-Flash4.0 V3
'''
virtual_mode = True

TARGET_MIN = 0 
TARGET_MAX = 65535
SAVE_BATCH_SIZE = 100

class DCAMLiveWorker(QPSLWorker):
    '''
    Create a thread for living image
    '''
    sig_report_ndarray = pyqtSignal(np.ndarray)
    sig_report_pixmap = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.m_data_count = 1<<22
        self.m_data_shape = (2048,2048)
        self.m_image_id = 0
        self.m_live_flag = True
        self.m_save_flag = False
        self.m_downsample_rate = 5
        self.m_muti_ratio = 20
        self.m_data_queues = deque()
        # Integrate ImageJ
        # self.ij = imagej.init(mode='interactive')
        # self.ij.ui().showUI()
        self.image_ij = None

    def to_delete(self):
        return super().to_delete()

    @QPSLObjectBase.log_decorator()     
    def receive_data_from_cam(self, pointer_:np.uint64):
        data_ptr = int(pointer_)
        imagedata_ptr = ctypes.cast(data_ptr,c_ImageData_p).contents
        imagedata_ptr: ImageData
        # frame_id = imagedata_pointer.frame_id
        imagedata_host = np.frombuffer(imagedata_ptr.buffer, dtype=np.uint16, count=self.m_data_count)
        imagedata_host = np.reshape(imagedata_host,self.m_data_shape)
        imagedata_host = imagedata_host.astype(np.uint16)
        # =============== Emit ndarray data to save as TIFF file ===============
        if self.m_save_flag:
                self.sig_report_ndarray.emit(imagedata_host)
        self.m_image_id += 1
        # =============== Downsample data to show on UI ===============        
        if self.m_live_flag and self.m_image_id%self.m_downsample_rate == 0:
            # imagedata_host = imagedata_host[::2,::2]
            # imagedata_host = np.uint16(imagedata_host * self.m_muti_ratio[0])
            # qimg_cam = QImage(imagedata_host.data,imagedata_host.shape[1], imagedata_host.shape[0],
            #     imagedata_host.shape[1] * 2, QImage.Format.Format_Grayscale16)
            # pixmap_cam = QPixmap.fromImage(qimg_cam)
            # self.sig_report_pixmap.emit(pixmap_cam)
            image_j = self.ij.py.to_imageplus(imagedata_host)
            if image_ij is None:
                image_ij = image_j
                image_ij.show()
            else:
                image_ij.setProcessor(image_j.getProcessor())

            self.ij.IJ.run(image_ij, "Enhance Contrast", "saturated=0.35")
        
        data_ptr = ctypes.cast(data_ptr,c_void_p)
        Delete_Data_pointer(data_ptr)          
        
    @QPSLObjectBase.log_decorator()     
    def receive_virtual_data_from_cam(self, imagedata_host:np.ndarray):
        if self.m_save_flag:    
            self.sig_report_ndarray.emit(imagedata_host)
        self.m_image_id += 1
        if self.m_live_flag:
            # image_j = self.ij.py.to_imageplus(imagedata_host)
            # if self.image_ij is None:
            #     self.image_ij = image_j
            #     self.image_ij.show()
            # else:
            #     self.image_ij.setProcessor(image_j.getProcessor())
            # self.ij.IJ.run(self.image_ij, "Enhance Contrast", "saturated=0.35")
            # self.ij.IJ.run(self.image_ij, "Measure", "")
            # image_j.close()
            self.sig_report_ndarray.emit(imagedata_host)




    # @QPSLObjectBase.log_decorator()
    # def multiprocessing_handle_image(self):
    #     process = Process(target=self.receive_data_from_cam)
    #     process.start()

class DCAMSaveWorker(QPSLWorker):
    '''
    Create a thread for saving frame data TIF file
    '''
    sig_to_set_save_path = pyqtSignal(int)
    sig_single_round_save_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.m_save_flag:bool = False
        self.m_endframe = 0
        self.image_id = 0
        self.m_scan_round = 0
        self.m_save_path:str
        # self.m_save_buffer = np.empty((SAVE_BATCH_SIZE, 2048, 2048), dtype=np.uint16)
        # self.m_batch_number = 0
    
    def load_attr(self, index:int):
        super().load_attr()
        self.index = index
        self.setup_logic()
        return self
    
    def to_delete(self):
        return super().to_delete()
    
    def setup_logic(self):
        connect_direct(self.sig_to_set_save_path,
                       self.set_save_path)

    @QPSLObjectBase.log_decorator()            
    def set_save_path(self, suffix):
        # folder_name = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_CAM{0}_Round{1}".format(self.index,suffix))
        folder_name = str("CAM{0}_Round{1}".format(self.index,suffix))
        self.save_file_path = "{0}/{1}".format(self.m_save_path,folder_name)
        if not os.path.exists(self.save_file_path):
            os.mkdir(self.save_file_path)
    
    @QPSLObjectBase.log_decorator()    
    def save_tiff_file(self, data:np.ndarray):
        if self.m_save_flag == False:
            return
        tifffile.imwrite(self.save_file_path + "/CAM{0}_{1}.tif".format(self.index, self.image_id),
                       data)
        self.image_id += 1
        if self.image_id == self.m_endframe:
            # self.sig_single_round_save_done.emit()
            # shared_camsave_state.value = 1
            # print("shared_camsave_state",shared_camsave_state.value)
            if self.index == 0:
                shm_status_buf[0] = 1
            elif self.index == 1:
                shm_status_buf[1] = 1
            print("相机%d图像存储完成"%self.index,array.array('b',shm_status_buf))
            self.image_id = 0
        # =============== Save tiff files as batch ===============
        # self.m_save_buffer[self.m_index_image] = data
        # if self.m_index_image % SAVE_BATCH_SIZE == 0 or self.m_index_image == self.m_endframe:        
        #     tifffile.imwrite(self.save_file_path + "/CAM{0}_{1}.tif".format(self.index, self.m_batch_number), 
        #                     self.m_save_buffer)
        #     self.m_save_buffer[:] = 0
        #     self.m_batch_number  += 1
        # if self.m_index_image == self.m_endframe:
        #     self.m_index_image = 0
        #     self.m_save_flag = False

    @QPSLObjectBase.log_decorator()    
    def compress_data(self, data:np.ndarray, algo:str, comp_path:str):
        t0 = time.time()
        _bytes = data.tobytes()
        nvarr_d = nvcomp.as_array(_bytes)
        nvcodec = nvcomp.Codec(algorithm=algo)
        nvcomp_arr = nvcodec.encode(nvarr_d)
        t1 = time.time()
        with  open(comp_path+"/{0}.{1}".format(self.image_id, algo), "wb") as f:  
            f.write(nvcomp_arr.cpu())
        # print ("initial data size: %s bytes\n"%nvarr_d.shape[0],
        #     "compressed data size: %s bytes\n"%nvcomp_arr.shape[0],
        #     "compression ratio: %s\n"%(nvarr_d.shape[0]/nvcomp_arr.shape[0]))
        return  t1-t0

class DCAMCompressWorker(QPSLWorker):
    pass


class Hamamatsu_camera_Worker(QPSLWorker):
    '''
    Worker for camera operation tasks
    '''  
    sig_open_cam, sig_to_open_cam, sig_cam_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()    
    sig_close_cam, sig_to_close_cam, sig_cam_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_live_cam, sig_to_live_cam, sig_cam_lived = pyqtSignal(
    ), pyqtSignal(bool), pyqtSignal()
    sig_abort_cam, sig_to_abort_cam, sig_cam_aborted = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_setROI_cam, sig_to_setROI_cam = pyqtSignal(
        int, int, int, int), pyqtSignal(int, int, int, int)
    sig_set_trigger_dalay_cam, sig_to_set_trigger_delay_cam = pyqtSignal(
        float), pyqtSignal(float)
    sig_setExposuretime_cam, sig_to_setExposuretime_cam = pyqtSignal(
        float), pyqtSignal(float)
    sig_strat_scan_cam, sig_to_start_scan_cam, sig_scan_cam_started = pyqtSignal(int
    ), pyqtSignal(int), pyqtSignal()
    sig_single_round_scan_done = pyqtSignal(int)  
    sig_stop_scan_cam, sig_to_stop_scan_cam, sig_scan_cam_stopped = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_send_data_to_live = pyqtSignal(int, np.uint64)
    sig_send_virtual_data_to_live = pyqtSignal(np.ndarray)
    sig_refresh_frame_rate = pyqtSignal(float)
    sig_send_message = pyqtSignal(str,int)

    def __init__(self):
        super().__init__()
        self.m_continue_flag: bool = True
        # self.m_scan_continus_flag: bool = True
        self.m_scan_loop_flag: bool = False
        self.m_loop_round: int = 10
        self.m_timer_freq = QElapsedTimer()
        self.m_id = 0

    def load_attr(self, index:int):
        super().load_attr()
        self.is_virtual = True
        self.index = index
        cam_info = [c_void_p(),c_int(index)]
        self.m_cam = DCAMController(*cam_info)
        self.setup_logic()
        return self

    def to_delete(self):
        if self.m_cam.has_handle():
            # self.m_cam.buffer_release()
            self.m_cam.close_device()
        DCAMAPI_uninit()
        return super().to_delete()

    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_open_cam,self.sig_open_cam,
                                 self.on_open_cam)
        connect_asynch_and_synch(self.sig_to_close_cam,self.sig_close_cam,
                                 self.on_close_cam)
        connect_asynch_and_synch(self.sig_to_live_cam,self.sig_live_cam,
                                 self.on_live_cam)
        connect_asynch_and_synch(self.sig_to_abort_cam,self.sig_abort_cam,
                                 self.on_abort_cam)
        connect_asynch_and_synch(self.sig_to_start_scan_cam,self.sig_strat_scan_cam,
                                 self.on_scan_cam)
        connect_asynch_and_synch(self.sig_to_stop_scan_cam,self.sig_stop_scan_cam,
                                 self.on_stop_scan_cam)
        connect_asynch_and_synch(self.sig_to_setROI_cam,self.sig_setROI_cam,
                                 self.on_set_ROI_cam)
        connect_asynch_and_synch(self.sig_to_set_trigger_delay_cam,self.sig_set_trigger_dalay_cam,
                                 self.on_set_trigger_delay_cam)
        connect_asynch_and_synch(self.sig_to_setExposuretime_cam,self.sig_setExposuretime_cam,
                                 self.on_set_exposure_time_cam)
    
    @QPSLObjectBase.log_decorator()
    def  on_open_cam(self):
        self.m_cam.open_device()
        self.sig_cam_opened.emit()
        self.on_set_exposure_time_cam(10)
        self.on_set_trigger_positive_cam(True)
        self.sig_send_message.emit(
            "{0}\nCAM{1} OPENED".format(dt.now().time().replace(microsecond=0),self.index),1
            )
    
    @QPSLObjectBase.log_decorator()
    def on_close_cam(self):
        # self.m_cam0.buffer_release()
        self.m_cam.close_device()
        self.sig_cam_closed.emit()
        self.sig_send_message.emit(
            "{0}\nCAM{1} CLOSED".format(dt.now().time().replace(microsecond=0),self.index),1
            )
    
    @QPSLObjectBase.log_decorator()
    def on_get_deviceID_cam(self):
        self.ID_cam =c_char()
        err, self.ID_cam = self.m_cam.get_cameraID()
    
    @QPSLObjectBase.log_decorator()
    def on_get_temperature_cam(self):
        self.temp_cam = c_double()
        err, self.temp_cam = self.m_cam.get_temperature()
    
    @QPSLObjectBase.log_decorator()
    def on_live_cam(self, is_virtual:bool):
        self.m_continue_flag = True
        self.sig_cam_lived.emit()
        if is_virtual:
            self.sig_send_message.emit("virtual CAM is living",2)
            image_files = glob.glob('resources/virtual_data/*.tif')
            self.m_timer_freq.start()
            for image_file in cycle(image_files):
                QCoreApplication.instance().processEvents()
                if not self.m_continue_flag:
                    break
                imagedata_host = tifffile.imread(image_file)
                self.sig_send_virtual_data_to_live.emit(imagedata_host)
                sleep_for(10) # Adjust sleep time as needed
                elapsed_time = self.m_timer_freq.elapsed()
                self.sig_refresh_frame_rate.emit(elapsed_time/1000.0)  
        else:
            self.sig_send_message.emit(
                "{0}\nCAM{1} is living".format(dt.now().time().replace(microsecond=0),self.index),2
                )
            self.m_worker_self = py_object(self)
            self.m_cam.pre_live()
            self.m_timer_freq.start()
            while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag:
                QCoreApplication.instance().processEvents()
                self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                callback= Hamamatsu_camera_Worker.on_everyframe_callback)
                elapsed_time = self.m_timer_freq.elapsed()
                self.sig_refresh_frame_rate.emit(elapsed_time/1000.0)
            self.m_cam.post_live()
            self.sig_send_message.emit(
                "{0}\nCAM{1} aborted".format(dt.now().time().replace(microsecond=0),self.index),3
                )
        self.sig_cam_aborted.emit()
        # del self.m_worker_self

    @QPSLObjectBase.log_decorator()
    def on_abort_cam(self):
        self.m_continue_flag = False
        self.m_id = 0
        # self.m_cam.abort()
    
    @QPSLObjectBase.log_decorator()    
    def on_capture_cam(self, m_save_path):
        self.m_cam.save_path = c_char_p(m_save_path)
        self.m_cam.capture()
    
    @QPSLObjectBase.log_decorator()
    def on_set_ROI_cam(self, hpos:int, vpos:int, hsize:int, vsize:int):
        self.m_cam.set_ROI(hpos,vpos,hsize,vsize)
        self.m_x0 = hpos
        self.m_y0 = vpos
        self.m_width = hsize
        self.m_height = vsize
        self.sig_send_message.emit(
            "{0}\nCAM{1} set ROI:{2}".format(dt.now().time().replace(microsecond=0),self.index,(hpos,vpos,hsize,vsize)),1
            )
   
    @QPSLObjectBase.log_decorator()
    def on_set_exposure_time_cam(self, exposure_time:float):
        self.m_cam.set_exposure_time(exposure_time/1000) #msec

    @QPSLObjectBase.log_decorator()
    def on_set_internal_trigger_cam(self):
        self.m_cam.set_internal_trigger()
        self.sig_send_message.emit(
            "{0}\nCAM{1} set internal trigger".format(dt.now().time().replace(microsecond=0),self.index),1
            )

    @QPSLObjectBase.log_decorator()
    def on_set_external_trigger_cam(self):
        self.m_cam.set_external_trigger()
        self.sig_send_message.emit(
            "{0}\nCAM{1} set external trigger".format(dt.now().time().replace(microsecond=0),self.index),1
            )

    @QPSLObjectBase.log_decorator()
    def on_set_syncreadout_cam(self):
        self.m_cam.set_syncreadout()
        self.sig_send_message.emit(
            "{0}\nCAM{1} set syncreadout".format(dt.now().time().replace(microsecond=0),self.index),1
            )

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_positive_cam(self, polarity:bool):
        self.m_cam.set_trigger_positive()
        self.sig_send_message.emit(
            "{0}\nCAM{1} set trigger positive".format(dt.now().time().replace(microsecond=0),self.index),1
            )

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_negative_cam(self, polarity:bool):
        self.m_cam.set_trigger_negative()
        self.sig_send_message.emit(
            "{0}\nCAM{1} set trigger negative".format(dt.now().time().replace(microsecond=0),self.index),1
            )

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_delay_cam(self, trigger_delay:float):
        self.m_cam.set_trigger_delay(trigger_delay)

    @QPSLObjectBase.log_decorator()
    def on_scan_cam(self,endframe:int):
        self.m_continue_flag = True
        if not self.m_scan_loop_flag:
            # self.m_continue_flag = True
            self.m_worker_self = py_object(self)
            # self.add_warning("Camera {0} is scaning".format(self.index))
            self.sig_send_message.emit(
                "{0}\nCAM{1} is scaning".format(dt.now().time().replace(microsecond=0),self.index),2
                )
            self.m_cam.pre_live()
            while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag and self.m_id < endframe:
                QCoreApplication.instance().processEvents()
                self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                callback= Hamamatsu_camera_Worker.on_everyframe_callback)
            self.m_cam.post_live()
        else:
            self.sig_send_message.emit(
                "{0}\nCAM{1} is scaning(Loop)".format(dt.now().time().replace(microsecond=0),self.index),2
                )
            # self.m_continue_flag = True
            for i in range(self.m_loop_round):
                QCoreApplication.instance().processEvents()
                self.m_id = 0
                self.m_worker_self = py_object(self)
                self.sig_send_message.emit(
                "{0}\nCAM{1} round{2} scan START".format(dt.now().time().replace(microsecond=0),self.index,i),2
                    )
                self.m_cam.pre_live()
                for j in range(endframe):
                    QCoreApplication.instance().processEvents()
                    self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                    callback= Hamamatsu_camera_Worker.on_everyframe_callback)
                self.m_cam.post_live()
                self.sig_send_message.emit(
                "{0}\nCAM{1} round{2} scan DONE".format(dt.now().time().replace(microsecond=0),self.index,i),2)
                print("相机%d扫描完成"%self.index, array.array('b',shm_status_buf))
                if shm_device_buf[2]: # Thorlabs stages is opened
                    if shm_device_buf[0] and not shm_device_buf[1]:# Only cam0 opened
                        while not shm_status_buf[0] or not shm_status_buf[2]:
                            print("相机%d等待上轮采集完成ing"%self.index, array.array('b',shm_status_buf))
                    elif not shm_device_buf[0] and shm_device_buf[1]:# Only cam1 opened
                        while not shm_status_buf[1] or not shm_status_buf[2]:
                            print("相机%d等待上轮采集完成ing"%self.index, array.array('b',shm_status_buf))                 
                    elif shm_device_buf[0] and shm_device_buf[1]: # Both cam are opened
                        while not shm_status_buf[0] or not shm_status_buf[1] or not shm_status_buf[2]:
                            print("双相机等待上轮采集完成ing", array.array('b',shm_status_buf))
                # sleep_for(15000)
                if i != self.m_loop_round-1:
                    self.sig_single_round_scan_done.emit(i+1)
        self.sig_send_message.emit(
            "{0}\nCAM{1} scan DONE".format(dt.now().time().replace(microsecond=0),self.index),3)                              
    
    @QPSLObjectBase.log_decorator()
    def on_stop_scan_cam(self):
        self.m_continue_flag = False
        # self.m_scan_continus_flag = False    
        self.m_scan_loop_flag = False
        self.m_id = 0
    
    @ctypes.WINFUNCTYPE(c_int32,c_void_p,c_void_p)
    def on_everyframe_callback(self:c_void_p,
                         data:c_void_p):    
        self = ctypes.cast(self, POINTER(py_object)).contents.value
        self: Hamamatsu_camera_Worker
        # self.add_warning("cam = {0}, img = {1}".format(self.index,self.m_id))
        ctypes.cast(data,c_ImageData_p).contents.frame_id = self.m_id
        self.m_id += 1
        data = np.uint64(data)
        # print(self.m_cam.bufframe.width,self.m_cam.bufframe.height,self.m_cam.bufframe.rowbytes)
        # if self.m_debug:
        #     pass
        self.sig_send_data_to_live.emit(self.index, data)
        # self.sig_send_data_to_save.emit(data)
        return 0


class Hamamatsu_camera_PluginUI(QPSLHSplitter,QPSLPluginBase):
    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_style()
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.is_virtual = True
        self.m_cam_worker = Hamamatsu_camera_Worker().load_attr(0)
        self.m_live_worker = DCAMLiveWorker().load_attr()
        self.m_save_worker = DCAMSaveWorker().load_attr(0)
        self.m_time_queue = [deque(), deque()]
        # Integrate napari
        self.viewer = napari.Viewer()
        self.image_layer = None

    def load_attr(self):
        with open(self.get_json_file(),"rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self
    
    def to_delete(self):
        self.m_cam_worker.stop_thread()
        self.m_cam_worker.to_delete()
        self.m_live_worker.stop_thread()
        self.m_live_worker.to_delete()
        self.m_save_worker.stop_thread()
        self.m_save_worker.to_delete()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()
    
    def get_named_widgets(self):        
        self.btn_init_API : QPSLPushButton = self.findChild(QPSLPushButton, "btn_init_API")
        self.btn_uninit_API : QPSLPushButton = self.findChild(QPSLPushButton, "btn_uninit_API")
        self.cbox_none_view : QPSLCheckBox = self.findChild(QPSLCheckBox, "cbox_none_view")
        self.cbox_view_with_napari : QPSLCheckBox = self.findChild(QPSLCheckBox, "cbox_view_with_napari")
        self.cbox_view_with_imagej : QPSLCheckBox = self.findChild(QPSLCheckBox, "cbox_view_with_imagej")
        self.btn_open_cam0 : QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_open_cam0")
        self.btn_live_cam0 : QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_live_cam0")
        self.btn_capture_cam0 : QPSLPushButton = self.findChild(QPSLPushButton, "btn_capture_cam0")
        self.label_device_cam0 : QPSLLabel = self.findChild(QPSLLabel, "label_device_cam0")
        self.label_temperature_cam0 : QPSLLabel = self.findChild(QPSLLabel, "label_temperature_cam0")
        self.label_framerate_cam0 : QPSLLabel = self.findChild(QPSLLabel, "label_framerate_cam0")
        self.sbox_x0_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_x0_cam0")
        self.sbox_width_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_width_cam0")
        self.sbox_y0_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_y0_cam0")
        self.sbox_height_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_height_cam0")
        self.btn_applyROI_cam0 : QPSLPushButton = self.findChild(QPSLPushButton, "btn_applyROI_cam0")
        self.cbox_trigger_cam0 : QPSLComboBox = self.findChild(QPSLComboBox, "cbox_trigger_cam0")
        self.btn_trigger_positive_cam0 : QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_positive_cam0")
        self.btn_trigger_negative_cam0 : QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_negative_cam0")
        self.sbox_trigger_delay_cam0 : QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_trigger_delay_cam0")
        self.sbox_exposure_time_cam0 : QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_exposure_time_cam0")
        self.btn_scan_continous_cam0 : QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_continous_cam0")
        self.btn_scan_loop_cam0 : QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_loop_cam0")
        self.frame_loop_setting : QPSLVFrameList = self.findChild(QPSLVFrameList, "frame_loop_setting")
        self.sbox_scan_endframe_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_scan_endframe_cam0")
        self.sbox_scan_loop_cam0 : QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_scan_loop_cam0")
        self.cbox_compress_method : QPSLComboBox = self.findChild(QPSLComboBox, "cbox_compress_method")
        self.line_path_cam0 : QPSLLineEdit = self.findChild(QPSLLineEdit, "line_path_cam0")
        self.btn_path_cam0 : QPSLPushButton = self.findChild(QPSLPushButton, "btn_path_cam0")
        self.btn_start_scan_cam0 : QPSLPushButton = self.findChild(QPSLPushButton, "btn_start_scan_cam0")
        self.btn_stop_scan_cam0 : QPSLPushButton = self.findChild(QPSLPushButton, "btn_stop_scan_cam0")
        self.camview_DCAM : QPSLCameraView = self.findChild(QPSLCameraView, "camview_DCAM")     
        
    def setup_style(self):
        self.get_named_widgets()
        self.view_choice_group = QtWidgets.QButtonGroup(self)
        self.view_choice_group.addButton(self.cbox_none_view)
        self.view_choice_group.addButton(self.cbox_view_with_napari)
        self.view_choice_group.addButton(self.cbox_view_with_imagej)
        self.cbox_none_view.setChecked(True)
        self.cbox_trigger_cam0.addItems(["Internal","External","Syncreadout"])
        self.scan_radiobuttongroup1 = QtWidgets.QButtonGroup(self)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_continous_cam0)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_loop_cam0)
        self.btn_scan_continous_cam0.setChecked(True)
        if self.btn_scan_continous_cam0.isChecked():
            self.frame_loop_setting.hide()
        self.line_path_cam0.setText("E:/Custom_Control_Software/Test")
        for btn in self.btn_after_API_init:
            btn.setDisabled(True)
        # self.viewer = napari.Viewer()
        # self.camview_DCAM.addSubWindow(self.viewer.window.qt_viewer)  

    
    def setup_logic(self):
        # self.get_named_widgets()
        # self.m_worker_cam0.load_attr()
        self.timer_temp_1 = QTimer(self)
        self.timer_temp_2 = QTimer(self)
        # connect_direct(self.tab_view.sig_index_changed_to,
        #                self.on_show_difference)
        '''============================================= DCAM-API ============================================='''
        connect_direct(self.btn_init_API.sig_clicked,
                       self.init_API)
        connect_direct(self.btn_uninit_API.sig_clicked,
                       self.uninit_API)
        '''============================================= CAMERA 0 ============================================='''
        connect_queued(self.m_cam_worker.sig_send_message,
                       self.add_log_message)
        # Open/Close  
        connect_direct(self.btn_open_cam0.sig_open,
                       self.on_click_open_cam0)
        connect_queued(self.m_cam_worker.sig_cam_opened,
                       self.btn_open_cam0.set_opened)
        connect_direct(self.timer_temp_1.timeout,
                       self.refresh_temperature_cam0)
        connect_direct(self.btn_open_cam0.sig_close,
                       self.on_click_close_cam0)
        connect_queued(self.m_cam_worker.sig_cam_closed,
                       self.btn_open_cam0.set_closed)
        # Capture
        connect_direct(self.btn_capture_cam0.sig_clicked,
                       self.on_click_capture_cam0)
        # Live/Abort
        connect_queued(self.cbox_view_with_napari.clicked,
                       self.camview_DCAM.startup_napari)
        connect_direct(self.btn_live_cam0.sig_open,
                       self.on_click_live_cam0)
        connect_queued(self.m_cam_worker.sig_cam_lived,
                       self.btn_live_cam0.set_opened)
        connect_queued(self.m_cam_worker.sig_send_data_to_live,
                       self.m_live_worker.receive_data_from_cam)
        connect_queued(self.m_cam_worker.sig_send_virtual_data_to_live,
                       self.m_live_worker.receive_virtual_data_from_cam)  
        connect_queued(self.m_live_worker.sig_report_pixmap,
                       self.refresh_live_view1)
        connect_direct(self.btn_live_cam0.sig_close,
                       self.on_click_abort_cam0)    
        connect_queued(self.m_cam_worker.sig_cam_aborted,
                       self.btn_live_cam0.set_closed)
        # connect_queued(self.view_cam0.sbox_ratio_1.sig_value_changed_to,
        #                self.on_change_live_ratio_cam0)
        connect_queued(self.m_cam_worker.sig_refresh_frame_rate,
                       self.refresh_framerate_cam0)
        # Scan/Stop
        connect_direct(self.btn_start_scan_cam0.sig_clicked,
                       self.on_clicked_scan_cam0)
        # connect_queued(self.m_live_worker.sig_report_ndarray,
        #                self.m_save_worker.save_tiff_file)
        connect_queued(self.m_live_worker.sig_report_ndarray,
                       self.refresh_napari)
        connect_direct(self.btn_stop_scan_cam0.sig_clicked,
                       self.on_clicked_stop_cam0)
        connect_queued(self.m_cam_worker.sig_single_round_scan_done,
                       self.m_save_worker.set_save_path)
        # Setting
        connect_direct(self.btn_applyROI_cam0.sig_clicked,
                       self.on_click_setROI_cam0)
        connect_direct(self.cbox_trigger_cam0.activated,
                       self.on_change_trigger_cam0)
        connect_queued(self.btn_trigger_positive_cam0.clicked,
                       self.m_cam_worker.on_set_trigger_positive_cam)
        connect_queued(self.btn_trigger_negative_cam0.clicked,
                       self.m_cam_worker.on_set_trigger_negative_cam)
        connect_direct(self.sbox_trigger_delay_cam0.sig_value_changed,
                       self.on_change_trigger_delay_cam0)     
        connect_direct(self.sbox_exposure_time_cam0.sig_value_changed,
                       self.on_change_Exposuretime_cam0)
        connect_direct(self.btn_path_cam0.clicked,
                       self.choose_path_cam0)
        '''============================================= CAMERA 1 ============================================='''
        # connect_queued(self.m_worker_cam1.sig_send_message,
        #                self.add_log_message)
        # # Open/Close       
        # connect_direct(self.btn_open_cam1.sig_open,
        #                self.on_click_open_cam1)
        # connect_queued(self.m_worker_cam1.sig_cam_opened,
        #                self.btn_open_cam1.set_opened)
        # connect_direct(self.timer_temp_2.timeout,
        #                self.refresh_temperature_cam1)
        # connect_direct(self.btn_open_cam1.sig_close,
        #                self.on_click_close_cam1)
        # connect_queued(self.m_worker_cam1.sig_cam_closed,
        #                self.btn_open_cam1.set_closed)
        # # Capture
        # connect_direct(self.btn_capture_cam1.sig_clicked,
        #                self.on_click_capture_cam1)
        # # Live/Abort      
        # connect_direct(self.btn_live_cam1.sig_open,
        #                self.on_click_live_cam1)
        # connect_queued(self.m_worker_cam1.sig_cam_lived,
        #                self.btn_live_cam1.set_opened)
        # connect_queued(self.m_worker_cam1.sig_cam_aborted,
        #                self.btn_live_cam1.set_closed)
        # connect_queued(self.m_worker_cam1.sig_send_data_to_live,
        #                self.m_live_worker.receive_data_from_cam)  
        # connect_queued(self.m_live_worker.sig_report_pixmap_cam1,
        #                self.refresh_live_view2)
        # connect_direct(self.btn_live_cam1.sig_close,
        #                self.on_click_abort_cam1)    
        # connect_queued(self.m_worker_cam1.sig_cam_aborted,
        #                self.btn_live_cam1.set_closed)
        # connect_direct(self.view_cam1.sbox_ratio_1.sig_value_changed_to,
        #                self.on_change_live_ratio_cam1)
        # connect_queued(self.m_worker_cam1.sig_refresh_frame_rate,
        #                self.refresh_framerate_cam1)
        # # Scan/Stop      
        # connect_direct(self.btn_start_scan_cam1.sig_clicked,
        #                self.on_clicked_scan_cam1)
        # connect_queued(self.m_live_worker.sig_report_ndarray_cam1,
        #                self.m_save_worker_cam1.save_tiff_file)
        # connect_direct(self.btn_stop_scan_cam1.sig_clicked,
        #                self.on_clicked_stop_cam1)
        # connect_queued(self.m_worker_cam1.sig_single_round_scan_done,
        #                self.m_save_worker_cam1.set_save_path)
        # # Setting       
        # connect_direct(self.btn_applyROI_cam1.sig_clicked,
        #                self.on_click_setROI_cam1)
        # connect_direct(self.cbox_trigger_cam1.activated,
        #                self.on_change_trigger_cam1)
        # connect_queued(self.btn_trigger_positive_cam1.clicked,
        #                self.m_worker_cam1.on_set_trigger_positive_cam)
        # connect_queued(self.btn_trigger_negative_cam1.clicked,
        #                self.m_worker_cam1.on_set_trigger_negative_cam)
        # connect_direct(self.sbox_trigger_delay_cam1.sig_value_changed,
        #                self.on_change_trigger_delay_cam1)        
        # connect_direct(self.sbox_exposure_time_cam1.sig_value_changed,
        #                self.on_change_Exposuretime_cam1)
        # connect_direct(self.btn_path_cam1.clicked,
        #                self.choose_path_cam1)

        # connect_direct(self.view_combined.sbox_ratio_1.sig_value_changed_to,
        #                self.on_change_live_ratio_cam0)
        # connect_direct(self.view_combined.sbox_ratio_2.sig_value_changed_to,
        #                self.on_change_live_ratio_cam1)
        # connect_queued(self.m_live_worker.sig_report_pixmap_difference,
        #                self.refresh_live_view_difference)
        
        self.m_cam_worker.start_thread()
        self.m_live_worker.start_thread()
        self.m_save_worker.start_thread()

    '''============================================= CAMERA 0 =============================================''' 
    @QPSLObjectBase.log_decorator()
    def on_click_open_cam0(self):
        if self.is_virtual:
            self.add_log_message("CAM opened under virtual mode",2)
            device_status_controller.set_device_opened('dcam_virtual')
        else:
            self.m_cam_worker.sig_to_open_cam.emit()
            sleep_for(1000)
            self.on_set_deviceID_cam0()
            self.timer_temp_1.start(1000)
            device_status_controller.set_device_opened('dcam')
        
        for btn in self.btn_after_cam0_opened:
            btn.setEnabled(True)

    @QPSLObjectBase.log_decorator()
    def on_click_close_cam0(self):
        if self.is_virtual:
            self.add_log_message("CAM closed under virtual mode",2)
            device_status_controller.set_device_closed('dcam_virtual')
        else:
            self.m_cam_worker.sig_to_open_cam.emit()
            self.timer_temp_1.stop()
            self.label_device_cam0.clear()
            self.label_temperature_cam0.clear()
            self.label_framerate_cam0.clear()
            device_status_controller.set_device_closed('dcam')

        for btn in self.btn_after_cam0_opened:
            btn.setDisabled(True)

    @QPSLObjectBase.log_decorator()
    def on_click_live_cam0(self):
        self.m_live_worker.m_live_flag = True
        self.m_live_worker.m_save_flag = False
        self.m_cam_worker.sig_to_live_cam.emit(self.is_virtual)
    
    @QPSLObjectBase.log_decorator()
    def on_change_live_ratio_cam0(self, ratio:float):
        self.m_live_worker.m_muti_ratio[0] = ratio

    @QPSLObjectBase.log_decorator()
    def refresh_live_view1(self, cam0_image:QPixmap):
        self.view_cam0.on_show_pixmap(cam0_image)

    @QPSLObjectBase.log_decorator()
    def on_click_abort_cam0(self):
        self.m_cam_worker.sig_to_abort_cam.emit()
        sleep_for(500)
        self.m_time_queue[0].clear()

    @QPSLObjectBase.log_decorator()
    def on_click_capture_cam0(self):
        m_save_path = self.line_path_cam0.text()
        if m_save_path == "":
            m_save_path = "E:/Custom_Control_Software/Test"
        m_file_name = "CAM0_" + dt.now().strftime("%Y%m%d_%H%M%S")
        m_file_path = "{0}/{1}".format(m_save_path, m_file_name).encode('utf-8')
        self.m_cam_worker.on_capture_cam(m_file_path)

    @QPSLObjectBase.log_decorator()
    def on_set_deviceID_cam0(self):
        self.m_cam_worker.on_get_deviceID_cam()
        self.label_device_cam0.setText("Device: " + self.m_cam_worker.ID_cam.value.decode("utf-8").replace("\\","/"))
    
    # @QPSLObjectBase.log_decorator()
    def refresh_temperature_cam0(self):
        self.m_cam_worker.on_get_temperature_cam()
        self.label_temperature_cam0.setText("Temperature: " + str(self.m_cam_worker.temp_cam.value))

    @QPSLObjectBase.log_decorator()
    def refresh_framerate_cam0(self,current_frame_time:float):
            self.m_time_queue[0].append(current_frame_time)
            while self.m_time_queue[0][-1] - 2 >= self.m_time_queue[0][0]:
                self.m_time_queue[0].popleft()
            self.label_framerate_cam0.setText("Framerate: " + str(len(self.m_time_queue[0])/2))
    
    @QPSLObjectBase.log_decorator()
    def on_click_setROI_cam0(self):        
        self.m_live_worker.m_data_count[0] = self.sbox_width_cam0.value() * self.sbox_height_cam0.value()
        self.m_live_worker.m_data_shape[0] = (self.sbox_height_cam0.value(),self.sbox_width_cam0.value())
        # self.m_save_worker_cam0.m_save_buffer = np.empty((SAVE_BATCH_SIZE,self.sbox_width_cam0.value(),self.sbox_height_cam0.value()), dtype=np.uint16)
        self.m_cam_worker.sig_to_setROI_cam.emit(self.sbox_x0_cam0.value(),
                                              self.sbox_y0_cam0.value(),
                                              self.sbox_width_cam0.value(),
                                              self.sbox_height_cam0.value())

    @QPSLObjectBase.log_decorator()
    def on_change_trigger_cam0(self, trigger_type:str):
        if self.cbox_trigger_cam0.currentText() == "Internal":
            self.m_cam_worker.on_set_internal_trigger_cam()
        elif self.cbox_trigger_cam0.currentText() == "External":
            self.m_cam_worker.on_set_external_trigger_cam()
        elif self.cbox_trigger_cam0.currentText() == "Syncreadout":
            self.m_cam_worker.on_set_syncreadout_cam()
        # self.add_log_message("DCAM_1({0}) set {1}".format(self.m_worker_cam0.ID_cam.value.decode("utf-8"), self.cbox_trigger_cam0.currentText()))
    
    @QPSLObjectBase.log_decorator()
    def on_change_trigger_delay_cam0(self):
        self.m_cam_worker.sig_to_set_trigger_delay_cam.emit(self.sbox_trigger_delay_cam0.value())

    @QPSLObjectBase.log_decorator()
    def on_change_Exposuretime_cam0(self):
        self.m_cam_worker.sig_to_setExposuretime_cam.emit(self.sbox_exposure_time_cam0.value())

    @QPSLObjectBase.log_decorator()
    def on_clicked_scan_cam0(self):
        if not self.m_live_worker.m_save_flag:
            self.m_live_worker.m_save_flag = True
        self.m_save_worker.m_save_flag = True
        self.m_save_worker.image_id = 0
        self.m_live_worker.m_live_flag = False
        if self.btn_scan_continous_cam0.isChecked():
            endframe = 50000
        elif self.btn_scan_endframe_cam0.isChecked():
            endframe = self.sbox_scan_endframe_cam0.value()
            self.m_cam_worker.m_scan_loop_flag = False
        elif self.btn_scan_loop_cam0.isChecked():
            endframe = self.sbox_scan_endframe_cam0.value()
            loop_round = self.sbox_scan_loop_cam0.value()
            self.m_cam_worker.m_scan_loop_flag = True
            self.m_cam_worker.m_loop_round = loop_round
        self.m_save_worker.m_endframe = endframe
        self.m_save_worker.m_save_path = self.line_path_cam0.text()
        self.m_save_worker.sig_to_set_save_path.emit(0)
        sleep_for(100)
        self.m_cam_worker.sig_to_start_scan_cam.emit(endframe)

    @QPSLObjectBase.log_decorator()
    def on_clicked_stop_cam0(self):
        self.m_cam_worker.sig_to_stop_scan_cam.emit()
        self.m_save_worker.m_save_flag = False
        if self.m_live_worker.m_save_flag:
            self.m_live_worker.m_save_flag = False

    @QPSLObjectBase.log_decorator()
    def choose_path_cam0(self, event):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder",'./')
        self.line_path_cam0.setText(folder_path)
    
    '''============================================= Global =============================================''' 
    @QPSLObjectBase.log_decorator()    
    def init_API(self):
        if self.is_virtual:
            self.add_log_message("Init under virtual mode",2)
        else:
            DCAMAPI_init()
            self.add_log_message("DCAM_API init Done",2)

        self.btn_open_cam0.setEnabled(True)
        self.btn_init_API.setDisabled(True)
        self.btn_uninit_API.setEnabled(True)
    
    @QPSLObjectBase.log_decorator()
    def uninit_API(self):
        if self.is_virtual:
            self.add_log_message("Uninit under virtual mode",2)
        else:
            DCAMAPI_init()
            self.add_log_message("DCAM_API uninit Done",2)
        DCAMAPI_uninit()

        for btn in self.btn_after_API_init:
            btn.setDisabled(True)
        self.btn_init_API.setEnabled(True)
        self.btn_uninit_API.setDisabled(True)

    @QPSLObjectBase.log_decorator()
    def add_log_message(self,log_message:str,level:int):
        # charformat = QTextCharFormat()
        # if level == 0:
        #     charformat.setForeground(QColor("black"))
        # elif level ==1:
        #     charformat.setForeground(QColor("green"))
        # elif level ==2:
        #     charformat.setForeground(QColor("blue"))
        # elif level ==3:
        #     charformat.setForeground(QColor("red"))
        # self.text_logger.moveCursor(QTextCursor.End)
        # cursor = self.text_logger.textCursor()
        # cursor.insertText(log_message+"\n",charformat)
        pass

    @QPSLObjectBase.log_decorator()
    def refresh_napari(self, cam_image:np.ndarray):
        if self.image_layer is None or 'cam_image' not in self.camview_DCAM.napari.layers:
            self.image_layer = self.camview_DCAM.napari.add_image(cam_image)
        else:
            self.image_layer.data = cam_image

    @QPSLObjectBase.log_decorator()
    def refresh_live_view_difference(self, cam_image_difference:QPixmap):
        self.view_combined.on_show_pixmap(cam_image_difference)
    
    @QPSLObjectBase.log_decorator()
    def on_show_difference(self,index:int):
        if index == 0:
            self.m_live_worker.m_difference_flag = False
        elif index == 1:
            self.m_live_worker.m_difference_flag = True
    
    @property    
    def btn_after_API_init(self) -> Iterable[QPSLPushButton]:
        return(self.btn_uninit_API,
               self.btn_open_cam0, 
               self.btn_live_cam0, 
               self.btn_capture_cam0, 
               self.btn_applyROI_cam0,
               self.cbox_trigger_cam0,
               self.sbox_trigger_delay_cam0,
               self.sbox_exposure_time_cam0,
               self.btn_start_scan_cam0, 
               self.btn_stop_scan_cam0)
    
    @property
    def btn_after_cam0_opened(self) -> Iterable[QPSLPushButton]:
        return(self.btn_live_cam0,
               self.btn_capture_cam0,
               self.btn_applyROI_cam0,
               self.cbox_trigger_cam0,
               self.sbox_trigger_delay_cam0,
               self.sbox_exposure_time_cam0,
               self.btn_start_scan_cam0,
               self.btn_stop_scan_cam0)
        

MainWidget = Hamamatsu_camera_PluginUI