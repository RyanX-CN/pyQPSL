from Tool import *
from ctypes import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QElapsedTimer
from PyQt5.QtGui import QTextCursor
from datetime import datetime

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .DCAMAPI import *

'''
    This Plugin is for controll 2 Hamamatsu CMOS camera ORCA-Flash4.0 V3
'''

TARGET_MIN = 0 
TARGET_MAX = 65535

class DCAMLiveWorker(QPSLWorker):
    '''
    Create a thread for living image
    '''
    sig_report_ndarray_cam1 = pyqtSignal(np.ndarray)
    sig_report_ndarray_cam2 = pyqtSignal(np.ndarray)
    sig_report_pixmap_cam1 = pyqtSignal(QPixmap)
    sig_report_pixmap_cam2 = pyqtSignal(QPixmap)
    sig_report_ndarray_difference = pyqtSignal(np.ndarray)
    sig_report_pixmap_difference = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.m_data_count = [1<<22]*2
        self.m_data_shape = [(2048,2048)]*2
        self.m_save_flag = False
        self.m_id_image = [0]*2
        self.m_live_flag = True
        self.m_downsample_rate = 6
        self.m_muti_ratio = [20]*2
        self.m_mirror_cam2 = bool
        self.m_difference_flag = False
        self.m_data_queues = [deque(), deque()]

    def to_delete(self):
        return super().to_delete()

    @QPSLObjectBase.log_decorator()     
    def receive_data_from_cam(self, index:int, data_cam:np.uint64):
        data_cam = int(data_cam)
        imagedata_cam = ctypes.cast(data_cam,c_ImageData_p).contents
        imagedata_cam: ImageData
        # frame_id = imagedata_cam.frame_id
        framebuffer_cam = np.frombuffer(imagedata_cam.buffer, dtype=np.uint16, count=self.m_data_count[index])
        framebuffer_cam = np.reshape(framebuffer_cam,self.m_data_shape[index])
        framebuffer_cam = framebuffer_cam.astype(np.uint16)
        # =============== Emit ndarray data to save as TIF file ===============
        if self.m_save_flag:
            if index == 0:
                self.sig_report_ndarray_cam1.emit(framebuffer_cam)
            elif index == 1:
                self.sig_report_ndarray_cam2.emit(framebuffer_cam)
        self.m_id_image[index] += 1
        # =============== Downsample data to show on UI ===============
        if self.m_live_flag:
            if self.m_id_image[index]%self.m_downsample_rate == 0:
                if index == 0:
                    scaled_array = framebuffer_cam * self.m_muti_ratio[0]
                elif index == 1:
                    scaled_array = framebuffer_cam * self.m_muti_ratio[1]
                framebuffer_cam = np.uint16(scaled_array)
                qimg_cam = QImage(framebuffer_cam.data,framebuffer_cam.shape[1], framebuffer_cam.shape[0],
                    framebuffer_cam.shape[1] * 2, QImage.Format.Format_Grayscale16)
                if index == 0:
                    pixmap_cam = QPixmap.fromImage(qimg_cam)
                    self.sig_report_pixmap_cam1.emit(pixmap_cam)
                elif index == 1:
                    if self.m_mirror_cam2:
                        qimg_cam = qimg_cam.mirrored(False, True)
                    pixmap_cam = QPixmap.fromImage(qimg_cam)
                    self.sig_report_pixmap_cam2.emit(pixmap_cam)                  
                
                if self.m_difference_flag:
                    self.m_data_queues[index].append(framebuffer_cam)
                    if self.m_data_queues[1 - index] and len(self.m_data_queues[index]) == 1:
                        self.calculate_difference()
        
        data_cam = ctypes.cast(data_cam,c_void_p)
        Delete_Data_pointer(data_cam)
    
    @QPSLObjectBase.log_decorator()    
    def calculate_difference(self):
        image_cam1 = self.m_data_queues[0].popleft()
        image_cam2 = self.m_data_queues[1].popleft()
        image_tmp = np.flip(image_cam2,0)
        image_difference = image_cam1 * self.m_muti_ratio[0] + image_tmp *self.m_muti_ratio[1]
        image_difference = np.uint16(image_difference)
        qimg_difference = QImage(image_difference.copy(),image_difference.shape[1], image_difference.shape[0],
                      image_difference.shape[1] * 2, QImage.Format.Format_Grayscale16)
        pixmap_cam = QPixmap.fromImage(qimg_difference)
        # self.sig_report_ndarray_difference.emit(image_difference)
        self.sig_report_pixmap_difference.emit(pixmap_cam)


class DCAMSaveWorker(QPSLWorker):
    '''
    Create a thread for saving frame data TIF file
    '''
    sig_to_set_save_path = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.m_save_flag:bool = True
        self.m_endframe = 0
        self.m_index_image = 0
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
        folder_name = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_Round{0}".format(suffix))
        self.save_file_path = "{0}/{1}".format(self.m_save_path,folder_name)
        if not os.path.exists(self.save_file_path):
            os.mkdir(self.save_file_path)
    
    @QPSLObjectBase.log_decorator()    
    def save_tiff_file(self, data:np.ndarray):
        if self.m_save_flag == False:
            return
        tifffile.imwrite(self.save_file_path + "/CAM{0}_{1}.tif".format(self.index, self.m_index_image),
                       data)
        self.m_index_image += 1
        if self.m_index_image == self.m_endframe:
            self.m_index_image = 0
        # =============== Save tiff files as batch ===============
        # self.m_save_buffer[self.m_index_image] = data
        # if self.m_index_image % SAVE_BATCH_SIZE == 0 or self.m_index_image == self.m_endframe:        
        #     tifffile.imwrite(self.save_file_path + "/CAM{0}_{1}.tif".format(self.index, self.m_batch_number), 
        #                     self.m_save_buffer)
        #     self.m_save_buffer[:] = 0
        #     self.m_batch_number  += 1
        # if self.m_index_image == self.m_endframe:
        #     self.m_index_image = 0
            # self.m_save_flag = False


class DoubleDCAMPluginWorker(QPSLWorker):
    '''
    Worker for camera operation tasks
    '''  
    sig_open_cam, sig_to_open_cam, sig_cam_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()    
    sig_close_cam, sig_to_close_cam, sig_cam_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_live_cam, sig_to_live_cam, sig_cam_lived = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_abort_cam, sig_to_abort_cam, sig_cam_aborted = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_setROI_cam, sig_to_setROI_cam = pyqtSignal(
        int, int, int, int), pyqtSignal(int, int, int, int)
    sig_set_trigger_dalay_cam, sig_to_set_trigger_delay_cam = pyqtSignal(
        float), pyqtSignal(float)
    sig_setExposuretime_cam, sig_to_setExposuretime_cam = pyqtSignal(
        float), pyqtSignal(float)
    sig_strat_scan_cam, sig_to_start_scan_cam, sig_scan_cam_started = pyqtSignal(int
    ), pyqtSignal(int), pyqtSignal(str)
    sig_single_round_scan, sig_single_round_done = pyqtSignal(int), pyqtSignal(str)    
    sig_stop_scan_cam, sig_to_stop_scan_cam, sig_scan_cam_stopped = pyqtSignal(
    ), pyqtSignal(), pyqtSignal(str)
    sig_send_data_to_live = pyqtSignal(int, np.uint64)
    sig_send_data_to_save = pyqtSignal(np.uint64)
    sig_refresh_frame_rate = pyqtSignal(float)

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
    
    @QPSLObjectBase.log_decorator()
    def on_close_cam(self):
        # self.m_cam1.buffer_release()
        self.m_cam.close_device()
        self.sig_cam_closed.emit()
    
    @QPSLObjectBase.log_decorator()
    def on_get_deviceID_cam(self):
        self.ID_cam =c_char()
        err, self.ID_cam = self.m_cam.get_cameraID()
    
    @QPSLObjectBase.log_decorator()
    def on_get_temperature_cam(self):
        self.temp_cam = c_double()
        err, self.temp_cam = self.m_cam.get_temperature()
    
    @QPSLObjectBase.log_decorator()
    def on_live_cam(self):
        self.m_continue_flag = True
        self.sig_cam_lived.emit()
        self.m_worker_self = py_object(self)
        self.add_warning("Camera {0} is living".format(self.index))
        self.m_cam.pre_live()
        self.m_timer_freq.start()
        while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag:
            QCoreApplication.instance().processEvents()
            self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                            callback= DoubleDCAMPluginWorker.on_everyframe_callback)
            elapsed_time = self.m_timer_freq.elapsed()
            self.sig_refresh_frame_rate.emit(elapsed_time/1000.0)
        self.m_cam.post_live()
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
   
    @QPSLObjectBase.log_decorator()
    def on_set_exposure_time_cam(self, exposure_time:float):
        self.m_cam.set_exposure_time(exposure_time/1000) #msec

    @QPSLObjectBase.log_decorator()
    def on_set_internal_trigger_cam(self):
        self.m_cam.set_internal_trigger()

    @QPSLObjectBase.log_decorator()
    def on_set_external_trigger_cam(self):
        self.m_cam.set_external_trigger()

    @QPSLObjectBase.log_decorator()
    def on_set_syncreadout_cam(self):
        self.m_cam.set_syncreadout()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_positive_cam(self, polarity:bool):
        self.m_cam.set_trigger_positive()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_negative_cam(self, polarity:bool):
        self.m_cam.set_trigger_negative()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_delay_cam(self, trigger_delay:float):
        self.m_cam.set_trigger_delay(trigger_delay)

    @QPSLObjectBase.log_decorator()
    def on_scan_cam(self,endframe:int):
        self.m_continue_flag = True
        """
        while self.m_scan_continus_flag:
            QCoreApplication.instance().processEvents()
            if not self.m_scan_loop_flag:
                # self.m_continue_flag = True
                self.m_worker_self = py_object(self)
                self.add_warning("Camera {0} is scaning".format(self.index))
                self.sig_scan_cam_started.emit("Camera {0} is scaning".format(self.index))
                self.m_cam.pre_live()
                while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag and self.m_id < endframe:
                    QCoreApplication.instance().processEvents()
                    self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                    callback= DoubleDCAMPluginWorker.on_everyframe_callback)
                self.m_cam.post_live()
                self.m_scan_continus_flag = False
                break
            else:
                # self.m_continue_flag = True
                self.m_id = 0
                self.m_worker_self = py_object(self)
                self.add_warning("Camera {0} is scaning(Loop)".format(self.index))
                self.sig_scan_cam_started.emit("Camera {0} is scaning(Loop)".format(self.index))
                self.m_cam.pre_live()
                while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag and self.m_id < endframe:
                    QCoreApplication.instance().processEvents()
                    self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                    callback= DoubleDCAMPluginWorker.on_everyframe_callback)
                self.m_cam.post_live()
                self.add_warning("Camera {0} scaning round {1} done".format(self.index,i))
                self.sig_single_round_done.emit("Camera {0} scaning round {1} done".format(self.index,i))
                i += 1
                sleep_for(4000)
        self.add_warning("Camera {0} scaning done".format(self.index))
        self.sig_scan_cam_stopped.emit("Camera {0} scaning done".format(self.index)) 
        """

        if not self.m_scan_loop_flag:
            # self.m_continue_flag = True
            self.m_worker_self = py_object(self)
            self.add_warning("Camera {0} is scaning".format(self.index))
            self.sig_scan_cam_started.emit("Camera {0} is scaning".format(self.index))
            self.m_cam.pre_live()
            while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag and self.m_id < endframe:
                QCoreApplication.instance().processEvents()
                self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                callback= DoubleDCAMPluginWorker.on_everyframe_callback)
            self.m_cam.post_live()
        else:
            for i in range(self.m_loop_round):
            # self.m_continue_flag = True
                QCoreApplication.instance().processEvents()
                self.m_id = 0
                self.m_worker_self = py_object(self)
                self.add_warning("Camera {0} is scaning(Loop)".format(self.index))
                self.sig_scan_cam_started.emit("Camera {0} is scaning(Loop)".format(self.index))
                self.m_cam.pre_live()
                while self.m_cam.err_code != DCAMERR_ABORT and self.m_continue_flag and self.m_id < endframe:
                    QCoreApplication.instance().processEvents()
                    self.m_cam.get_single_frame(pyworker=byref(self.m_worker_self), 
                                    callback= DoubleDCAMPluginWorker.on_everyframe_callback)
                self.m_cam.post_live()
                self.add_warning("Camera {0} scaning round {1} done".format(self.index,i))
                if i != self.m_loop_round-1:
                    self.sig_single_round_scan.emit(i+1)
                self.sig_single_round_done.emit("Camera {0} scaning round {1} done".format(self.index,i))
                sleep_for(4000)
        self.add_warning("Camera {0} scaning done".format(self.index))
        self.sig_scan_cam_stopped.emit("Camera {0} scaning done".format(self.index))                                 
    
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
        self: DoubleDCAMPluginWorker
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


class DoubleDCAMPluginUI(QPSLHSplitter,QPSLPluginBase):
    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_style()
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker_cam1 = DoubleDCAMPluginWorker().load_attr(0)
        self.m_worker_cam2 = DoubleDCAMPluginWorker().load_attr(1)
        self.m_live_worker = DCAMLiveWorker().load_attr()
        self.m_save_worker_cam1 = DCAMSaveWorker().load_attr(0)
        self.m_save_worker_cam2 = DCAMSaveWorker().load_attr(1)
        self.m_time_queue = [deque(), deque()]

    def load_attr(self):
        with open(self.get_json_file(),"rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self
    
    def to_delete(self):
        # if self.btn_open_cam1.sig_opened:
        #     self.m_worker_cam1.on_close_cam()
        # if self.btn_open_cam2.sig_opened:
        #     self.m_worker_cam2.on_close_cam()
        self.m_worker_cam1.stop_thread()
        self.m_worker_cam1.to_delete()
        self.m_worker_cam2.stop_thread()
        self.m_worker_cam2.to_delete()
        self.m_live_worker.stop_thread()
        self.m_live_worker.to_delete()
        self.m_save_worker_cam1.stop_thread()
        self.m_save_worker_cam1.to_delete()
        self.m_save_worker_cam2.stop_thread()
        self.m_save_worker_cam2.to_delete()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()
    
    def get_named_widgets(self):        
        # ============================================= CAMERA 1 =============================================
        self.btn_open_cam1: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_open_cam1")
        self.btn_live_cam1: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_live_cam1")
        self.btn_capture_cam1: QPSLPushButton = self.findChild(QPSLPushButton, "btn_capture_cam1")
        self.label_device_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_device_cam1")
        self.label_temperature_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_temperature_cam1")
        self.label_framerate_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_framerate_cam1")
        self.sbox_x0_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_x0_cam1")
        self.sbox_width_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_width_cam1")
        self.sbox_y0_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_y0_cam1")
        self.sbox_height_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_height_cam1")
        self.btn_applyROI_cam1: QPSLPushButton = self.findChild(QPSLPushButton, "btn_applyROI_cam1")
        self.cbox_trigger_cam1: QPSLComboBox = self.findChild(QPSLComboBox, "cbox_trigger_cam1")
        self.btn_trigger_positive_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_positive_cam1")
        self.btn_trigger_negative_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_negative_cam1")
        self.sbox_trigger_delay_cam1: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_trigger_delay_cam1")
        self.sbox_exposure_time_cam1: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_exposure_time_cam1")
        self.btn_start_scan_cam1: QPSLPushButton = self.findChild(QPSLPushButton,"btn_start_scan_cam1")
        self.btn_stop_scan_cam1: QPSLPushButton = self.findChild(QPSLPushButton,"btn_stop_scan_cam1")
        self.btn_scan_continous_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_continous_cam1")
        self.btn_scan_endframe_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_endframe_cam1")
        self.sbox_scan_endframe_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox,"sbox_scan_endframe_cam1")
        self.btn_scan_loop_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_loop_cam1")
        self.sbox_scan_loop_cam1: QPSLSpinBox = self.findChild(QPSLSpinBox,"sbox_scan_loop_cam1")
        self.line_path_cam1: QPSLLineEdit = self.findChild(QPSLLineEdit, "line_path_cam1")
        self.btn_path_cam1: QPSLPushButton = self.findChild(QPSLPushButton, "btn_path_cam1")
        # self.sbox_filename_cam1:QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_filename_cam1")
        # self.btn_path_apply_cam1:QPSLPushButton = self.findChild(QPSLPushButton, "btn_path_apply_cam1")        
        # ============================================= CAMERA 2 =============================================
        self.btn_open_cam2: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_open_cam2")
        self.btn_live_cam2: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_live_cam2")
        self.btn_capture_cam2: QPSLPushButton = self.findChild(QPSLPushButton, "btn_capture_cam2")
        self.label_device_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_device_cam2")
        self.label_temperature_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_temperature_cam2")
        self.label_framerate_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_framerate_cam2")
        self.sbox_x0_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_x0_cam2")
        self.sbox_width_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_width_cam2")
        self.sbox_y0_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_y0_cam2")
        self.sbox_height_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_height_cam2")
        self.btn_applyROI_cam2: QPSLPushButton = self.findChild(QPSLPushButton, "btn_applyROI_cam2")
        self.cbox_trigger_cam2: QPSLComboBox = self.findChild(QPSLComboBox, "cbox_trigger_cam2")
        self.btn_trigger_positive_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_positive_cam2")
        self.btn_trigger_negative_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_trigger_negative_cam2")
        self.sbox_trigger_delay_cam2: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_trigger_delay_cam2")
        self.sbox_exposure_time_cam2: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox, "sbox_exposure_time_cam2")
        self.btn_start_scan_cam2: QPSLPushButton = self.findChild(QPSLPushButton,"btn_start_scan_cam2")
        self.btn_stop_scan_cam2: QPSLPushButton = self.findChild(QPSLPushButton,"btn_stop_scan_cam2")
        self.btn_scan_continous_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_continous_cam2")
        self.btn_scan_endframe_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_endframe_cam2")
        self.sbox_scan_endframe_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox,"sbox_scan_endframe_cam2")
        self.btn_scan_loop_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_loop_cam2")
        self.sbox_scan_loop_cam2: QPSLSpinBox = self.findChild(QPSLSpinBox,"sbox_scan_loop_cam2")
        self.line_path_cam2: QPSLLineEdit = self.findChild(QPSLLineEdit, "line_path_cam2")
        self.btn_path_cam2: QPSLPushButton = self.findChild(QPSLPushButton, "btn_path_cam2")        
        # self.sbox_filename_cam2:QPSLSpinBox = self.findChild(QPSLSpinBox, "sbox_filename_cam2")
        # self.btn_path_apply_cam2:QPSLPushButton = self.findChild(QPSLPushButton, "btn_path_apply_cam2")
        # ============================================= Global =============================================
        self.btn_init_API: QPSLPushButton = self.findChild(QPSLPushButton, "btn_init_API")        
        self.btn_uninit_API: QPSLPushButton = self.findChild(QPSLPushButton, "btn_uninit_API")        
        self.text_logger: QPSLTextEdit = self.findChild(QPSLTextEdit, "text_logger")
        self.view_cam1: QPSLDCAMView = self.findChild(QPSLDCAMView, "view_cam1")
        self.view_cam2: QPSLDCAMView = self.findChild(QPSLDCAMView, "view_cam2")
        self.view_combined: QPSLDCAMView = self.findChild(QPSLDCAMView, "view_combined")
        
    def setup_style(self):
        self.get_named_widgets()
        self.cbox_trigger_cam1.addItems(["Internal","External","Syncreadout"])
        self.cbox_trigger_cam2.addItems(["Internal","External","Syncreadout"])
        self.scan_radiobuttongroup1 = QtWidgets.QButtonGroup(self)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_continous_cam1)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_endframe_cam1)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_loop_cam1)
        self.scan_radiobuttongroup2 = QtWidgets.QButtonGroup(self)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_continous_cam2)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_endframe_cam2)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_loop_cam2)
        self.line_path_cam1.setText("E:/Custom_Control_Software/Test")
        self.line_path_cam2.setText("E:/Custom_Control_Software/Test")
        self.view_cam1.sbox_ratio_2.hide()
        self.view_cam1.label_ratio_2.hide()
        self.view_cam2.sbox_ratio_2.hide()
        self.view_cam2.label_ratio_2.hide()
        self.view_combined.label_ratio_1.setText("ratio_cam1:")
        self.view_combined.label_ratio_2.setText("ratio_cam2:")
        for btn in self.btn_after_API_init:
            btn.setDisabled(True)
    
    def setup_logic(self):
        self.get_named_widgets()
        # self.m_worker_cam1.load_attr()
        self.timer_temp_1 = QTimer(self)
        self.timer_temp_2 = QTimer(self)
        '''============================================= DCAM-API ============================================='''
        connect_direct(self.btn_init_API.sig_clicked,
                       self.init_API)
        connect_direct(self.btn_uninit_API.sig_clicked,
                       self.uninit_API)
        '''============================================= CAMERA 1 ============================================='''
        # Open/Close  
        connect_direct(self.btn_open_cam1.sig_open,
                       self.on_click_open_cam1)
        connect_queued(self.m_worker_cam1.sig_cam_opened,
                       self.btn_open_cam1.set_opened)
        connect_direct(self.timer_temp_1.timeout,
                       self.refresh_temperature_cam1)
        connect_direct(self.btn_open_cam1.sig_close,
                       self.on_click_close_cam1)
        connect_queued(self.m_worker_cam1.sig_cam_closed,
                       self.btn_open_cam1.set_closed)
        # Capture
        connect_direct(self.btn_capture_cam1.sig_clicked,
                       self.on_click_capture_cam1)
        # Live/Abort
        connect_direct(self.btn_live_cam1.sig_open,
                       self.on_click_live_cam1)
        connect_queued(self.m_worker_cam1.sig_cam_lived,
                       self.btn_live_cam1.set_opened)
        connect_queued(self.m_worker_cam1.sig_send_data_to_live,
                       self.m_live_worker.receive_data_from_cam)  
        connect_queued(self.m_live_worker.sig_report_pixmap_cam1,
                       self.refresh_live_view1)
        connect_direct(self.btn_live_cam1.sig_close,
                       self.on_click_abort_cam1)    
        connect_queued(self.m_worker_cam1.sig_cam_aborted,
                       self.btn_live_cam1.set_closed)
        connect_queued(self.view_cam1.sbox_ratio_1.sig_value_changed_to,
                       self.on_change_live_ratio_cam1)
        connect_queued(self.m_worker_cam1.sig_refresh_frame_rate,
                       self.refresh_framerate_cam1)
        # Scan/Stop
        connect_direct(self.btn_start_scan_cam1.sig_clicked,
                       self.on_clicked_scan_cam1)
        connect_queued(self.m_live_worker.sig_report_ndarray_cam1,
                       self.m_save_worker_cam1.save_tiff_file)
        connect_direct(self.btn_stop_scan_cam1.sig_clicked,
                       self.on_clicked_stop_cam1)
        connect_queued(self.m_worker_cam1.sig_scan_cam_started,
                       self.add_log_message)
        connect_queued(self.m_worker_cam1.sig_single_round_done,
                       self.add_log_message)
        connect_queued(self.m_worker_cam1.sig_scan_cam_stopped,
                       self.add_log_message)
        connect_queued(self.m_worker_cam1.sig_single_round_scan,
                       self.m_save_worker_cam1.set_save_path)

        # connect_queued(self.m_worker_cam1.sig_send_data_to_save,
        #                self.m_save_worker_cam1.save_tiff_file)
        # Setting
        connect_direct(self.btn_applyROI_cam1.sig_clicked,
                       self.on_click_setROI_cam1)
        connect_direct(self.cbox_trigger_cam1.activated,
                       self.on_change_trigger_cam1)
        connect_queued(self.btn_trigger_positive_cam1.clicked,
                       self.m_worker_cam1.on_set_trigger_positive_cam)
        connect_queued(self.btn_trigger_negative_cam1.clicked,
                       self.m_worker_cam1.on_set_trigger_negative_cam)
        connect_direct(self.sbox_trigger_delay_cam1.sig_value_changed,
                       self.on_change_trigger_delay_cam1)     
        connect_direct(self.sbox_exposure_time_cam1.sig_value_changed,
                       self.on_change_Exposuretime_cam1)
        connect_direct(self.btn_path_cam1.clicked,
                       self.choose_path_cam1)
        '''============================================= CAMERA 2 ============================================='''
        # Open/Close       
        connect_direct(self.btn_open_cam2.sig_open,
                       self.on_click_open_cam2)
        connect_queued(self.m_worker_cam2.sig_cam_opened,
                       self.btn_open_cam2.set_opened)
        connect_direct(self.timer_temp_2.timeout,
                       self.refresh_temperature_cam2)
        connect_direct(self.btn_open_cam2.sig_close,
                       self.on_click_close_cam2)
        connect_queued(self.m_worker_cam2.sig_cam_closed,
                       self.btn_open_cam2.set_closed)
        # Capture
        connect_direct(self.btn_capture_cam2.sig_clicked,
                       self.on_click_capture_cam2)
        # Live/Abort      
        connect_direct(self.btn_live_cam2.sig_open,
                       self.on_click_live_cam2)
        connect_queued(self.m_worker_cam2.sig_cam_lived,
                       self.btn_live_cam2.set_opened)
        connect_queued(self.m_worker_cam2.sig_cam_aborted,
                       self.btn_live_cam2.set_closed)
        connect_queued(self.m_worker_cam2.sig_send_data_to_live,
                       self.m_live_worker.receive_data_from_cam)  
        connect_queued(self.m_live_worker.sig_report_pixmap_cam2,
                       self.refresh_live_view2)
        connect_direct(self.btn_live_cam2.sig_close,
                       self.on_click_abort_cam2)    
        connect_queued(self.m_worker_cam2.sig_cam_aborted,
                       self.btn_live_cam2.set_closed)
        connect_direct(self.view_cam2.sbox_ratio_1.sig_value_changed_to,
                       self.on_change_live_ratio_cam2)
        connect_queued(self.m_worker_cam2.sig_refresh_frame_rate,
                       self.refresh_framerate_cam2)
        # Scan/Stop      
        connect_direct(self.btn_start_scan_cam2.sig_clicked,
                       self.on_clicked_scan_cam2)
        connect_queued(self.m_live_worker.sig_report_ndarray_cam2,
                       self.m_save_worker_cam2.save_tiff_file)
        connect_direct(self.btn_stop_scan_cam2.sig_clicked,
                       self.on_clicked_stop_cam2)
        connect_queued(self.m_worker_cam2.sig_scan_cam_started,
                       self.add_log_message)
        connect_queued(self.m_worker_cam2.sig_single_round_done,
                       self.add_log_message)
        connect_queued(self.m_worker_cam2.sig_scan_cam_stopped,
                       self.add_log_message)
        connect_queued(self.m_worker_cam2.sig_single_round_scan,
                       self.m_save_worker_cam2.set_save_path)
        # Setting       
        connect_direct(self.btn_applyROI_cam2.sig_clicked,
                       self.on_click_setROI_cam2)
        connect_direct(self.cbox_trigger_cam2.activated,
                       self.on_change_trigger_cam2)
        connect_queued(self.btn_trigger_positive_cam2.clicked,
                       self.m_worker_cam2.on_set_trigger_positive_cam)
        connect_queued(self.btn_trigger_negative_cam2.clicked,
                       self.m_worker_cam2.on_set_trigger_negative_cam)
        connect_direct(self.sbox_trigger_delay_cam2.sig_value_changed,
                       self.on_change_trigger_delay_cam2)        
        connect_direct(self.sbox_exposure_time_cam2.sig_value_changed,
                       self.on_change_Exposuretime_cam2)
        connect_direct(self.btn_path_cam2.clicked,
                       self.choose_path_cam2)

        connect_direct(self.view_combined.sbox_ratio_1.sig_value_changed_to,
                       self.on_change_live_ratio_cam1)
        connect_direct(self.view_combined.sbox_ratio_2.sig_value_changed_to,
                       self.on_change_live_ratio_cam2)
        connect_queued(self.m_live_worker.sig_report_pixmap_difference,
                       self.refresh_live_view_difference)
        
        self.m_worker_cam1.start_thread()
        self.m_worker_cam2.start_thread()
        self.m_live_worker.start_thread()
        self.m_save_worker_cam1.start_thread()
        self.m_save_worker_cam2.start_thread()

    '''============================================= CAMERA 1 =============================================''' 
    @QPSLObjectBase.log_decorator()
    def on_click_open_cam1(self):
        self.m_worker_cam1.sig_to_open_cam.emit()
        sleep_for(1000)
        self.on_set_deviceID_cam1()
        self.timer_temp_1.start(1000)
        for btn in self.btn_after_CAM1_opened:
            btn.setEnabled(True)
        self.add_log_message("DCAM_1({0}) Opened".format(self.m_worker_cam1.ID_cam.value.decode("utf-8")))

    @QPSLObjectBase.log_decorator()
    def on_click_close_cam1(self):
        self.m_worker_cam1.sig_to_close_cam.emit()
        self.timer_temp_1.stop()
        self.label_device_cam1.clear()
        self.label_temperature_cam1.clear()
        self.label_framerate_cam1.clear()
        self.add_log_message("DCAM_1 Closed")

    @QPSLObjectBase.log_decorator()
    def on_click_live_cam1(self):
        self.m_live_worker.m_live_flag = True
        self.m_worker_cam1.sig_to_live_cam.emit()
    
    @QPSLObjectBase.log_decorator()
    def on_change_live_ratio_cam1(self, ratio:float):
        self.m_live_worker.m_muti_ratio[0] = ratio

    @QPSLObjectBase.log_decorator()
    def refresh_live_view1(self, cam1_image:QPixmap):
        self.view_cam1.on_show_pixmap(cam1_image)

    @QPSLObjectBase.log_decorator()
    def on_click_abort_cam1(self):
        self.m_worker_cam1.sig_to_abort_cam.emit()
        sleep_for(500)
        self.m_time_queue[0].clear()

    @QPSLObjectBase.log_decorator()
    def on_click_capture_cam1(self):
        # m_save_path = self.line_path_cam1.text()
        # if m_save_path == "":
        #     m_save_path = "E:/Custom_Control_Software/Test"
        # m_file_name = self.sbox_filename_cam1.value()
        # m_file_path = "{0}/{1}".format(m_save_path, m_file_name).encode('utf-8')
        # self.m_worker_cam1.on_capture_cam(m_file_path)
        # self.add_log_message("DCAM {0} Captured picture {1}".format(self.m_worker_cam1.ID_cam.value.decode("utf-8"),
        #                                                             m_file_name))
        pass

    @QPSLObjectBase.log_decorator()
    def on_set_deviceID_cam1(self):
        self.m_worker_cam1.on_get_deviceID_cam()
        self.label_device_cam1.setText("Device: " + self.m_worker_cam1.ID_cam.value.decode("utf-8").replace("\\","/"))
    
    @QPSLObjectBase.log_decorator()
    def refresh_temperature_cam1(self):
        self.m_worker_cam1.on_get_temperature_cam()
        self.label_temperature_cam1.setText("Temperature: " + str(self.m_worker_cam1.temp_cam.value))

    @QPSLObjectBase.log_decorator()
    def refresh_framerate_cam1(self,current_frame_time:float):
            self.m_time_queue[0].append(current_frame_time)
            while self.m_time_queue[0][-1] - 2 >= self.m_time_queue[0][0]:
                self.m_time_queue[0].popleft()
            self.label_framerate_cam1.setText("Framerate: " + str(len(self.m_time_queue[0])/2))
    
    @QPSLObjectBase.log_decorator()
    def on_click_setROI_cam1(self):        
        self.m_live_worker.m_data_count[0] = self.sbox_width_cam1.value() * self.sbox_height_cam1.value()
        self.m_live_worker.m_data_shape[0] = (self.sbox_width_cam1.value(),self.sbox_height_cam1.value())
        # self.m_save_worker_cam1.m_save_buffer = np.empty((SAVE_BATCH_SIZE,self.sbox_width_cam1.value(),self.sbox_height_cam1.value()), dtype=np.uint16)
        self.m_worker_cam1.sig_to_setROI_cam.emit(self.sbox_x0_cam1.value(),
                                              self.sbox_y0_cam1.value(),
                                              self.sbox_width_cam1.value(),
                                              self.sbox_height_cam1.value())

    @QPSLObjectBase.log_decorator()
    def on_change_trigger_cam1(self, trigger_type:str):
        if self.cbox_trigger_cam1.currentText() == "Internal":
            self.m_worker_cam1.on_set_internal_trigger_cam()
        elif self.cbox_trigger_cam1.currentText() == "External":
            self.m_worker_cam1.on_set_external_trigger_cam()
        elif self.cbox_trigger_cam1.currentText() == "Syncreadout":
            self.m_worker_cam1.on_set_syncreadout_cam()
        self.add_log_message("DCAM_1({0}) set {1}".format(self.m_worker_cam1.ID_cam.value.decode("utf-8"), self.cbox_trigger_cam1.currentText()))
    
    @QPSLObjectBase.log_decorator()
    def on_change_trigger_delay_cam1(self):
        self.m_worker_cam1.sig_to_set_trigger_delay_cam.emit(self.sbox_trigger_delay_cam1.value())

    @QPSLObjectBase.log_decorator()
    def on_change_Exposuretime_cam1(self):
        self.m_worker_cam1.sig_to_setExposuretime_cam.emit(self.sbox_exposure_time_cam1.value())

    @QPSLObjectBase.log_decorator()
    def on_clicked_scan_cam1(self):
        self.m_save_worker_cam1.m_save_flag = True
        self.m_save_worker_cam1.m_index_image = 0
        self.m_live_worker.m_live_flag = False
        if self.btn_scan_continous_cam1.isChecked():
            endframe = 50000
        elif self.btn_scan_endframe_cam1.isChecked():
            endframe = self.sbox_scan_endframe_cam1.value()
            self.m_worker_cam1.m_scan_loop_flag = False
        elif self.btn_scan_loop_cam1.isChecked():
            endframe = self.sbox_scan_endframe_cam1.value()
            loop_round = self.sbox_scan_loop_cam1.value()
            self.m_worker_cam1.m_scan_loop_flag = True
            self.m_worker_cam1.m_loop_round = loop_round
        self.m_save_worker_cam1.m_endframe = endframe
        self.m_save_worker_cam1.m_save_path = self.line_path_cam1.text()
        self.m_save_worker_cam1.sig_to_set_save_path.emit(0)
        sleep_for(100)
        self.m_worker_cam1.sig_to_start_scan_cam.emit(endframe)

    @QPSLObjectBase.log_decorator()
    def on_clicked_stop_cam1(self):
        self.m_worker_cam1.sig_to_stop_scan_cam.emit()
        self.m_save_worker_cam1.m_save_flag = False

    @QPSLObjectBase.log_decorator()
    def choose_path_cam1(self, event):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder",'./')
        self.line_path_cam1.setText(folder_path)
    
    '''============================================= CAMERA 2 =============================================''' 
    @QPSLObjectBase.log_decorator()
    def on_click_open_cam2(self):
        self.m_live_worker.m_difference_flag = True
        self.m_worker_cam2.sig_to_open_cam.emit()
        sleep_for(1000)
        self.on_set_deviceID_cam2()
        self.timer_temp_2.start(1000)
        for btn in self.btn_after_CAM2_opened:
            btn.setEnabled(True)
        self.add_log_message("DCAM_2({0}) Opened".format(self.m_worker_cam2.ID_cam.value.decode("utf-8")))

    @QPSLObjectBase.log_decorator()
    def on_click_close_cam2(self):
        self.m_worker_cam2.sig_to_close_cam.emit()
        self.m_live_worker.m_difference_flag = False
        self.timer_temp_2.stop()
        self.label_device_cam2.clear()
        self.label_temperature_cam2.clear()
        self.label_framerate_cam2.clear()
        self.add_log_message("DCAM_2 Closed")

    @QPSLObjectBase.log_decorator()
    def on_click_live_cam2(self):
        self.m_live_worker.m_live_flag = False
        self.m_worker_cam2.sig_to_live_cam.emit()

    @QPSLObjectBase.log_decorator()
    def on_change_live_ratio_cam2(self, ratio:float):
        self.m_live_worker.m_muti_ratio[1] = ratio

    @QPSLObjectBase.log_decorator()
    def refresh_live_view2(self, cam2_image:QPixmap):
        self.view_cam2.on_show_pixmap(cam2_image)

    @QPSLObjectBase.log_decorator()
    def on_click_abort_cam2(self):
        self.m_worker_cam2.sig_to_abort_cam.emit()
        sleep_for(500)
        self.m_time_queue[1].clear()

    @QPSLObjectBase.log_decorator()
    def on_click_capture_cam2(self):
        # m_save_path = self.line_path_cam2.text()
        # if m_save_path == "":
        #     m_save_path = "E:/Custom_Control_Software/Test"
        # m_file_name = self.sbox_filename_cam2.value()
        # m_file_path = "{0}/{1}".format(m_save_path, m_file_name).encode('utf-8')
        # self.m_worker_cam2.on_capture_cam(m_file_path)
        # self.add_log_message("DCAM {0} Captured picture {1}".format(self.m_worker_cam2.ID_cam.value.decode("utf-8"),
        #                                                             m_file_name))
        pass

    @QPSLObjectBase.log_decorator()
    def on_set_deviceID_cam2(self):
        self.m_worker_cam2.on_get_deviceID_cam()
        self.label_device_cam2.setText("Device: " + self.m_worker_cam2.ID_cam.value.decode("utf-8").replace("\\","/"))
    
    @QPSLObjectBase.log_decorator()
    def refresh_temperature_cam2(self):
        self.m_worker_cam2.on_get_temperature_cam()
        self.label_temperature_cam2.setText("Temperature: " + str(self.m_worker_cam2.temp_cam.value))

    @QPSLObjectBase.log_decorator()
    def refresh_framerate_cam2(self,current_frame_time:float):
            self.m_time_queue[1].append(current_frame_time)
            while self.m_time_queue[1][-1] - 2 >= self.m_time_queue[1][0]:
                self.m_time_queue[1].popleft()
            self.label_framerate_cam2.setText("Framerate: " + str(len(self.m_time_queue[1])/2))
    
    @QPSLObjectBase.log_decorator()
    def on_click_setROI_cam2(self):        
        self.m_live_worker.m_data_count[1] = self.sbox_width_cam2.value() * self.sbox_height_cam2.value()
        self.m_live_worker.m_data_shape[1] = (self.sbox_width_cam2.value(),self.sbox_height_cam2.value())
        self.m_worker_cam2.sig_to_setROI_cam.emit(self.sbox_x0_cam2.value(),
                                              self.sbox_y0_cam2.value(),
                                              self.sbox_width_cam2.value(),
                                              self.sbox_height_cam2.value())

    @QPSLObjectBase.log_decorator()
    def on_change_trigger_cam2(self,trigger_type:str):
        if self.cbox_trigger_cam2.currentText() == "Internal":
            self.m_worker_cam2.on_set_internal_trigger_cam()
        elif self.cbox_trigger_cam2.currentText() == "External":
            self.m_worker_cam2.on_set_external_trigger_cam()
        elif self.cbox_trigger_cam2.currentText() == "Syncreadout":
            self.m_worker_cam2.on_set_syncreadout_cam()
        self.add_log_message("DCAM_2({0}) set {1}".format(self.m_worker_cam2.ID_cam.value.decode("utf-8"), self.cbox_trigger_cam2.currentText()))

    @QPSLObjectBase.log_decorator()
    def on_change_trigger_delay_cam2(self):
        self.m_worker_cam2.sig_to_set_trigger_delay_cam.emit(self.sbox_trigger_delay_cam2.value())

    @QPSLObjectBase.log_decorator()
    def on_change_Exposuretime_cam2(self):
        self.m_worker_cam2.sig_to_setExposuretime_cam.emit(self.sbox_exposure_time_cam2.value())

    @QPSLObjectBase.log_decorator()
    def on_clicked_scan_cam2(self):
        self.m_save_worker_cam2.m_save_flag = True
        self.m_save_worker_cam2.m_index_image = 0
        self.m_live_worker.m_live_flag = False
        if self.btn_scan_continous_cam2.isChecked():
            endframe = 50000
        elif self.btn_scan_endframe_cam2.isChecked():
            endframe = self.sbox_scan_endframe_cam2.value()
            self.m_worker_cam2.m_scan_loop_flag = False
        elif self.btn_scan_loop_cam2.isChecked():
            endframe = self.sbox_scan_endframe_cam2.value()
            loop_round = self.sbox_scan_loop_cam2.value()
            self.m_worker_cam2.m_scan_loop_flag = True
            self.m_worker_cam2.m_loop_round = loop_round
        self.m_save_worker_cam2.m_endframe = endframe
        self.m_save_worker_cam2.m_save_path = self.line_path_cam2.text()
        self.m_save_worker_cam2.sig_to_set_save_path.emit(0)
        sleep_for(100)
        self.m_worker_cam2.sig_to_start_scan_cam.emit(endframe)

    @QPSLObjectBase.log_decorator()
    def on_clicked_stop_cam2(self):
        self.m_worker_cam2.sig_to_stop_scan_cam.emit()
        self.m_save_worker_cam2.m_save_flag = False

    @QPSLObjectBase.log_decorator()
    def choose_path_cam2(self, event):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder",'./')
        self.line_path_cam2.setText(folder_path)
    
    '''============================================= Global =============================================''' 
    @QPSLObjectBase.log_decorator()    
    def init_API(self):
        DCAMAPI_init()
        self.add_log_message("DCAM_API init Done")
        self.btn_open_cam1.setEnabled(True)
        self.btn_open_cam2.setEnabled(True)
        self.btn_init_API.setDisabled(True)
        self.btn_uninit_API.setEnabled(True)
    
    @QPSLObjectBase.log_decorator()
    def uninit_API(self):
        DCAMAPI_uninit()
        self.add_log_message("DCAM_API uninit Done")
        for btn in self.btn_after_API_init:
            btn.setDisabled(True)
        self.btn_init_API.setEnabled(True)
        self.btn_uninit_API.setDisabled(True)

    @QPSLObjectBase.log_decorator()
    def add_log_message(self,log_message:str):
        self.text_logger.moveCursor(QTextCursor.End)
        self.text_logger.append(log_message)

    @QPSLObjectBase.log_decorator()
    def refresh_live_view_difference(self, cam_image_difference:QPixmap):
        self.view_combined.on_show_pixmap(cam_image_difference)

    @property    
    def btn_after_API_init(self) -> Iterable[QPSLPushButton]:
        return(self.btn_uninit_API,
               self.btn_open_cam1, self.btn_open_cam2,
               self.btn_live_cam1, self.btn_live_cam2,
               self.btn_capture_cam1, self.btn_capture_cam2,
               self.btn_applyROI_cam1,self.btn_applyROI_cam2,
               self.cbox_trigger_cam1,self.cbox_trigger_cam2,
               self.sbox_trigger_delay_cam1,self.sbox_trigger_delay_cam2,
               self.sbox_exposure_time_cam1,self.sbox_exposure_time_cam2,
               self.btn_start_scan_cam1, self.btn_start_scan_cam2,
               self.btn_stop_scan_cam1, self.btn_stop_scan_cam2)
    
    @property
    def btn_after_CAM1_opened(self) -> Iterable[QPSLPushButton]:
        return(self.btn_live_cam1,
               self.btn_capture_cam1,
               self.btn_applyROI_cam1,
               self.cbox_trigger_cam1,
               self.sbox_trigger_delay_cam1,
               self.sbox_exposure_time_cam1,
               self.btn_start_scan_cam1,
               self.btn_stop_scan_cam1)
    
    @property
    def btn_after_CAM2_opened(self) -> Iterable[QPSLPushButton]:
        return(self.btn_live_cam2,
               self.btn_capture_cam2,
               self.btn_applyROI_cam2,
               self.cbox_trigger_cam2,
               self.sbox_trigger_delay_cam2,
               self.sbox_exposure_time_cam2,
               self.btn_start_scan_cam2,
               self.btn_stop_scan_cam2)
        

MainWidget = DoubleDCAMPluginUI