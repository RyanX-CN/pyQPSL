from QPSLClass.Base import *
from ctypes import c_byte, c_char

BUFFERSIZE = 16777216
DCAMERR_ABORT = -2147483390

class ImageData(Structure):
    _fields_ = [('buffer',c_byte * BUFFERSIZE),
                ('frame_id',c_int)]    
    
class DCAMWAIT_START(Structure):
    _fields_ = [('size',c_int32),
                ('eventhappened',c_int32),
                ('eventmask',c_int32),
                ('timeout',c_int32)]
    
class DCAM_TIMESTAMP(Structure):
    _fields_ = [('sec',c_uint32),
            ('microsec',c_int32)]
    
class DCAMBUF_FRAME(Structure):
    _fields_ = [('size',c_int32),
                ('iKind',c_int32),
                ('option',c_int32),
                ('iFrame',c_int32),
                ('buf',c_void_p),
                ('rowbytes',c_int32),
                ('type',c_int),
                ('width',c_int32),
                ('height',c_int32),
                ('left',c_int32),
                ('top',c_int32),
                ('timestamp',DCAM_TIMESTAMP),
                ('framestamp',c_int32),
                ('camerastamp',c_int32)]	

class DCAMController(Structure):
    _fields_ = [('hdcam',c_void_p),
                ('index',c_int32),
                ('hwait',c_void_p),
                ('hrec',c_void_p),
                ('waitstart',DCAMWAIT_START),
                ('bufframe',DCAMBUF_FRAME),
                ('save_path',c_char_p),
                ('err_code',c_int32), ('err_buffer',c_char * 1024)]
    
    def open_device(self):
        _QPSL_DCAM_open(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code

    def close_device(self):
        _QPSL_DCAM_close(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def get_cameraID(self) -> Tuple[int, c_char * 256]: # type: ignore
        id_string = ctypes.create_string_buffer(256)
        _QPSL_DCAM_getstring(pointer(self), id_string)
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code, id_string

    def get_temperature(self) -> Tuple[int, c_double]:
        temp_data = c_double()
        _QPSL_DCAM_getvalue(pointer(self), byref(temp_data))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code, temp_data    
    
    def set_ROI(self, hpos, vpos, hsize, vsize):
        _QPSL_DCAM_setROI(pointer(self), 
                          c_int32(hpos), c_int32(vpos), 
                          c_int32(hsize), c_int32(vsize))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_exposure_time(self, exposure_time):
        _QPSL_DCAM_setExposureTime(pointer(self), c_double(exposure_time))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
        
    def set_internal_trigger(self):
        _QPSL_DCAM_setInternalTrigger(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code

    def set_external_trigger(self):
        _QPSL_DCAM_setExternalTrigger(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_syncreadout(self):
        _QPSL_DCAM_setSyncReadout(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_trigger_positive(self):
        _QPSL_DCAM_setTriggerPositive(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_trigger_negative(self):
        _QPSL_DCAM_setTriggerNegative(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_trigger_delay(self, delay):
        _QPSL_DCAM_setTriggerDelay(pointer(self), c_double(delay/1000))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def set_bitwidth_8bit(self):
        _QPSL_DCAM_set8bit(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))                
        return self.err_code
    
    def set_bitwidth_16bit(self):
        _QPSL_DCAM_set16bit(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))                
        return self.err_code
    
    def capture(self):
        _QPSL_DCAM_Capture(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
        
    def get_single_frame_8bit(self, pyworker: c_void_p, callback: Callable):
        _QPSL_DCAM_Get_single_frame_8bit(pointer(self), pyworker, callback)
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def get_single_frame(self, pyworker: c_void_p, callback: Callable):
        _QPSL_DCAM_Get_single_frame(pointer(self), pyworker, callback)
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def pre_live(self):
        _QPSL_Live_pre_processer(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def post_live(self):
        _QPSL_Live_post_processer(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code
    
    def abort(self):
        _QPSL_DCAM_Abort(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code

    # def scan(self, endframe):
    #     _QPSL_DCAM_Scan(pointer(self),c_int(endframe))
    #     if self.err_code < 0:
    #         raise BaseException(
    #             bytes.decode(self.err_buffer, encoding='utf8'))
    #     return self.err_code

    def has_handle(self) ->bool:
        return self.hdcam
    
    def buffer_release(self):
        _QPSL_DCAM_bufferRelease(pointer(self))
        if self.err_code < 0:
            raise BaseException(
                bytes.decode(self.err_buffer, encoding='utf8'))
        return self.err_code

# Load .dll fuctions   
c_ImageData_p = POINTER(ImageData)
c_DCAMController_p = POINTER(DCAMController)
c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)

try:
    _library = load_dll("QPSL_DCAM.dll")
except BaseException as e:
    loading_error(e)

try:
    _QPSL_DCAMAPI_init = getattr(_library, "QPSL_DCAMAPI_init")
    _QPSL_DCAMAPI_init.argtypes = [c_char_p]
    _QPSL_DCAMAPI_init.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAMAPI_init"))

try:
    _QPSL_DCAMAPI_uninit = getattr(_library, "QPSL_DCAMAPI_uninit")
    _QPSL_DCAMAPI_uninit.argtypes = [c_char_p]
    _QPSL_DCAMAPI_uninit.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAMAPI_uninit"))

try:
    _QPSL_DCAM_open = getattr(_library, "QPSL_DCAM_open")
    _QPSL_DCAM_open.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_open.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_open"))

try:
    _QPSL_DCAM_close = getattr(_library, "QPSL_DCAM_close")
    _QPSL_DCAM_close.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_close.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_close"))

try:
    _QPSL_DCAM_getstring = getattr(_library, "QPSL_DCAM_getstring")
    _QPSL_DCAM_getstring.argtypes = [c_DCAMController_p, c_char_p]
    _QPSL_DCAM_getstring.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_getstring"))

try:
    _QPSL_DCAM_getvalue = getattr(_library, "QPSL_DCAM_getvalue")
    _QPSL_DCAM_getvalue.argtypes = [c_DCAMController_p, c_double_p]
    _QPSL_DCAM_getvalue.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_getvalue"))

try:
    _QPSL_DCAM_setROI = getattr(_library, "QPSL_DCAM_setROI")
    _QPSL_DCAM_setROI.argtypes = [
        c_DCAMController_p, c_int32, c_int32, c_int32, c_int32]
    _QPSL_DCAM_setROI.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setROI"))

try:
    _QPSL_DCAM_setExposureTime = getattr(_library, "QPSL_DCAM_setExposureTime")
    _QPSL_DCAM_setExposureTime.argtypes = [
        c_DCAMController_p, c_double]
    _QPSL_DCAM_setExposureTime.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setgetExposureTime"))

try:
    _QPSL_DCAM_setInternalTrigger = getattr(_library, "QPSL_DCAM_setInternalTrigger")
    _QPSL_DCAM_setInternalTrigger.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_setInternalTrigger.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setInternalTrigger")) 

try:
    _QPSL_DCAM_setExternalTrigger = getattr(_library, "QPSL_DCAM_setExternalTrigger")
    _QPSL_DCAM_setExternalTrigger.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_setExternalTrigger.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setExternalTrigger"))

try:
    _QPSL_DCAM_setSyncReadout = getattr(_library, "QPSL_DCAM_setSyncReadout")
    _QPSL_DCAM_setSyncReadout.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_setSyncReadout.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setSyncReadout"))

try:
    _QPSL_DCAM_setTriggerPositive = getattr(_library, "QPSL_DCAM_setTriggerPositive")
    _QPSL_DCAM_setTriggerPositive.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_setTriggerPositive.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setTriggerPositive"))

try:
    _QPSL_DCAM_setTriggerNegative = getattr(_library, "QPSL_DCAM_setTriggerNegative")
    _QPSL_DCAM_setTriggerNegative.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_setTriggerNegative.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setTriggerNegative"))

try:
    _QPSL_DCAM_setTriggerDelay = getattr(_library, "QPSL_DCAM_setTriggerDelay")
    _QPSL_DCAM_setTriggerDelay.argtypes = [c_DCAMController_p, c_double]
    _QPSL_DCAM_setTriggerDelay.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_setTriggerDelay"))

try:
    _QPSL_DCAM_set8bit = getattr(_library,"QPSL_DCAM_set8bit")
    _QPSL_DCAM_set8bit.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_set8bit.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_set8bit"))

try:
    _QPSL_DCAM_set16bit = getattr(_library,"QPSL_DCAM_set16bit")
    _QPSL_DCAM_set16bit.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_set16bit.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_set16bit"))

try:
    _QPSL_DCAM_bufferRelease = getattr(_library, "QPSL_DCAM_bufferRelease")
    _QPSL_DCAM_bufferRelease.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_bufferRelease.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_bufferRelease"))

try:
    _QPSL_DCAM_Capture = getattr(_library, "QPSL_DCAM_Capture")
    _QPSL_DCAM_Capture.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_Capture.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_Capture"))

try:
    _QPSL_DCAM_Get_single_frame_8bit = getattr(_library, "QPSL_DCAM_Get_single_frame_8bit")
    _QPSL_DCAM_Get_single_frame_8bit.argtypes = [c_DCAMController_p, c_void_p, c_void_p]
    _QPSL_DCAM_Get_single_frame_8bit.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_Get_single_frame_8bit"))

try:
    _QPSL_DCAM_Get_single_frame = getattr(_library, "QPSL_DCAM_Get_single_frame")
    _QPSL_DCAM_Get_single_frame.argtypes = [c_DCAMController_p, c_void_p, c_void_p]
    _QPSL_DCAM_Get_single_frame.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_Get_single_frame"))

try:
    _QPSL_Live_pre_processer = getattr(_library, "QPSL_Live_pre_processer")
    _QPSL_Live_pre_processer.argtypes = [c_DCAMController_p]
    _QPSL_Live_pre_processer.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_Live_pre_processer"))

try:
    _QPSL_Live_post_processer = getattr(_library, "QPSL_Live_post_processer")
    _QPSL_Live_post_processer.argtypes = [c_DCAMController_p]
    _QPSL_Live_post_processer.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_Live_post_processer"))

try:
    _QPSL_DCAM_Abort = getattr(_library, "QPSL_DCAM_Abort")
    _QPSL_DCAM_Abort.argtypes = [c_DCAMController_p]
    _QPSL_DCAM_Abort.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DCAM_Abort"))

# try:
#     _QPSL_DCAM_Scan = getattr(_library, "QPSL_DCAM_Scan")
#     _QPSL_DCAM_Scan.argtypes = [c_DCAMController_p, c_int]
#     _QPSL_DCAM_Scan.restype = c_int32
# except:
#     loading_error("failed to load function {0}".format("QPSL_DCAM_Scan"))

try:
    _Delete_Data_pointer = getattr(_library,"Delete_Data_pointer")
    _Delete_Data_pointer.argtypes = [c_void_p]
    _Delete_Data_pointer.restype = c_int32
except:
    loading_error("failed to load function {0}".format("Delete_Data_pointer"))

# DCAM_API init/uninit
def DCAMAPI_init(err_buffer_len=1024):
    err_buffer = ctypes.create_string_buffer(init=err_buffer_len,
                                             size=err_buffer_len)
    _QPSL_DCAMAPI_init(err_buffer)
    return bytes.decode(err_buffer.value, encoding='utf8')

def DCAMAPI_uninit(err_buffer_len=1024):
    err_buffer = ctypes.create_string_buffer(init=err_buffer_len,
                                             size=err_buffer_len)
    _QPSL_DCAMAPI_uninit(err_buffer)
    return bytes.decode(err_buffer.value, encoding='utf8')

def Delete_Data_pointer(ptr:c_void_p):
    _Delete_Data_pointer(ptr)

  

