from QPSLClass.Base import*

DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123


class DAQmxDigitalOutputChannel(Structure):
    _fields_ = [('physical_line_name',c_char * 256)]

c_DAQmxDigitalOutputChannel_p = POINTER(DAQmxDigitalOutputChannel)

class DAQmxDigitalOutputTask(Structure):
    _fields_ =[('handle', c_void_p),
                ('channels', c_DAQmxDigitalOutputChannel_p),
                ('line_number', c_uint32),
                ('trigger_source', c_char * 1024), ('sample_rate', c_double),
                ('sample_mode', c_int32), ('sample_per_channel', c_int32),
                ('error_code', c_int32), ('error_buffer', c_char * 1024)]
    
    def init_task(self) -> int:
        _QPSL_DAQmxDO_init(pointer(self))
        if self.error_code:
            raise BaseException(bytes.decode(self.error_buffer,encoding='utf8'))
        return self.error_code
    
    def register_everyn_callback(self, everyn: int, callback: Callable,
                                 callback_data: c_void_p) -> int:
        _QPSL_DAQmxDO_register_everyn_callback(pointer(self), everyn, callback,
                                               callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code
    
    def register_done_callback(self, callback: Callable,
                               callback_data: c_void_p) -> int:
        _QPSL_DAQmxDO_register_done_callback(pointer(self), callback,
                                             callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code
    
    def write_data(self,arr2d:np.ndarray) ->Tuple[int,c_int32]:
        assert arr2d.shape[0] == self.line_number
        assert arr2d.shape[1] == self.sample_per_channel
        num_of_written = c_int32()
        arr = arr2d.reshape(arr2d.shape[0] *arr2d.shape[1])
        buffer = (c_uint8 *len(arr))(*arr)
        # print(arr)
        # print(buffer)
        _QPSL_DAQmxWriteDigitalLines(byref(self),byref(num_of_written),buffer)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return num_of_written.value,self.error_code
    
    def get_buffer_size(self) -> Tuple[int,c_uint32]:
        size = c_int32()
        _QPSL_DAQmxGetBufOutputBufSize(byref(self),byref(size))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return size.value
    
    def start_task(self) -> int:
        _QPSL_DAQmxDO_start(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code
    
    def stop_task(self) -> int:
        _QPSL_DAQmxDO_stop(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code
    
    def clear_task(self) -> int:
        _QPSL_DAQmxDO_clear(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code
    
    def reset(self) -> int:
        num_of_written =c_int32(100)
        arr2d = np.zeros((self.line_number,50),dtype=int)
        arr = arr2d.reshape(arr2d.shape[0] * arr2d.shape[1])
        buffer = (c_uint8 * len(arr))(*arr)
        _QPSL_DAQmxDO_init(pointer(self))
        _QPSL_DAQmxWriteDigitalLines(byref(self), byref(num_of_written), buffer)
        _QPSL_DAQmxDO_start(pointer(self))
        _QPSL_DAQmxDO_stop(pointer(self))
        _QPSL_DAQmxDO_clear(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def has_handle(self) -> bool:
        return self.handle

    def has_handle(self) -> bool:
        return self.handle

c_DAQmxDigitalOutputTask_p = POINTER(DAQmxDigitalOutputTask)

c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)
c_uint8_p = POINTER(c_uint8)

try:
    _library = load_dll("QPSL_NIDAQDO.dll")
except BaseException as e:
    loading_error(e)
try:
    _QPSL_DAQmxGetErrorString = getattr(_library, "QPSL_DAQmxGetErrorString")
    _QPSL_DAQmxGetErrorString.argtypes = [c_int32, c_char_p, c_uint32]
    _QPSL_DAQmxGetErrorString.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetErrorString"))
try:
    _QPSL_DAQmxGetExtendedErrorInfo = getattr(
        _library, "QPSL_DAQmxGetExtendedErrorInfo")
    _QPSL_DAQmxGetExtendedErrorInfo.argtypes = [c_char_p, c_uint32]
    _QPSL_DAQmxGetExtendedErrorInfo.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetExtendedErrorInfo"))
try:
    _QPSL_DAQmxGetDeviceList = getattr(_library, "QPSL_DAQmxGetDeviceList")
    _QPSL_DAQmxGetDeviceList.argtypes = [c_char_p, c_int32, c_char_p, c_uint32]
    _QPSL_DAQmxGetDeviceList.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetDeviceList"))
try:
    _QPSL_DAQmxGetDevTerminals = getattr(_library, "QPSL_DAQmxGetDevTerminals")
    _QPSL_DAQmxGetDevTerminals.argtypes = [
        c_char_p, c_char_p, c_int32, c_char_p, c_uint32
    ]
    _QPSL_DAQmxGetDevTerminals.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetDevTerminals"))
try:
    _QPSL_DAQmxGetDOLineList = getattr(_library,
                                          "QPSL_DAQmxGetDOLineList")
    _QPSL_DAQmxGetDOLineList.argtypes = [
        c_char_p, c_char_p, c_int32, c_char_p, c_uint32
    ]
    _QPSL_DAQmxGetDOLineList.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetDOlineList"))
try:
    _QPSL_DAQmxDO_init = getattr(_library, "QPSL_DAQmxDO_init")
    _QPSL_DAQmxDO_init.argtypes = [c_DAQmxDigitalOutputTask_p]
    _QPSL_DAQmxDO_init.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxDO_init"))
try:
    _QPSL_DAQmxDO_register_everyn_callback = getattr(
        _library, "QPSL_DAQmxDO_register_everyn_callback")
    _QPSL_DAQmxDO_register_everyn_callback.argtypes = [
        c_DAQmxDigitalOutputTask_p, c_uint32, c_void_p, c_void_p
    ]
    _QPSL_DAQmxDO_register_everyn_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxDO_register_everyn_callback"))
try:
    _QPSL_DAQmxDO_register_done_callback = getattr(
        _library, "QPSL_DAQmxDO_register_done_callback")
    _QPSL_DAQmxDO_register_done_callback.argtypes = [
        c_DAQmxDigitalOutputTask_p, c_void_p, c_void_p
    ]
    _QPSL_DAQmxDO_register_done_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxDO_register_done_callback"))
try:
    _QPSL_DAQmxWriteDigitalLines = getattr(_library,"QPSL_DAQmxWriteDigitalLines")
    _QPSL_DAQmxWriteDigitalLines.argtypes = [
        c_DAQmxDigitalOutputTask_p, c_int32_p, c_uint8_p
    ]
    _QPSL_DAQmxWriteDigitalLines.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxWriteDigitalLines"))
try:
    _QPSL_DAQmxGetBufOutputBufSize = getattr(_library,
                                             "QPSL_DAQmxGetBufOutputBufSize")
    _QPSL_DAQmxGetBufOutputBufSize.argtypes = [
        c_DAQmxDigitalOutputTask_p, c_uint32_p
    ]
    _QPSL_DAQmxGetBufOutputBufSize.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetBufOutputBufSize"))
try:
    _QPSL_DAQmxDO_start = getattr(_library, "QPSL_DAQmxDO_start")
    _QPSL_DAQmxDO_start.argtypes = [c_DAQmxDigitalOutputTask_p]
    _QPSL_DAQmxDO_start.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxDO_start"))
try:
    _QPSL_DAQmxDO_stop = getattr(_library, "QPSL_DAQmxDO_stop")
    _QPSL_DAQmxDO_stop.argtypes = [c_DAQmxDigitalOutputTask_p]
    _QPSL_DAQmxDO_stop.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxDO_stop"))
try:
    _QPSL_DAQmxDO_clear = getattr(_library, "QPSL_DAQmxDO_clear")
    _QPSL_DAQmxDO_clear.argtypes = [c_DAQmxDigitalOutputTask_p]
    _QPSL_DAQmxDO_clear.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxDO_clear"))

def DAQmxGetErrorString(error_code: int,
                        error_buffer_len=1024) -> Tuple[int, str]:
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetErrorString(error_code, error_buffer, error_buffer_len)
    return res, bytes.decode(error_buffer.value, encoding='utf8')


def DAQmxGetExtendedErrorInfo(error_buffer_len=1024) -> Tuple[int, str]:
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetExtendedErrorInfo(error_buffer, error_buffer_len)
    return res, bytes.decode(error_buffer.value, encoding='utf8')


def DAQmxGetDeviceList(name_buffer_len=1024,
                       error_buffer_len=1024) -> Tuple[int, List[str], str]:
    name_buffer = ctypes.create_string_buffer(init=name_buffer_len,
                                              size=name_buffer_len)
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetDeviceList(name_buffer, name_buffer_len, error_buffer,
                                   error_buffer_len)
    return res, list(
        map(str.strip,
            bytes.decode(name_buffer.value,
                         encoding='utf8').split(','))), bytes.decode(
                             error_buffer.value, encoding='utf8')


def DAQmxGetDOLineList(device_name: str,
                          name_buffer_len=1024,
                          error_buffer_len=1024) -> Tuple[int, List[str], str]:
    device_name = ctypes.create_string_buffer(init=device_name.encode('utf8'))
    name_buffer = ctypes.create_string_buffer(init=name_buffer_len,
                                              size=name_buffer_len)
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetDOLineList(device_name, name_buffer,
                                      name_buffer_len, error_buffer,
                                      error_buffer_len)
    return res, list(
        map(str.strip,
            bytes.decode(name_buffer.value,
                         encoding='utf8').split(','))), bytes.decode(
                             error_buffer.value, encoding='utf8')


def DAQmxGetTerminalList(device_name: str,
                         terminal_buffer_len=4096,
                         error_buffer_len=1024) -> Tuple[int, List[str], str]:
    device_name = ctypes.create_string_buffer(init=device_name.encode('utf8'))
    terminal_buffer = ctypes.create_string_buffer(init=terminal_buffer_len,
                                                  size=terminal_buffer_len)
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetDevTerminals(device_name, terminal_buffer,
                                     terminal_buffer_len, error_buffer,
                                     error_buffer_len)
    return res, list(
        map(str.strip,
            bytes.decode(terminal_buffer.value,
                         encoding='utf8').split(','))), bytes.decode(
                             error_buffer.value, encoding='utf8')