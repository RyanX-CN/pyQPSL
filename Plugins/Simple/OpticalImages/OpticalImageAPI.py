from QPSLClass.Base import *

c_uint16_p = POINTER(c_uint16)
c_bool_p = POINTER(c_bool)


class c_Divisor(Structure):
    _fields_ = [('m_width', c_int), ('m_height', c_int),
                ('m_down_ratio', c_int), ('m_down_width', c_int),
                ('m_down_height', c_int), ('m_binary_th', c_int),
                ('m_radius', c_int), ('m_buffer', c_uint16_p),
                ('m_down_buffer', c_uint16_p), ('m_mask', c_bool_p)]


c_char_p_p = POINTER(c_char_p)
c_double_p = POINTER(c_double)
c_int_p = POINTER(c_int)
c_uint32_p = POINTER(c_uint32)

try:
    _library = load_dll("QPSL_OpticalImagesDivision.dll")
except BaseException as e:
    loading_error(e)
try:
    _QPSL_Divisor_run = getattr(_library, "QPSL_Divisor_run")
    _QPSL_Divisor_run.argtypes = [c_void_p]
    _QPSL_Divisor_run.restype = c_int
except:
    loading_error("failed to load function {0}".format("QPSL_Divisor_run"))
try:
    _QPSL_Divisor_get_edge_by_mask = getattr(_library,
                                             "QPSL_Divisor_get_edge_by_mask")
    _QPSL_Divisor_get_edge_by_mask.argtypes = [
        c_bool_p, c_bool_p, c_int, c_int, c_int
    ]
    _QPSL_Divisor_get_edge_by_mask.restype = c_int
except:
    loading_error(
        "failed to load function {0}".format("QPSL_Divisor_get_edge_by_mask"))


class Divisor_16:

    def __init__(self) -> None:
        self.m_divisor = c_Divisor()

    def set_buffer(self, height: int, width: int, divide_down_ratio: int):
        self.m_divisor.m_height = height
        self.m_divisor.m_width = width
        self.m_divisor.m_down_height = (height + divide_down_ratio -
                                        1) // divide_down_ratio
        self.m_divisor.m_down_width = (width + divide_down_ratio -
                                       1) // divide_down_ratio
        self.m_divisor.m_buffer = (c_uint16 * (height * width))()
        self.m_divisor.m_down_buffer = (
            c_uint16 *
            (self.m_divisor.m_down_height * self.m_divisor.m_down_width))()
        self.m_divisor.m_mask = (
            c_bool * (self.m_divisor.m_height * self.m_divisor.m_width))()

    def set_graph_data(self, graph: np.ndarray):
        self.m_shape = graph.shape
        ctypes.memmove(self.m_divisor.m_buffer, c_void_p(graph.ctypes.data),
                       self.m_shape[0] * self.m_shape[1] * 2)

    def get_mask(self):
        arr = np.empty(shape=self.m_shape, dtype=bool)
        ctypes.memmove(c_void_p(arr.ctypes.data), self.m_divisor.m_mask,
                       self.m_shape[0] * self.m_shape[1])
        return arr

    def get_edge_by_mask(self, mask: np.ndarray):
        arr = np.zeros(shape=self.m_shape, dtype=bool)
        _QPSL_Divisor_get_edge_by_mask(arr.ctypes.data_as(c_bool_p),
                                       mask.ctypes.data_as(c_bool_p),
                                       mask.shape[0], mask.shape[1], 5)
        return arr

    def set_divide_down_ratio(self, divide_down_ratio: int):
        self.m_divisor.m_down_ratio = divide_down_ratio

    def set_binary_thresh(self, binary_thresh: int):
        self.m_divisor.m_binary_th = binary_thresh

    def set_radius(self, radius: int):
        self.m_divisor.m_radius = radius

    def run(self):
        res: c_int = _QPSL_Divisor_run(byref(self.m_divisor))
        return res
