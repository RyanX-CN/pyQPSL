from Tool import *
from ctypes import *
from PyQt5 import QtWidgets

os_path_append("./{0}/bin".format(__package__.replace('.', '/')))
from .DoubleDCAMAPI import *

'''
    This Plugin is for controller 2 Hamamatsu CMOS camera ORCA-Flash4.0 V3
'''

class DoubleDCAMPluginWorker(QPSLWorker):
    # Camera 1    
    sig_open_cam1, sig_to_open_cam1, sig_cam1_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()    
    sig_close_cam1, sig_to_close_cam1, sig_cam1_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_live_cam1, sig_to_live_cam1, sig_cam1_lived = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_abort_cam1, sig_to_abort_cam1, sig_cam1_aborted = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_setROI_cam1, sig_to_setROI_cam1 = pyqtSignal(
        c_int,c_int,c_int,c_int), pyqtSignal(c_int,c_int,c_int,c_int)
    sig_setExposuretime_cam1, sig_to_setExposuretime_cam1 = pyqtSignal(
        c_double), pyqtSignal(c_double)
    sig_strat_scan_cam1, sig_to_start_scan_cam1, sig_scan_cam1_started = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    
    # Camera 2
    sig_open_cam2, sig_to_open_cam2, sig_cam2_opened = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()    
    sig_close_cam2, sig_to_close_cam2, sig_cam2_closed = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_live_cam2, sig_to_live_cam2, sig_cam2_lived = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()
    sig_setROI_cam2, sig_to_setROI_cam2 = pyqtSignal(
        c_int,c_int,c_int,c_int), pyqtSignal(c_int,c_int,c_int,c_int)
    sig_setExposuretime_cam2, sig_to_setExposuretime_cam2 = pyqtSignal(
        c_double), pyqtSignal(c_double)
    sig_strat_scan_cam2, sig_to_start_scan_cam2, sig_scan_cam2_started = pyqtSignal(
    ), pyqtSignal(), pyqtSignal()

    def __init__(self):
        super().__init__()
        # DCAMAPI_init()

    def load_attr(self):
        super().load_attr()
        cam1_info = [c_void_p(),c_int(0)]
        cam2_info = [c_void_p(),c_int(1)]
        self.m_cam1 = DCAMController(*cam1_info)
        self.m_cam2 = DCAMController(*cam2_info)
        self.setup_logic()
        return self

    def to_delete(self):
        if self.m_cam1.has_handle():
            self.m_cam1.buffer_release()
            self.m_cam1.close_device()
        if self.m_cam2.has_handle():
            self.m_cam1.buffer_release()
            self.m_cam2.close_device()
        # DCAMAPI_uninit()
        return super().to_delete()

    def setup_logic(self):
        #Camera 1
        connect_asynch_and_synch(self.sig_to_open_cam1,self.sig_open_cam1,
                                 self.on_open_cam1)
        connect_asynch_and_synch(self.sig_to_close_cam1,self.sig_close_cam1,
                                 self.on_close_cam1)
        connect_asynch_and_synch(self.sig_to_live_cam1,self.sig_live_cam1,
                                 self.on_live_cam1)
        connect_asynch_and_synch(self.sig_to_abort_cam1,self.sig_abort_cam1,
                                 self.on_abort_cam1)
        connect_asynch_and_synch(self.sig_to_start_scan_cam1,self.sig_strat_scan_cam1,
                                 self.on_scan_cam1)
        '''
        #Camera 2
        connect_asynch_and_synch(self.sig_to_open_cam2,self.sig_open_cam2,
                                 self.on_open_cam2)
        connect_asynch_and_synch(self.sig_to_close_cam2,self.sig_close_cam2,
                                 self.on_close_cam2)
        connect_asynch_and_synch(self.sig_to_live_cam2,self.sig_live_cam2,
                                 self.on_live_cam2)
        connect_asynch_and_synch(self.sig_to_start_scan_cam2,self.sig_strat_scan_cam2,
                                 self.on_scan_cam2)
        '''
        
    #Camera 1
    @QPSLObjectBase.log_decorator()
    def on_open_cam1(self):
        self.m_cam1.open_device()
    
    @QPSLObjectBase.log_decorator()
    def on_close_cam1(self):
        self.m_cam1.buffer_release()
        self.m_cam1.close_device()
    
    @QPSLObjectBase.log_decorator()
    def on_get_deviceID_cam1(self):
        err, self.ID_cam1 = self.m_cam1.get_cameraID()
    
    @QPSLObjectBase.log_decorator()
    def on_get_temperature_cam1(self):
        err, self.temp_cam1 = self.m_cam1.get_temperature()
    
    @QPSLObjectBase.log_decorator()
    def on_live_cam1(self):
        self.m_image1 = py_object(self)
        self.m_cam1.live(image_data=byref(self.m_image1))
        print(self.m_image1)
        self.add_warning("Camera 1 is live")

    @QPSLObjectBase.log_decorator()
    def on_abort_cam1(self):
        self.m_cam1.abort()
    
    @QPSLObjectBase.log_decorator()    
    def on_capture_cam1(self, m_save_path):
        self.m_cam1.save_path = c_char_p(m_save_path)
        self.m_cam1.capture()
    
    @QPSLObjectBase.log_decorator()
    def on_set_ROI_cam1(self, m_hpos, m_vpos, m_hsize, m_vsize):
        self.m_cam1.set_ROI(m_hpos,m_vpos,m_hsize,m_vsize)
   
    @QPSLObjectBase.log_decorator()
    def on_set_exposure_time_cam1(self, m_exposure_time):
        self.m_cam1.set_exposure_time(m_exposure_time)

    @QPSLObjectBase.log_decorator()
    def on_set_internal_trigger_cam1(self):
        self.m_cam1.set_internal_trigger()

    @QPSLObjectBase.log_decorator()
    def on_set_external_trigger_cam1(self):
        self.m_cam1.set_external_trigger()

    @QPSLObjectBase.log_decorator()
    def on_set_syncreadout_cam1(self):
        self.m_cam1.set_syncreadout()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_positive_cam1(self):
        self.m_cam1.set_trigger_positive()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_negative_cam1(self):
        self.m_cam1.set_trigger_negative()

    @QPSLObjectBase.log_decorator()
    def on_set_trigger_delay_cam1(self, m_trigger_delay):
        self.m_cam1.set_trigger_delay(m_trigger_delay)

    @QPSLObjectBase.log_decorator()
    def on_scan_cam1(self, m_endframe, m_save_path):
        self.m_cam1.save_path = c_char_p(m_save_path)
        self.m_cam1.scan(m_endframe)

    @QPSLObjectBase.log_decorator()
    def on_scan_cam1_continous(self, m_endframe, m_save_path):
        self.m_cam1.save_path = c_char_p(m_save_path)
        while True:
            self.m_cam1.scan(m_endframe)        
        
    #Camera 2


class DoubleDCAMPluginUI(QPSLHFrameList,QPSLPluginBase):
    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_style()
        self.setup_logic()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = DoubleDCAMPluginWorker()

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
        #Camera 1
        self.btn_open_cam1: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_open_cam1")
        self.btn_live_cam1: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_live_cam1")
        self.btn_capture_cam1: QPSLPushButton = self.findChild(QPSLPushButton, "btn_capture_cam1")
        self.label_device_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_device_cam1")
        self.label_temperature_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_temperature_cam1")
        self.label_framerate_cam1: QPSLLabel =self.findChild(QPSLLabel, "label_framerate_cam1")
        self.sbox_x0_cam1: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_x0_cam1")
        self.sbox_width_cam1: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_width_cam1")
        self.sbox_y0_cam1: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_y0_cam1")
        self.sbox_height_cam1: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_height_cam1")
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
        self.btn_scan_custom_cam1: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_custom_cam1")
        self.line_path_cam1: QPSLLineEdit = self.findChild(QPSLLineEdit, "line_path_cam1")
        #Camera 2
        self.btn_open_cam2: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_open_cam2")
        self.btn_live_cam2: QPSLToggleButton = self.findChild(QPSLToggleButton, "btn_live_cam2")
        self.btn_capture_cam2: QPSLPushButton = self.findChild(QPSLPushButton, "btn_capture_cam2")
        self.label_device_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_device_cam2")
        self.label_temperature_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_temperature_cam2")
        self.label_framerate_cam2: QPSLLabel =self.findChild(QPSLLabel, "label_framerate_cam2")
        self.sbox_x0_cam2: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_x0_cam2")
        self.sbox_width_cam2: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_width_cam2")
        self.sbox_y0_cam2: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_y0_cam2")
        self.sbox_height_cam2: QPSLSpinBox = self.findChild(QPSLLabel, "sbox_height_cam2")
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
        self.btn_scan_custom_cam2: QPSLRadioButton = self.findChild(QPSLRadioButton, "btn_scan_custom_cam2")
        self.line_path_cam2: QPSLLineEdit = self.findChild(QPSLLineEdit, "line_path_cam2")
        #Log
        self.text_logger: QPSLTextEdit = self.findChild(QPSLTextEdit, "text_logger")
        #Live view
        self.view_cam1: QPSLTrackedScalePixmapLabel = self.findChild(QPSLTrackedScalePixmapLabel, "view_cam1")
        self.view_cam2: QPSLTrackedScalePixmapLabel = self.findChild(QPSLTrackedScalePixmapLabel, "view_cam2")
        self.view_combined: QPSLTrackedScalePixmapLabel = self.findChild(QPSLTrackedScalePixmapLabel, "view_combined")
        

    def setup_style(self):
        self.get_named_widgets()
        self.cbox_trigger_cam1.addItems(["Internal","External","Syncreadout"])
        self.cbox_trigger_cam2.addItems(["Internal","External","Syncreadout"])
        self.scan_radiobuttongroup1 = QtWidgets.QButtonGroup(self)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_continous_cam1)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_endframe_cam1)
        self.scan_radiobuttongroup1.addButton(self.btn_scan_custom_cam1)
        self.scan_radiobuttongroup2 = QtWidgets.QButtonGroup(self)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_continous_cam2)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_endframe_cam2)
        self.scan_radiobuttongroup2.addButton(self.btn_scan_custom_cam2)
    
    def setup_logic(self):
        self.get_named_widgets()
        self.m_worker.load_attr()
        self.timer = QTimer(self)
        #CAMERA 1
        connect_direct(self.btn_open_cam1.sig_open,
                       self.on_click_open_cam1)
        connect_queued(self.m_worker.sig_cam1_opened,
                       self.btn_open_cam1.set_opened)   #Open CAM 1
        connect_direct(self.btn_open_cam1.sig_close,
                       self.on_click_close_cam1)
        connect_queued(self.m_worker.sig_cam1_closed,
                       self.btn_open_cam1.set_closed)   #Close CAM 1
        connect_direct(self.btn_live_cam1.sig_open,
                       self.on_click_live_cam1)
        connect_queued(self.m_worker.sig_cam1_lived,
                       self.btn_live_cam1.set_opened)   #Live
        connect_direct(self.btn_live_cam1.sig_close,
                       self.on_click_abort_cam1)    
        connect_queued(self.m_worker.sig_cam1_aborted,
                       self.btn_live_cam1.set_closed)   #Abort
        connect_direct(self.btn_capture_cam1.sig_clicked,
                       self.on_click_capture_cam1)
        connect_direct(self.timer.timeout,
                       self.refresh_temperature_cam1)
        connect_direct(self.btn_applyROI_cam1.sig_clicked,
                       self.on_click_setROI_cam1)
        connect_direct(self.sbox_exposure_time_cam1.sig_value_changed,
                       self.on_click_setExposuretime_cam1)
        
    #CAMERA 1    
    @QPSLObjectBase.log_decorator()
    def on_click_open_cam1(self):
        self.m_worker.sig_to_open_cam1.emit()
        self.on_set_deviceID_cam1()

    @QPSLObjectBase.log_decorator()
    def on_click_close_cam1(self):
        self.m_worker.sig_to_close_cam1.emit()
        self.label_device_cam1.clear()
        self.label_temperature_cam1.clear()
        self.label_framerate_cam1.clear()

    @QPSLObjectBase.log_decorator()
    def on_click_live_cam1(self):
        self.m_worker.sig_to_live_cam1.emit()
        self.m_worker.sig_to_live_cam1.emit()

    @QPSLObjectBase.log_decorator()
    def on_click_abort_cam1(self):
        self.m_worker.sig_to_abort_cam1.emit()
        self.m_worker.on_abort_cam1()

    @QPSLObjectBase.log_decorator()
    def on_click_capture_cam1(self):
        m_save_path = self.line_path_cam1.text()
        self.m_worker.on_capture_cam1(m_save_path)

    @QPSLObjectBase.log_decorator()
    def on_set_deviceID_cam1(self):
        self.m_worker.on_get_deviceID_cam1()
        self.label_device_cam1.setText("Device:" + str(self.m_worker.ID_cam1))
    
    @QPSLObjectBase.log_decorator()
    def refresh_temperature_cam1(self):
        self.m_worker.on_get_temperature_cam1()
        self.label_temperature_cam1.setText("Temperature: " + str(self.m_worker.temp_cam1))

    @QPSLObjectBase.log_decorator()
    def refresh_framerate_cam1(self):
        pass
    
    @QPSLObjectBase.log_decorator()
    def on_click_setROI_cam1(self):        
        self.m_worker.sig_to_setROI_cam1.emit(c_int(self.sbox_x0_cam1.value()),
                                              c_int(self.sbox_y0_cam1.value()),
                                              c_int(self.sbox_width_cam1.value()),
                                              c_int(self.sbox_height_cam1.value()))
        
    @QPSLObjectBase.log_decorator()
    def on_click_setExposuretime_cam1(self):
        self.m_worker.sig_to_setExposuretime_cam1.emit(c_double(self.sbox_exposure_time_cam1))

    @QPSLObjectBase.log_decorator()
    def on_clicked_scan_cam1(self):
        self.m_worker.sig_to_start_scan_cam1.emit()

    

MainWidget = DoubleDCAMPluginUI