from QPSLClass.Base import *

BMC_MAX_PATH = 260
BMC_SERIAL_NUMBER_LEN = 11
MAX_DM_SIZE = 4096


class c_DM_PRIV(Structure):
    pass


c_DM_PRIV_P = POINTER(c_DM_PRIV)


class c_DM_DRIVER(Structure):
    _fields_ = [
        ('channel_count', c_uint),
        ('serial_number', c_char * (BMC_SERIAL_NUMBER_LEN + 1)),
        ('reversed', c_uint * 7),
    ]


class c_DM(Structure):
    _fields_ = [('Driver_Type', c_uint),
                ('DevId', c_uint), ('HVA_Type', c_uint), ('use_fiber', c_uint),
                ('use_CL', c_uint), ('burst_mode', c_uint),
                ('fiber_mode', c_uint), ('ActCount', c_uint),
                ('MaxVoltage', c_uint), ('VoltageLimit', c_uint),
                ('mapping', c_char * BMC_MAX_PATH),
                ('inactive', c_uint * MAX_DM_SIZE),
                ('profiles_path', c_char * BMC_MAX_PATH),
                ('maps_path', c_char * BMC_MAX_PATH),
                ('cals_path', c_char * BMC_MAX_PATH),
                ('cal', c_char * BMC_MAX_PATH),
                ('serial_number', c_char * (BMC_SERIAL_NUMBER_LEN + 1)),
                ('driver', c_DM_DRIVER), ('priv', c_DM_PRIV_P)]


c_DM_P = POINTER(c_DM)
c_char_p_p = POINTER(c_char_p)
c_double_p = POINTER(c_double)
c_int_p = POINTER(c_int)
c_uint32_p = POINTER(c_uint32)

try:
    _library = load_dll("QPSL_DM.dll")
except BaseException as e:
    loading_error(e)
try:
    _QPSL_BMCOpen = getattr(_library, "QPSL_BMCOpen")
    _QPSL_BMCOpen.argtypes = [c_DM_P, c_char_p, c_int_p, c_char_p]
    _QPSL_BMCOpen.restype = c_bool
except:
    loading_error("failed to load function {0}".format("QPSL_BMCOpen"))
try:
    _QPSL_BMCClose = getattr(_library, "QPSL_BMCClose")
    _QPSL_BMCClose.argtypes = [c_DM_P, c_int_p, c_char_p]
    _QPSL_BMCClose.restype = c_bool
except:
    loading_error("failed to load function {0}".format("QPSL_BMCClose"))
try:
    _QPSL_BMCLoadMap = getattr(_library, "QPSL_BMCLoadMap")
    _QPSL_BMCLoadMap.argtypes = [c_DM_P, c_uint32_p, c_int_p, c_char_p]
    _QPSL_BMCLoadMap.restype = c_bool
except:
    loading_error("failed to load function {0}".format("QPSL_BMCLoadMap"))
try:
    _QPSL_BMCSetArray = getattr(_library, "QPSL_BMCSetArray")
    _QPSL_BMCSetArray.argtypes = [
        c_DM_P, c_double_p, c_uint32_p, c_int_p, c_char_p
    ]
    _QPSL_BMCSetArray.restype = c_bool
except:
    loading_error("failed to load function {0}".format("QPSL_BMCSetArray"))
try:
    _QPSL_BMCErrorString = getattr(_library, "QPSL_BMCErrorString")
    _QPSL_BMCErrorString.argtypes = [c_int, c_char_p]
    _QPSL_BMCErrorString.restype = c_bool
except:
    loading_error("failed to load function {0}".format("QPSL_BMCErrorString"))


class DMController:

    def __init__(self) -> None:
        self.m_state = False
        self.m_map_loaded = False
        self.m_dm = c_DM()
        self.m_map_lut = (c_uint32 * 4096)()

    def get_state(self):
        return self.m_state

    def BMCOpen(self, serial_number: str) -> Tuple[bool, int, str]:
        assert not self.m_state
        serial_number_buffer = ctypes.create_string_buffer(
            init=serial_number.encode("utf8"))
        error_code = c_int(value=0)
        error_buffer = ctypes.create_string_buffer(init=1024, size=1024)
        res: c_bool = _QPSL_BMCOpen(byref(self.m_dm), serial_number_buffer,
                                    byref(error_code), error_buffer)
        if res:
            self.m_state = True
            self.m_map_loaded = False
        return res, error_code, bytes.decode(error_buffer.value,
                                             encoding='utf8')

    def BMCClose(self) -> Tuple[bool, int, str]:
        assert self.m_state
        error_code = c_int(value=0)
        error_buffer = ctypes.create_string_buffer(init=1024, size=1024)
        res: c_bool = _QPSL_BMCClose(byref(self.m_dm), byref(error_code),
                                     error_buffer)
        if res:
            self.m_state = False
        return res, error_code, bytes.decode(error_buffer.value,
                                             encoding='utf8')

    def is_opened(self):
        return self.m_state

    def BMCLoadMap(self) -> Tuple[bool, int, str]:
        assert self.m_state
        error_code = c_int(value=0)
        error_buffer = ctypes.create_string_buffer(init=1024, size=1024)
        try:
            res: c_bool = _QPSL_BMCLoadMap(byref(self.m_dm), self.m_map_lut,
                                           byref(error_code), error_buffer)
            if res:
                self.m_map_loaded = True
            return res, error_code, bytes.decode(error_buffer.value,
                                                 encoding='utf8')
        except OSError as e:
            loading_error(e)
            return False, -1, str(e)

    def is_map_loaded(self):
        assert self.m_state
        return self.m_map_loaded

    def BMCSetArray(self, double_arr: List[float]):
        assert self.m_state
        assert self.m_map_loaded
        value_array = (c_double * len(double_arr))(*double_arr)
        error_code = c_int(value=0)
        error_buffer = ctypes.create_string_buffer(init=1024, size=1024)
        try:
            res: c_bool = _QPSL_BMCSetArray(byref(self.m_dm),
                                            value_array, self.m_map_lut,
                                            byref(error_code), error_buffer)
            return res, error_code, bytes.decode(error_buffer.value,
                                                 encoding='utf8')
        except OSError as e:
            loading_error(e)
            return False, -1, str(e)

    def translate_error_code(self, error_code: int):
        error_buffer = ctypes.create_string_buffer(init=1024, size=1024)
        res: c_bool = _QPSL_BMCErrorString(error_code, error_buffer)
        return res, error_code, bytes.decode(error_buffer.value,
                                             encoding='utf8')
