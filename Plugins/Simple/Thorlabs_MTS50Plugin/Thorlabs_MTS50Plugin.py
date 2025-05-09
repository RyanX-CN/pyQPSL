from Tool import *
from ctypes import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
import pyqtgraph.opengl as gl
import numpy as np

'''
    This Plugin is for Thorlabs MTS50 Stage with KDC101 motor
'''
# os.chdir("C:\Program Files\Thorlabs\Kinesis")
os_path_append("./{0}/bin".format(__package__.replace('.', '/')))

# Parameters for MTS50/M-Z8
STEPS_PER_REV = c_double(512)
GEARBOX_RATIO = c_double(67.49)
PITCH = c_double(1)

# Serial number of each stage
# SERIAL_NUMBER_X = b"27000001"
# SERIAL_NUMBER_Y = b"27000002"
# SERIAL_NUMBER_Z = b"27000003"

SERIAL_NUMBER_X = b"27258500"
SERIAL_NUMBER_Y = b"27258730"
SERIAL_NUMBER_Z = b"27258489"

# Relative move distance in realunit(mm)
minus_distance = c_double(-1)
plus_distance = c_double(1)


class Thorlabs_MTS50Base(QPSLWorker):
    
    _lib = load_dll("Thorlabs.MotionControl.KCube.DCServo.dll")
    _log = []
    moving_state = bool

    def __init__(self,serial_number:str):
        super().__init__()
        self.m_serial_number = c_char_p(serial_number)
    
    @QPSLObjectBase.log_decorator()
    def open_device(self):  
        self._lib.TLI_InitializeSimulations() # Uncomment this line if you are using simulations
        self._lib.TLI_BuildDeviceList()
        self._lib.CC_Open(self.m_serial_number)
        self._lib.CC_SetMotorParamsExt(self.m_serial_number, STEPS_PER_REV, GEARBOX_RATIO, PITCH)
        self._lib.CC_StartPolling(self.m_serial_number,c_int(200))
        # self._lib.CC_SetTriggerConfigParams(self.m_serial_number,c_int(12),c_int(1))
        self._log.append("Device %s Opened" % (self.m_serial_number.value))
        self.add_info("Device %s Opened" % (self.m_serial_number.value))
        # trigger1Mode  = c_int()
        # trigger1Polarity = c_int()
        # self._lib.CC_GetTriggerConfigParams(self.m_serial_number,byref(trigger1Mode),byref(trigger1Polarity))

    @QPSLObjectBase.log_decorator()
    def close_device(self):
        self._lib.CC_StopPolling(self.m_serial_number)
        self._lib.CC_Close(self.m_serial_number)
        self._log.append("Device %s Closed" % (self.m_serial_number.value))
        self.add_info("Device %s Closed" % (self.m_serial_number.value))
        # self._lib.TLI_UninitializeSimulations() #Better not use this line when using more than one stage

    @QPSLObjectBase.log_decorator()
    def move_home(self):
        self._lib.CC_Home(self.m_serial_number)
        self._log.append("Device %s is Homing" % (self.m_serial_number.value))

    @QPSLObjectBase.log_decorator()
    def move_absolute(self, position_real: c_double):
        position_dev = c_int()
        self._lib.CC_GetDeviceUnitFromRealValue(self.m_serial_number,
                                          position_real,
                                          byref(position_dev),
                                          0)
        self._lib.CC_SetMoveAbsolutePosition(self.m_serial_number, position_dev)
        # time.sleep(0.25)
        self._lib.CC_MoveAbsolute(self.m_serial_number)

    @QPSLObjectBase.log_decorator()
    def move_relative(self, distance_real: c_double):
        distance_dev = c_int()
        self._lib.CC_GetDeviceUnitFromRealValue(self.m_serial_number,
                                          distance_real,
                                          byref(distance_dev),
                                          0)
        self._lib.CC_SetMoveRelativeDistance(self.m_serial_number, distance_dev)
        self._lib.CC_MoveRelativeDistance(self.m_serial_number)

    @QPSLObjectBase.log_decorator()
    def stop_immediate(self):
        '''
        Stop the current move immediately (with risk of losing track of position).
        '''
        self._lib.CC_StopImmediate(self.m_serial_number)

    @QPSLObjectBase.log_decorator()
    def stop_profiled(self):
        '''
        Stop the current move using the current velocity profile. 
        '''
        self._lib.CC_StopProfiled(self.m_serial_number)

    @QPSLObjectBase.log_decorator()
    def get_position(self):
        # self.lib.CC_RequestPosition(self.m_serial_number)
        dev_pos = c_int(self._lib.CC_GetPosition(self.m_serial_number))
        real_pos = c_double()
        self._lib.CC_GetRealValueFromDeviceUnit(self.m_serial_number,
                                          dev_pos,
                                          byref(real_pos),
                                          0)
        return real_pos

    @QPSLObjectBase.log_decorator()
    def wait_on_ready(self) -> bool:
        messageType = c_ushort()
        messageID = c_ushort()
        messageData = c_ulong()
        if self.moving_state == True:
            while messageType.value != 2 or messageID.value != 1:
                self._lib.CC_WaitForMessage(self.m_serial_number, byref(messageType), byref(messageID), byref(messageData))
            #  print(messageType, messageID)
        else:
            pass
    
    @QPSLObjectBase.log_decorator()
    def set_accleration_and_velocity(self,acceleration_real,velocity_real):
        acceleration_dev = c_int()
        velocity_dev = c_int()
        self._lib.CC_GetDeviceUnitFromRealValue(self.m_serial_number,
                                          acceleration_real,
                                          byref(acceleration_dev),
                                          2)
        self._lib.CC_GetDeviceUnitFromRealValue(self.m_serial_number,
                                          velocity_real,
                                          byref(velocity_dev),
                                          1)
        self._lib.CC_SetVelParams(self.m_serial_number,acceleration_dev,velocity_dev)

    @QPSLObjectBase.log_decorator()
    def get_accleration_and_velocity(self):
        acceleration_dev = c_int()
        velocity_dev = c_int()
        self._lib.CC_GetVelParams(self.m_serial_number,byref(acceleration_dev),byref(velocity_dev))
        acceleration_real = c_double()
        velocity_real = c_double()
        self._lib.CC_GetRealValueFromDeviceUnit(self.m_serial_number,
                                          acceleration_dev,
                                          byref(acceleration_real),
                                          2)
        self._lib.CC_GetRealValueFromDeviceUnit(self.m_serial_number,
                                          velocity_dev,
                                          byref(velocity_real),
                                          1)

    @QPSLObjectBase.log_decorator()
    def set_output_mode_byvelocity(self,trigger1Mode,trigger1Polarity,trigger2Mode,trigger2Polarity):
        self._lib.CC_SetTriggerConfigParams(self.m_serial_number,c_int(trigger1Mode),c_int(trigger1Polarity),c_int(trigger2Mode),c_int(trigger2Polarity))
        # trigger1Mode  = c_int()
        # trigger1Polarity = c_int()
        # self._lib.CC_GetTriggerConfigParams(self.m_serial_number,byref(trigger1Mode),byref(trigger1Polarity))       

class Thorlabs_MTS50PluginWorker(QPSLWorker):
    sig_open_device, sig_to_open_device, sig_device_opened = pyqtSignal(), pyqtSignal(), pyqtSignal()
    sig_close_device, sig_to_close_device, sig_device_closed = pyqtSignal(), pyqtSignal(), pyqtSignal()
    sig_move_home, sig_to_move_home = pyqtSignal(), pyqtSignal()
    sig_move_absolute_x, sig_to_move_absolute_x = pyqtSignal(c_double), pyqtSignal(c_double)
    sig_move_absolute_y, sig_to_move_absolute_y = pyqtSignal(c_double), pyqtSignal(c_double)
    sig_move_absolute_z, sig_to_move_absolute_z = pyqtSignal(c_double), pyqtSignal(c_double)
    sig_init_scan, sig_to_init_scan = pyqtSignal(c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double), pyqtSignal(c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double)
    sig_start_scan, sig_to_start_scan, sig_scan_started = pyqtSignal(c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double), pyqtSignal(c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double,c_double), pyqtSignal()
    sig_stop_scan, sig_to_stop_scan, sig_scan_stopped = pyqtSignal(), pyqtSignal(), pyqtSignal()

    def __init__(self):
        super().__init__()
        self.x_stage = Thorlabs_MTS50Base(serial_number=SERIAL_NUMBER_X)
        self.y_stage = Thorlabs_MTS50Base(serial_number=SERIAL_NUMBER_Y)
        self.z_stage = Thorlabs_MTS50Base(serial_number=SERIAL_NUMBER_Z)
        self.setup_logic()

    def to_delete(self):
        self.x_stage.close_device()
        self.y_stage.close_device()
        self.z_stage.close_device()
        return super().to_delete()
    
    def setup_logic(self):
        connect_asynch_and_synch(self.sig_to_move_absolute_x,
                                 self.sig_move_absolute_x,
                                 self.on_move_absolute_position_x)
        connect_asynch_and_synch(self.sig_to_move_absolute_y,
                                 self.sig_move_absolute_y,
                                 self.on_move_absolute_position_y)
        connect_asynch_and_synch(self.sig_to_move_absolute_z,
                                 self.sig_move_absolute_z,
                                 self.on_move_absolute_position_z)
        connect_asynch_and_synch(self.sig_to_init_scan,
                                 self.sig_init_scan,
                                 self.on_init_scan)
        connect_asynch_and_synch(self.sig_to_start_scan,
                                 self.sig_start_scan,
                                 self.on_start_scan)
        connect_asynch_and_synch(self.sig_to_stop_scan,
                                 self.sig_stop_scan,
                                 self.on_stop_scan)

    @QPSLObjectBase.log_decorator()
    def open_devices(self):
        self.x_stage.open_device()
        self.y_stage.open_device()
        self.z_stage.open_device()
        self.sig_device_opened.emit()

    @QPSLObjectBase.log_decorator()
    def close_devices(self):
        self.x_stage.close_device()
        self.y_stage.close_device()
        self.z_stage.close_device()
        self.sig_device_closed.emit()

    @QPSLObjectBase.log_decorator()
    def home_all(self):
        self.x_stage.move_home()
        self.y_stage.move_home()
        self.z_stage.move_home()
        self.sig_move_home.emit()

    @QPSLObjectBase.log_decorator()
    def stop_all(self):
        self.x_stage.stop_immediate()
        self.y_stage.stop_immediate()
        self.z_stage.stop_immediate()
        self.sig_scan_stopped.emit()

    @QPSLObjectBase.log_decorator()
    def get_position(self):
        self.x_pos = self.x_stage.get_position().value
        self.y_pos = self.y_stage.get_position().value
        self.z_pos = self.z_stage.get_position().value

    @QPSLObjectBase.log_decorator()
    def minus_x(self):
        self.x_stage.move_relative(minus_distance)

    @QPSLObjectBase.log_decorator()
    def plus_x(self):
        self.x_stage.move_relative(plus_distance)
    
    @QPSLObjectBase.log_decorator()
    def minus_y(self):
        self.y_stage.move_relative(minus_distance)

    @QPSLObjectBase.log_decorator()
    def plus_y(self):
        self.y_stage.move_relative(plus_distance)

    @QPSLObjectBase.log_decorator()
    def minus_z(self):
        self.z_stage.move_relative(minus_distance)

    @QPSLObjectBase.log_decorator()
    def plus_z(self):
        self.z_stage.move_relative(plus_distance)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_position_x(self, distance: c_double):
        self.x_stage.move_absolute(position_real = distance)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_position_y(self, distance: c_double):
        self.y_stage.move_absolute(position_real = distance)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_position_z(self, distance: c_double):
        self.z_stage.move_absolute(position_real = distance)

    # functions for auto scan mode
    @QPSLObjectBase.log_decorator()
    def on_init_scan(self, acc_x:c_double, acc_y:c_double, acc_z:c_double,
                     vel_x:c_double, vel_y:c_double, vel_z:c_double,
                     min_x:c_double, min_y:c_double, min_z:c_double):
        self.x_stage.set_accleration_and_velocity(acc_x,vel_x)
        self.y_stage.set_accleration_and_velocity(acc_y,vel_y)
        self.z_stage.set_accleration_and_velocity(acc_z,vel_z)
        self.x_stage.move_absolute(min_x)
        self.y_stage.move_absolute(min_y)
        self.z_stage.move_absolute(min_z)

    @QPSLObjectBase.log_decorator()
    def on_start_scan(self, max_x:c_double, min_x:c_double, interval_x:c_double,
                         max_y:c_double, min_y:c_double, interval_y:c_double,
                         max_z:c_double, min_z:c_double, acc_z:c_double, vel_z:c_double):
            self.sig_scan_started.emit()
            # self.x_stage.moving_state = True
            self.y_stage.moving_state = True
            self.z_stage.moving_state = True
            try:
                while self.y_pos < max_y.value:
                    while self.x_pos < max_x.value:
                        self.z_stage.set_output_mode_byvelocity(12,1,12,1)
                        self.z_stage.set_accleration_and_velocity(acc_z, vel_z)
                        self.z_stage.move_absolute(max_z)
                        self.z_stage.wait_on_ready()
                        self.z_stage.set_output_mode_byvelocity(0,2,0,2)
                        self.z_stage.set_accleration_and_velocity(c_double(1.5), c_double(2.0))
                        self.z_stage.move_absolute(min_z)
                        # self.z_stage.wait_on_ready()
                        self.x_stage.move_relative(interval_x)
                        # self.z_stage.wait_on_ready()
                        if self.z_stage.moving_state == False:
                            raise StopIteration
                        self.z_stage.wait_on_ready()
                    self.y_stage.move_relative(interval_y)
                    self.x_stage.move_absolute(min_x)
                    # self.x_stage.wait_on_ready()
                    if self.y_stage.moving_state == False:
                        raise StopIteration
                    self.y_stage.wait_on_ready()
            except StopIteration:
                print("motion stopped")

    @QPSLObjectBase.log_decorator()
    def on_stop_scan(self):
        # self.x_stage.moving_state = False
        self.y_stage.moving_state = False
        self.z_stage.moving_state = False
        self.x_stage.stop_immediate()
        self.y_stage.stop_immediate()
        self.z_stage.stop_immediate()
        self.sig_scan_stopped.emit()

class Thorlabs_MTS50PluginUI(QPSLHFrameList,QPSLPluginBase):
    
    def load_by_json(self,json:Dict):
        super().load_by_json(json)  
        self.setup_logic()
        self.setup_style()

    def to_json(self):
        res: Dict = super().to_json()
        return res

    def __init__(self):
        super().__init__()
        self.m_worker = Thorlabs_MTS50PluginWorker()

    def load_attr(self):
        with open(self.get_json_file(),"rt") as f:
            ui_json: Dict = json.load(f)
        self.load_by_json(ui_json.get(self.__class__.__name__))
        return self
    
    def to_delete(self):
        self.m_worker.stop_thread()
        self.timer.destroyed
        self.m_worker.to_delete()
        # self.position_3d.deleteLater()
        if self.auto_save():
            self.save_into_json(json_path=self.get_json_file())
        return super().to_delete()
    
    def get_named_widgets(self):
        #initialize
        self.text_logger: QPSLTextEdit = self.findChild(QPSLTextEdit,
                                                         "text_logger")
        self.btn_open_all: QPSLToggleButton = self.findChild(QPSLToggleButton,
                                                             "btn_open_all")
        self.btn_home_all: QPSLPushButton = self.findChild(QPSLPushButton,
                                                           "btn_home_all")
        self.btn_stop_all: QPSLPushButton = self.findChild(QPSLPushButton,
                                                           "btn_stop_all")
        #x axis
        self.sbox_pos_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_pos_x")
        self.btn_minus_x: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_minus_x")
        self.btn_plus_x: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_plus_x")
        self.btn_stop_x: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_stop_x")
        self.sbox_vel_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_vel_x")
        self.sbox_acc_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_acc_x")
        self.sbox_move_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                             "sbox_move_x")
        self.btn_move_x: QPSLPushButton = self.findChild(QPSLPushButton,
                                                         "btn_move_x")  
        self.sbox_interval_x:QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                                "sbox_interval_x")
        #y axis
        self.sbox_pos_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_pos_y")
        self.btn_minus_y: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_minus_y")
        self.btn_plus_y: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_plus_y")
        self.btn_stop_y: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_stop_y")
        self.sbox_vel_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_vel_y")
        self.sbox_acc_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_acc_y")
        self.sbox_move_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                             "sbox_move_y")
        self.btn_move_y: QPSLPushButton = self.findChild(QPSLPushButton,
                                                         "btn_move_y")
        self.sbox_interval_y:QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                                "sbox_interval_y")
        #z axis
        self.sbox_pos_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_pos_z")
        self.btn_minus_z: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_minus_z")
        self.btn_plus_z: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_plus_z")
        self.btn_stop_z: QPSLPushButton = self.findChild(QPSLPushButton,
                                                          "btn_stop_z")
        self.sbox_vel_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_vel_z")
        self.sbox_acc_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_acc_z")
        self.sbox_move_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                             "sbox_move_z")
        self.btn_move_z: QPSLPushButton = self.findChild(QPSLPushButton,
                                                         "btn_move_z")
        #auto scan
        self.sbox_min_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_min_x")
        self.sbox_max_x: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_max_x")
        self.sbox_min_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_min_y")
        self.sbox_max_y: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_max_y")
        self.sbox_min_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_min_z")
        self.sbox_max_z: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                            "sbox_max_z")
        self.btn_init_scan: QPSLPushButton = self.findChild(QPSLPushButton,
                                                            "btn_init_scan")
        self.btn_start_scan: QPSLToggleButton = self.findChild(QPSLToggleButton,
                                                             "btn_start_scan")
        self.btn_mark_point: QPSLPushButton = self.findChild(QPSLPushButton,
                                                             "btn_mark_point")
        # self.position_3d: QPSLOpenGLWidget = self.findChild(QPSLOpenGLWidget,
        #                                                         "plot_path_tracing")
        #utils
        self.sbox_exposure_time: QPSLDoubleSpinBox = self.findChild(QPSLDoubleSpinBox,
                                                                "sbox_exposure_time")
        self.text_caputuring_number: QPSLLabel = self.findChild(QPSLLabel,
                                                                "text_capturing_number")

    @QPSLObjectBase.log_decorator()
    def setup_logic(self):
        self.marked_point_number = 0
        self.get_named_widgets()
        self.m_worker.load_attr()
        self.timer = QTimer(self)
        # self.plot_init()

        # connect devices
        connect_direct(self.btn_open_all.sig_open,
                       self.m_worker.open_devices)
        connect_queued(self.m_worker.sig_device_opened,
                       self.btn_open_all.set_opened)
        connect_queued(self.m_worker.sig_device_opened,
                        self.start_polling)
        connect_direct(self.btn_open_all.sig_close,
                       self.m_worker.close_devices)
        connect_queued(self.m_worker.sig_device_closed,
                       self.btn_open_all.set_closed)
        connect_direct(self.btn_home_all.sig_clicked,
                       self.m_worker.home_all)
        connect_direct(self.btn_stop_all.sig_clicked,
                       self.m_worker.stop_all)
    
        # Information refresh
        # connect_direct(self.timer.timeout,
        #                self.plot_position)
        connect_direct(self.timer.timeout,
                       self.refresh_pos)
        connect_direct(self.timer.timeout,
                       self.write_log)

        # X axis stage
        connect_direct(self.btn_stop_x.sig_clicked,
                       self.m_worker.x_stage.stop_immediate)
        connect_direct(self.btn_minus_x.sig_clicked,
                       self.m_worker.minus_x)
        connect_direct(self.btn_plus_x.sig_clicked,
                       self.m_worker.plus_x)
        connect_direct(self.btn_move_x.sig_clicked,
                       self.on_move_absolute_x)

        # Y axis stage
        connect_direct(self.btn_stop_y.sig_clicked,
                self.m_worker.y_stage.stop_immediate)
        connect_direct(self.btn_minus_y.sig_clicked,
                       self.m_worker.minus_y)
        connect_direct(self.btn_plus_y.sig_clicked,
                       self.m_worker.plus_y)
        connect_direct(self.btn_move_y.sig_clicked,
                       self.on_move_absolute_y)

        # Z axis stage
        connect_direct(self.btn_stop_z.sig_clicked,
                       self.m_worker.z_stage.stop_immediate)
        connect_direct(self.btn_minus_z.sig_clicked,
                       self.m_worker.minus_z)
        connect_direct(self.btn_plus_z.sig_clicked,
                       self.m_worker.plus_z)
        connect_direct(self.btn_move_z.sig_clicked,
                       self.on_move_absolute_z)

        #Auto scan
        connect_direct(self.btn_init_scan.sig_clicked,
                       self.init_scan)
        connect_direct(self.btn_mark_point.sig_clicked,
                       self.mark_point)
        connect_direct(self.btn_start_scan.sig_open,
                       self.start_scan)
        connect_queued(self.m_worker.sig_scan_started,
                       self.btn_start_scan.set_opened)
        connect_direct(self.btn_start_scan.sig_close,
                       self.m_worker.on_stop_scan)
        connect_queued(self.m_worker.sig_scan_stopped,
                       self.btn_start_scan.set_closed)
        
        #Utils
        connect_direct(self.timer.timeout,
                       self.utils_capturing_times)
        
        self.m_worker.start_thread()

    @QPSLObjectBase.log_decorator()
    def setup_style(self):
        root = QFileInfo(__file__).absolutePath()
        self.btn_home_all.setIcon(QIcon(root + '/resources/home.png'))
        self.btn_stop_all.setIcon(QIcon(root + '/resources/stop.png'))
        self.btn_stop_x.setIcon(QIcon(root + '/resources/stop.png'))
        self.btn_stop_x.setIconSize(QtCore.QSize(48, 48))
        self.btn_minus_x.setIcon(QIcon(root + '/resources/left-red.png'))
        self.btn_minus_x.setIconSize(QtCore.QSize(32, 32))      
        self.btn_plus_x.setIcon(QIcon(root + '/resources/right-red.png'))
        self.btn_plus_x.setIconSize(QtCore.QSize(32, 32))  
        self.btn_stop_y.setIcon(QIcon(root + '/resources/stop.png'))
        self.btn_stop_y.setIconSize(QtCore.QSize(48, 48))
        self.btn_minus_y.setIcon(QIcon(root + '/resources/left-green.png'))
        self.btn_minus_y.setIconSize(QtCore.QSize(32, 32))  
        self.btn_plus_y.setIcon(QIcon(root + '/resources/right-green.png'))
        self.btn_plus_y.setIconSize(QtCore.QSize(32, 32)) 
        self.btn_stop_z.setIcon(QIcon(root + '/resources/stop.png'))
        self.btn_stop_z.setIconSize(QtCore.QSize(48, 48))
        self.btn_minus_z.setIcon(QIcon(root + '/resources/left-blue.png'))
        self.btn_minus_z.setIconSize(QtCore.QSize(32, 32)) 
        self.btn_plus_z.setIcon(QIcon(root + '/resources/right-blue.png'))
        self.btn_plus_z.setIconSize(QtCore.QSize(32, 32)) 

        self.sbox_pos_x.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)         
        self.sbox_pos_y.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)          
        self.sbox_pos_z.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        self.sbox_acc_x.setSingleStep(0.1)
        self.sbox_acc_y.setSingleStep(0.1)
        self.sbox_acc_z.setSingleStep(0.1)
        self.sbox_vel_x.setSingleStep(0.1)
        self.sbox_vel_y.setSingleStep(0.1)
        self.sbox_vel_z.setSingleStep(0.1)

    @QPSLObjectBase.log_decorator()
    def write_log(self):
        self.text_logger.setText("\n".join(self.m_worker.x_stage._log))
        self.text_logger.setText("\n".join(self.m_worker.y_stage._log))
        self.text_logger.setText("\n".join(self.m_worker.z_stage._log))
        self.text_logger.moveCursor(self.text_logger.textCursor().End)

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_x(self):
        self.m_worker.sig_to_move_absolute_x.emit(c_double(self.sbox_move_x.value()))

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_y(self):
        self.m_worker.sig_to_move_absolute_y.emit(c_double(self.sbox_move_y.value()))

    @QPSLObjectBase.log_decorator()
    def on_move_absolute_z(self):
        self.m_worker.sig_to_move_absolute_z.emit(c_double(self.sbox_move_z.value()))

    @QPSLObjectBase.log_decorator()
    def start_polling(self):
        self.timer.start(100)

    @QPSLObjectBase.log_decorator()
    def refresh_pos(self):
        self.m_worker.get_position()
        self.sbox_pos_x.setValue(self.m_worker.x_pos)
        self.sbox_pos_y.setValue(self.m_worker.y_pos)
        self.sbox_pos_z.setValue(self.m_worker.z_pos)

    @QPSLObjectBase.log_decorator()
    def plot_init(self):
        # self.position_3d = QPSLOpenGLWidget()
        self.position_3d.opts['distance'] = 100
        gx = gl.GLGridItem()
        gx.setSize(50, 50, 50)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-25, 0, 0)
        self.position_3d.addItem(gx)
        gy = gl.GLGridItem()
        gy.setSize(50, 50, 50)
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -25, 0)
        self.position_3d.addItem(gy)
        gz = gl.GLGridItem()
        gz.setSize(50, 50, 50)
        gz.translate(0, 0, -25)
        self.position_3d.addItem(gz)
        
    @QPSLObjectBase.log_decorator()
    def plot_position(self):
        self.m_worker.get_position()
        # self._position = np.empty((1, 3))
        # self.position = np.append(self._position, [[self.x_pos-25, self.y_pos-25, self.z_pos-25]], axis=0)
        self.position = np.array([[self.m_worker.x_pos-25, self.m_worker.y_pos-25, self.m_worker.z_pos-25]])        
        self.pos_plot = gl.GLScatterPlotItem(pos=self.position, color=(1.0, 1.0, 1.0, 1))
        self.position_3d.addItem(self.pos_plot)
        sleep_for(200)
        self.position_3d.removeItem(self.pos_plot) 

    @QPSLObjectBase.log_decorator()
    def mark_point(self):
        self.marked_point_number += 1
        self.marked_point = np.array([[self.sbox_pos_x.value()-25, self.sbox_pos_y.value()-25, self.sbox_pos_z.value()-25]])
        self.mark_plot = gl.GLScatterPlotItem(pos=self.marked_point, color=(1.0, 0.0, 0.0, 1))
        self.position_3d.addItem(self.mark_plot)
        print("Marked point {0} position ({1}, {2}, {3})".format(
            self.marked_point_number, self.sbox_pos_x.value(), self.sbox_pos_y.value(), self.sbox_pos_z.value()))
    
    @QPSLObjectBase.log_decorator()
    def init_scan(self):
        self.m_worker.sig_to_init_scan.emit(c_double(self.sbox_acc_x.value()),
                                            c_double(self.sbox_acc_y.value()),
                                            c_double(self.sbox_acc_z.value()),
                                            c_double(self.sbox_vel_x.value()),
                                            c_double(self.sbox_vel_y.value()),
                                            c_double(self.sbox_vel_z.value()),
                                            c_double(self.sbox_min_x.value()),
                                            c_double(self.sbox_min_y.value()),
                                            c_double(self.sbox_min_z.value()))
    
    @QPSLObjectBase.log_decorator()
    def start_scan(self):
        self.m_worker.sig_to_start_scan.emit(c_double(self.sbox_max_x.value()),
                                             c_double(self.sbox_min_x.value()),
                                            c_double(self.sbox_interval_x.value()),
                                            c_double(self.sbox_max_y.value()),
                                            c_double(self.sbox_min_y.value()),
                                            c_double(self.sbox_interval_y.value()),
                                            c_double(self.sbox_max_z.value()),
                                            c_double(self.sbox_min_z.value()),
                                            c_double(self.sbox_acc_z.value()),
                                            c_double(self.sbox_vel_z.value()))

    @QPSLObjectBase.log_decorator()
    def utils_capturing_times(self):
        self.uniform_motion_time = 1000*(self.sbox_max_z.value()-self.sbox_min_z.value()-(self.sbox_vel_z.value()**2/self.sbox_acc_z.value()))/self.sbox_vel_z.value()
        self.text_caputuring_number.setText(str(math.ceil(self.uniform_motion_time/self.sbox_exposure_time.value())))


MainWidget = Thorlabs_MTS50PluginUI