from QPSLClass.Base import *


class c_Divisor(Structure):
    _fields_ = [('m_width', c_int), ('m_height', c_int),
                ('m_down_ratio', c_int), ('m_down_width', c_int),
                ('m_down_height', c_int), ('m_binary_th', c_int),
                ('m_radius', c_int), ('m_buffer', c_uint16 * 100000000),
                ('m_down_buffer', c_uint16 * 100000000)]


c_char_p_p = POINTER(c_char_p)
c_double_p = POINTER(c_double)
c_int_p = POINTER(c_int)
c_uint32_p = POINTER(c_uint32)

try:
    _library = load_dll("image_division.dll")
except BaseException as e:
    loading_error(e)
try:
    _QPSL_Divisor_run = getattr(_library, "QPSL_Divisor_run")
    _QPSL_Divisor_run.argtypes = [c_void_p]
    _QPSL_Divisor_run.restype = c_int
except:
    loading_error("failed to load function {0}".format("QPSL_Divisor_run"))

_global_divisor = c_Divisor()
_mutex = QMutex()


class Divisor:

    def set_graph_data(self, graph: np.ndarray):
        self.m_shape = graph.shape
        _mutex.lock()
        _global_divisor.m_height, _global_divisor.m_width = graph.shape
        ctypes.memmove(_global_divisor.m_buffer, c_void_p(graph.ctypes.data),
                       self.m_shape[0] * self.m_shape[1] * 2)

    def get_result_data(self):
        arr = np.zeros(shape=self.m_shape, dtype=np.uint16)
        ctypes.memmove(c_void_p(arr.ctypes.data), _global_divisor.m_buffer,
                       self.m_shape[0] * self.m_shape[1] * 2)
        _mutex.unlock()
        return arr

    def set_divide_down_ratio(self, divide_down_ratio: int):
        _global_divisor.m_down_ratio = divide_down_ratio

    def set_binary_thresh(self, binary_thresh: int):
        _global_divisor.m_binary_th = binary_thresh

    def set_radius(self, radius: int):
        _global_divisor.m_radius = radius

    def run(self):
        res: c_int = _QPSL_Divisor_run(byref(_global_divisor))
        return res
