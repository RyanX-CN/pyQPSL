from QPSLClass.Base import *

DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123


class DAQmxAnalogInputChannel(Structure):
    _fields_ = [('physical_channel_name', c_char * 256)]


c_DAQmxAnalogInputChannel_p = POINTER(DAQmxAnalogInputChannel)


class DAQmxAnalogInputTask(Structure):
    _fields_ = [('handle', c_void_p),
                ('channels', c_DAQmxAnalogInputChannel_p),
                ('channel_number', c_uint32),
                ('trigger_source', c_char * 1024), ('sample_rate', c_double),
                ('sample_mode', c_int32), ('sample_per_channel', c_int32),
                ('min_val', c_double), ('max_val', c_double),
                ('error_code', c_int32), ('error_buffer', c_char * 1024)]

    def init_task(self, channel_names: List[str], sample_rate: int,
                  sample_number: int, min_val: float, max_val: float) -> int:
        channel_number = len(channel_names)
        c_channels = (DAQmxAnalogInputChannel * channel_number)()
        for i, channel_name in enumerate(channel_names):
            c_channels[i].physical_channel_name = channel_name.encode('utf8')
        self.channels = c_channels
        self.channel_number = channel_number
        self.sample_rate = sample_rate
        self.min_val = min_val
        self.max_val = max_val
        if sample_number:
            self.sample_mode = DAQmx_Val_FiniteSamps
        else:
            self.sample_mode = DAQmx_Val_ContSamps
        self.sample_per_channel = sample_number
        _QPSL_DAQmxAI_init(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def register_everyn_callback(self, everyn: int, callback: Callable,
                                 callback_data: c_void_p) -> int:
        _QPSL_DAQmxAI_register_everyn_callback(pointer(self), everyn, callback,
                                               callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def unregister_everyn_callback(self) -> int:
        _QPSL_DAQmxAI_register_everyn_callback(pointer(self), 0, c_void_p(),
                                               c_void_p())
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def register_done_callback(self, callback: Callable,
                               callback_data: c_void_p) -> int:
        _QPSL_DAQmxAI_register_done_callback(pointer(self), callback,
                                             callback_data)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def read_data(self, read_per_channel: int) -> Tuple[int, np.ndarray]:
        num_of_read_per_channel = c_int32()
        buffer = (c_double * (read_per_channel * self.channel_number))()
        _QPSL_DAQmxReadAnalogF64(byref(self), byref(num_of_read_per_channel),
                                 buffer,
                                 read_per_channel * self.channel_number,
                                 read_per_channel)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        assert num_of_read_per_channel.value == read_per_channel
        return self.error_code, np.array(buffer).reshape(
            (self.channel_number, num_of_read_per_channel.value))

    def get_buffer_size(self) -> Tuple[int, c_uint32]:
        data = c_uint32()
        _QPSL_DAQmxGetBufInputBufSize(byref(self), byref(data))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code, data

    def set_buffer_size(self, buffer_size: int) -> int:
        _QPSL_DAQmxSetBufInputBufSize(byref(self), buffer_size)
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def clear_task(self) -> int:
        _QPSL_DAQmxAI_clear(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def start_task(self) -> int:
        _QPSL_DAQmxAI_start(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def stop_task(self) -> int:
        _QPSL_DAQmxAI_stop(pointer(self))
        if self.error_code:
            raise BaseException(
                bytes.decode(self.error_buffer, encoding='utf8'))
        return self.error_code

    def has_handle(self) -> bool:
        return self.handle


c_DAQmxAnalogInputTask_p = POINTER(DAQmxAnalogInputTask)
c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)

try:
    _library = load_dll("QPSL_NIDAQmxAI.dll")
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
    _QPSL_DAQmxGetAIChannelList = getattr(_library,
                                          "QPSL_DAQmxGetAIChannelList")
    _QPSL_DAQmxGetAIChannelList.argtypes = [
        c_char_p, c_char_p, c_int32, c_char_p, c_uint32
    ]
    _QPSL_DAQmxGetAIChannelList.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetAIChannelList"))
try:
    _QPSL_DAQmxAI_init = getattr(_library, "QPSL_DAQmxAI_init")
    _QPSL_DAQmxAI_init.argtypes = [c_DAQmxAnalogInputTask_p]
    _QPSL_DAQmxAI_init.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAI_init"))
try:
    _QPSL_DAQmxAI_start = getattr(_library, "QPSL_DAQmxAI_start")
    _QPSL_DAQmxAI_start.argtypes = [c_DAQmxAnalogInputTask_p]
    _QPSL_DAQmxAI_start.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAI_start"))
try:
    _QPSL_DAQmxAI_stop = getattr(_library, "QPSL_DAQmxAI_stop")
    _QPSL_DAQmxAI_stop.argtypes = [c_DAQmxAnalogInputTask_p]
    _QPSL_DAQmxAI_stop.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAI_stop"))
try:
    _QPSL_DAQmxAI_clear = getattr(_library, "QPSL_DAQmxAI_clear")
    _QPSL_DAQmxAI_clear.argtypes = [c_DAQmxAnalogInputTask_p]
    _QPSL_DAQmxAI_clear.restype = c_int32
except:
    loading_error("failed to load function {0}".format("QPSL_DAQmxAI_clear"))
try:
    _QPSL_DAQmxAI_register_everyn_callback = getattr(
        _library, "QPSL_DAQmxAI_register_everyn_callback")
    _QPSL_DAQmxAI_register_everyn_callback.argtypes = [
        c_DAQmxAnalogInputTask_p, c_uint32, c_void_p, c_void_p
    ]
    _QPSL_DAQmxAI_register_everyn_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxAI_register_everyn_callback"))
try:
    _QPSL_DAQmxAI_register_done_callback = getattr(
        _library, "QPSL_DAQmxAI_register_done_callback")
    _QPSL_DAQmxAI_register_done_callback.argtypes = [
        c_DAQmxAnalogInputTask_p, c_void_p, c_void_p
    ]
    _QPSL_DAQmxAI_register_done_callback.restype = c_int32
except:
    loading_error("failed to load function {0}".format(
        "QPSL_DAQmxAI_register_done_callback"))
try:
    _QPSL_DAQmxReadAnalogF64 = getattr(_library, "QPSL_DAQmxReadAnalogF64")
    _QPSL_DAQmxReadAnalogF64.argtypes = [
        c_DAQmxAnalogInputTask_p, c_int32_p, c_double_p, c_uint32, c_int32
    ]
    _QPSL_DAQmxReadAnalogF64.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxReadAnalogF64"))
try:
    _QPSL_DAQmxGetBufInputBufSize = getattr(_library,
                                            "QPSL_DAQmxGetBufInputBufSize")
    _QPSL_DAQmxGetBufInputBufSize.argtypes = [
        c_DAQmxAnalogInputTask_p, c_uint32_p
    ]
    _QPSL_DAQmxGetBufInputBufSize.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxGetBufInputBufSize"))
try:
    _QPSL_DAQmxSetBufInputBufSize = getattr(_library,
                                            "QPSL_DAQmxSetBufInputBufSize")
    _QPSL_DAQmxSetBufInputBufSize.argtypes = [
        c_DAQmxAnalogInputTask_p, c_uint32
    ]
    _QPSL_DAQmxSetBufInputBufSize.restype = c_int32
except:
    loading_error(
        "failed to load function {0}".format("QPSL_DAQmxSetBufInputBufSize"))


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


def DAQmxGetAIChannelList(device_name: str,
                          name_buffer_len=1024,
                          error_buffer_len=1024) -> Tuple[int, List[str], str]:
    device_name = ctypes.create_string_buffer(init=device_name.encode('utf8'))
    name_buffer = ctypes.create_string_buffer(init=name_buffer_len,
                                              size=name_buffer_len)
    error_buffer = ctypes.create_string_buffer(init=error_buffer_len,
                                               size=error_buffer_len)
    res = _QPSL_DAQmxGetAIChannelList(device_name, name_buffer,
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
