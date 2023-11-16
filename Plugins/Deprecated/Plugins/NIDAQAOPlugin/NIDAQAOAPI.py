from QPSLClass.Base import *

DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123


class DAQmxAnalogOutputChannel(Structure):
    _fields_ = [('physical_channel_name', c_char * 256), ('min_val', c_double),
                ('max_val', c_double)]


c_DAQmxAnalogOutputChannel_p = POINTER(DAQmxAnalogOutputChannel)


class DAQmxAnalogOutputTask(Structure):
    _fields_ = [('handle', c_void_p),
                ('channels', c_DAQmxAnalogOutputChannel_p),
                ('channel_number', c_uint32),
                ('trigger_source', c_char * 1024), ('sample_rate', c_double),
                ('sample_mode', c_int32), ('sample_per_channel', c_int32),
                ('error_code', c_int32), ('error_buffer', c_char * 1024)]

    def init_task(self) -> int:
        _QPSL_DAQmxAO_init(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def register_everyn_callback(self, everyn: int, callback: Callable,
                                 callback_data: c_void_p) -> int:
        _QPSL_DAQmxAO_register_everyn_callback(pointer(self), everyn, callback,
                                               callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def register_done_callback(self, callback: Callable,
                               callback_data: c_void_p) -> int:
        _QPSL_DAQmxAO_register_done_callback(pointer(self), callback,
                                             callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def write_data(self, arr2d: np.ndarray) -> Tuple[int, c_int32]:
        assert arr2d.shape[0] == self.channel_number and arr2d.shape[
            1] == self.sample_per_channel
        num_of_writen = c_int32()
        arr = arr2d.reshape(arr2d.shape[0] * arr2d.shape[1])
        buffer = (c_double * len(arr))(*arr)
        _QPSL_DAQmxWriteAnalogF64(byref(self), byref(num_of_writen), buffer)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code, num_of_writen

    def get_buffer_size(self) -> Tuple[int, c_uint32]:
        data = c_uint32()
        _QPSL_DAQmxGetBufOutputBufSize(byref(self), byref(data))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code, data

    def clear_task(self) -> int:
        _QPSL_DAQmxAO_clear(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def start_task(self) -> int:
        _QPSL_DAQmxAO_start(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def stop_task(self) -> int:
        _QPSL_DAQmxAO_stop(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def has_handle(self) -> bool:
        return self.handle


c_DAQmxAnalogOutputTask_p = POINTER(DAQmxAnalogOutputTask)
c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)

try:
    _library = load_dll("QPSL_NIDAQAO.dll")
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
    _QPSL_DAQmxGetAOChannelList = getattr(_library,
                                          "QPSL_DAQmxGetAOChannelList")
    _QPSL_DAQmxGetAOChannelList.argtypes = [
        c_char_p, c_char_p, c_int32, c_char_p, c_uint32
    ]
    _QPSL_DAQmxGetAOChannelList.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetAOChannelList"))
try:
    _QPSL_DAQmxAO_init = getattr(_library, "QPSL_DAQmxAO_init")
    _QPSL_DAQmxAO_init.argtypes = [c_DAQmxAnalogOutputTask_p]
    _QPSL_DAQmxAO_init.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAO_init"))
try:
    _QPSL_DAQmxAO_start = getattr(_library, "QPSL_DAQmxAO_start")
    _QPSL_DAQmxAO_start.argtypes = [c_DAQmxAnalogOutputTask_p]
    _QPSL_DAQmxAO_start.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAO_start"))
try:
    _QPSL_DAQmxAO_stop = getattr(_library, "QPSL_DAQmxAO_stop")
    _QPSL_DAQmxAO_stop.argtypes = [c_DAQmxAnalogOutputTask_p]
    _QPSL_DAQmxAO_stop.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAO_stop"))
try:
    _QPSL_DAQmxAO_clear = getattr(_library, "QPSL_DAQmxAO_clear")
    _QPSL_DAQmxAO_clear.argtypes = [c_DAQmxAnalogOutputTask_p]
    _QPSL_DAQmxAO_clear.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAO_clear"))
try:
    _QPSL_DAQmxAO_register_everyn_callback = getattr(
        _library, "QPSL_DAQmxAO_register_everyn_callback")
    _QPSL_DAQmxAO_register_everyn_callback.argtypes = [
        c_DAQmxAnalogOutputTask_p, c_uint32, c_void_p, c_void_p
    ]
    _QPSL_DAQmxAO_register_everyn_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxAO_register_everyn_callback"))
try:
    _QPSL_DAQmxAO_register_done_callback = getattr(
        _library, "QPSL_DAQmxAO_register_done_callback")
    _QPSL_DAQmxAO_register_done_callback.argtypes = [
        c_DAQmxAnalogOutputTask_p, c_void_p, c_void_p
    ]
    _QPSL_DAQmxAO_register_done_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxAO_register_done_callback"))
try:
    _QPSL_DAQmxWriteAnalogF64 = getattr(_library, "QPSL_DAQmxWriteAnalogF64")
    _QPSL_DAQmxWriteAnalogF64.argtypes = [
        c_DAQmxAnalogOutputTask_p, c_int32_p, c_double_p
    ]
    _QPSL_DAQmxWriteAnalogF64.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxWriteAnalogF64"))
try:
    _QPSL_DAQmxGetBufOutputBufSize = getattr(_library,
                                             "QPSL_DAQmxGetBufOutputBufSize")
    _QPSL_DAQmxGetBufOutputBufSize.argtypes = [
        c_DAQmxAnalogOutputTask_p, c_uint32_p
    ]
    _QPSL_DAQmxGetBufOutputBufSize.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetBufOutputBufSize"))


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


def DAQmxGetAOChannelList(device_name: str,
                          name_buffer_len=1024,
                          error_buffer_len=1024) -> Tuple[int, List[str], str]:
    device_name = ctypes.create_string_buffer(init=device_name.encode('utf8'))
    name_buffer = ctypes.create_string_buffer(init=name_buffer_len,
                                              size=name_buffer_len)
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetAOChannelList(device_name, name_buffer,
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
