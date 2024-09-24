import collections
import ctypes
import datetime
import decimal
import distutils.core
import enum
import glob
import importlib
import inspect
import itertools
import json
import math
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
import typing
import warnings
import weakref
import array
from collections import defaultdict, deque, namedtuple
from ctypes import byref, c_bool, c_char, c_char_p, c_double, c_int, c_int32, c_uint, c_uint8, c_uint16, c_uint32, c_void_p, c_ushort,c_ulong, pointer, py_object, sizeof, POINTER, Structure
from typing import Any, Callable, Dict, Generic, Generator, Iterable, Iterator, List, Mapping, NoReturn, Optional, Set, Tuple, TypeVar, Union
from Utils.Hooks import *
from multiprocessing import Manager


loading_warning("pyQPSL initializing...")
loading_info("python version = {0}".format(sys.version))
try:
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    loading_info("Qt version = {0}".format(QT_VERSION_STR))
    loading_info("PyQt version = {0}".format(PYQT_VERSION_STR))
except:
    loading_warning("PyQt version = ?")
loading_info("working directory = {0}".format(QPSL_Working_Directory))
from PyQt5.QtCore import pyqtBoundSignal, pyqtSignal, pyqtSlot, Q_ARG, Q_RETURN_ARG
from PyQt5.QtCore import QAbstractItemModel, QByteArray, QCoreApplication, QDir, QEvent, QEventLoop, QItemSelection, QItemSelectionModel
from PyQt5.QtCore import QMetaObject, QModelIndex, QMutex, QObject, QPoint, QPointF, QProcess, QPropertyAnimation, QRect, QRectF, QRegExp, QRunnable
from PyQt5.QtCore import QSettings, QSize, Qt, QThread, QThreadPool, QTimer, QTimerEvent, QUrl, QVariant,QFileInfo
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QAction, QActionGroup, QBoxLayout, QCheckBox, QColorDialog, QComboBox
from PyQt5.QtWidgets import QDesktopWidget, QDialog, QDialogButtonBox, QDockWidget, QDoubleSpinBox, QFileDialog, QFontComboBox, QFontDialog, QFrame
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsObject, QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGraphicsWidget
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHeaderView, QHBoxLayout, QLabel, QLayout, QLayoutItem, QLineEdit, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QMenu, QMenuBar, QMessageBox, QProgressBar, QProgressDialog, QPushButton, QRadioButton
from PyQt5.QtWidgets import QScrollArea, QScrollBar, QShortcut, QSizePolicy, QSlider, QSpacerItem, QSpinBox, QSplitter, QStatusBar, QStackedWidget, QStyleFactory
from PyQt5.QtWidgets import QTabBar, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit, QToolBox, QToolButton, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QActionEvent, QBrush, QCloseEvent, QContextMenuEvent, QFocusEvent, QHoverEvent, QMouseEvent, QMoveEvent, QPaintEvent, QResizeEvent, QShowEvent, QWheelEvent
from PyQt5.QtGui import QColor, QCursor, QDoubleValidator, QFont, QFontMetrics, QIcon, QImage, QIntValidator, QKeyEvent, QKeySequence, QLinearGradient
from PyQt5.QtGui import QMovie, QPainter, QPainterPath, QPalette, QPen, QPixmap, QRegExpValidator, QScreen, QStandardItem, QStandardItemModel, QValidator, QWindow
import numpy as np

loading_info("numpy version = {0}".format(np.__version__))
try:
    import Cython, Cython.Build
    loading_info("cython version = {0}".format(Cython.__version__))
except:
    loading_warning("no Cython")
try:
    import fitz, fitz.fitz, fitz.utils  # PyMuPDF 是 fitz 的必需
    loading_info("fitz version = {0}".format(fitz.version))
except:
    loading_warning("no fitz.")
try:
    import pyqtgraph
    loading_info("pyqtgraph version = {0}".format(pyqtgraph.__version__))
except:
    loading_warning("no pyqtgraph")
try:
    import qdarkstyle
    loading_info("qdarkstyle version = {0}".format(qdarkstyle.__version__))
except:
    loading_warning("no qdarkstyle")
try:
    import qt_material
    loading_info("qt_material version = {0}".format("unknown"))
except:
    loading_warning("no qt_material")
try:
    import tifffile
    loading_info("tifffile version = {0}".format(tifffile.__version__))
except:
    loading_warning("no tifffile")
try:
    import tqdm
    loading_info("tqdm version = {0}".format(tqdm.__version__))
except:
    loading_warning("no tqdm")
try:
    import win32api
    loading_info("win32api version = {0}".format("unknown"))
except:
    loading_warning("no win32api")
try:
    import win32comext, win32comext.shell.shell, win32comext.shell.shellcon
    loading_info("win32comext version = {0}".format("unknown"))
except:
    loading_warning("no win32comext")
try:
    import win32gui
    loading_info("win32gui version = {0}".format("unknown"))
except:
    loading_warning("no win32gui")
try:
    import cupy as cp
    loading_info("cupy verision = {0}".format(cp.__version__))
except:
    loading_warning("no cupy")


class SharedStateController:

    class State(enum.Enum):
        Stop = 0
        Continue = 1

    __slots__ = "m_value", "m_replied"
    """共享状态控制器

    当不同线程持有同一个共享状态控制器时，可以使用该对象进行开关控制

    当发送者设置信号后，可以将 m_replied 设为 False；接收者收到信号后，可以将 m_replied 设为 True，表示已阅
    """

    def __init__(self, value: 'SharedStateController.State' = State.Continue):
        self.m_value = value
        self.m_replied = True

    def set_continue(self):
        self.m_value = SharedStateController.State.Continue

    def set_continue_until_reply(self, interval_msec: int = 15):
        self.m_replied = False
        self.set_continue()
        while not self.is_replied():
            sleep_for(interval_msec)

    def set_stop(self):
        self.m_value = SharedStateController.State.Stop

    def set_stop_until_reply(self, interval_msec: int = 15):
        self.m_replied = False
        self.set_stop()
        while not self.is_replied():
            sleep_for(interval_msec)

    def is_continue(self) -> bool:
        return self.m_value == SharedStateController.State.Continue

    def is_stop(self) -> bool:
        return self.m_value == SharedStateController.State.Stop

    def get_value(self) -> State:
        return self.m_value

    def reply_receive(self):
        self.m_replied = True

    def is_replied(self) -> bool:
        return self.m_replied

    def reply_if_continue(self) -> bool:
        if self.is_continue():
            self.m_replied = True
            return True
        else:
            return False

    def reply_if_stop(self) -> bool:
        if self.is_stop():
            self.m_replied = True
            return True
        else:
            return False


#
def check_QPSLClass_topo(output=False):
    dir = "./QPSLClass"
    vertex = set()
    adj = defaultdict(list)
    deg = defaultdict(int)
    for file in filter(lambda s: s.startswith("QPSL"), os.listdir(dir)):
        cur = file.split('.')[0]
        pre = set()
        with open(f"{dir}/{file}", "rt", encoding="utf8") as f:
            for line in f.readlines():
                if line.startswith("from QPSL"):
                    pre.add(line.strip().split()[1].split('.')[1])
        pre.remove("Stable")
        for p in pre:
            adj[p].append(cur)
        deg[cur] += len(pre)
        vertex.add(cur)
        vertex |= pre
    Q = deque(x for x in vertex if deg[x] == 0)
    res = []
    while Q:
        p = Q.popleft()
        res.append(p)
        for q in adj[p]:
            deg[q] -= 1
            if deg[q] == 0:
                Q.append(q)
    if output:
        loading_info("sorted QPSLClass:", *res)
    return res


#
def check_update_log(dirs=("./QPSLClass", ), output=False):
    old_files = []
    new_files = []
    for dir in dirs:
        for file in os.listdir(dir):
            file = dir + "/" + file
            if os.path.isfile(file):
                with open(file, "rt", encoding='utf8') as f:
                    line = f.readlines()[1]
                    modify_time = datetime.datetime.fromtimestamp(
                        int(os.path.getmtime(file)))
                    if line.startswith("# @"):
                        mark_time = datetime.datetime.strptime(
                            line[23:42], "%Y-%m-%d %H:%M:%S")
                        if modify_time > mark_time:
                            dt = modify_time - mark_time
                            if dt > datetime.timedelta(minutes=1):
                                new_files.append(
                                    (mark_time, modify_time, file))
                    else:
                        old_files.append((modify_time, file))
    old_files.sort()
    new_files.sort()
    if output:
        loading_info("new files:")
        for t, t2, f in new_files:
            loading_info('{0:<40}{1}\t{2}'.format(get_pure_filename(f), t, t2))
        loading_info("old files:")
        for t, f in old_files:
            loading_info('{0:<40}{1}'.format(get_pure_filename(f), t))
    return new_files, old_files


def clipboard_getText():
    """获取剪贴板文本
    """
    return QApplication.clipboard().text()


def clipboard_setText(text: str):
    """将文本送到剪贴板

    Args:
        text (str): 要粘贴的文本
    """
    QApplication.clipboard().setText(text)


def connect_direct(signal: Union[pyqtSignal, pyqtBoundSignal],
                   slot: Union[Callable[..., None], pyqtBoundSignal]):
    """direct 方式连接信号槽

    以直接连接方式连接信号和槽，发出信号时直接调用槽函数。

    要求信号发出和槽函数执行在同一线程内。

    Args:
        signal (Union[pyqtSignal, pyqtBoundSignal]): 信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    pyqtBoundSignal.connect(signal, slot, Qt.ConnectionType.DirectConnection)


def connect_blocked(signal: Union[pyqtSignal, pyqtBoundSignal],
                    slot: Union[Callable[..., None], pyqtBoundSignal]):
    """ blocked 方式连接信号槽

    以阻塞队列方式连接信号和槽。
    
    发出信号时，通知另一线程调用槽函数，同时本线程进入阻塞状态；等到槽函数执行完毕时，本线程解除阻塞。

    要求信号发出和槽函数执行在不同线程内。

    Args:
        signal (Union[pyqtSignal, pyqtBoundSignal]): 信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    pyqtBoundSignal.connect(signal, slot,
                            Qt.ConnectionType.BlockingQueuedConnection)


def connect_queued(signal: Union[pyqtSignal, pyqtBoundSignal],
                   slot: Union[Callable[..., None], pyqtBoundSignal]):
    """ queued 方式连接信号槽

    以队列方式连接信号和槽。多用于信号发出和槽函数执行在不同线程内的情况。
    
    发出信号时，槽函数加入信号接收者所在的事件队列，本线程不会阻塞。

    Args:
        signal (Union[pyqtSignal, pyqtBoundSignal]): 信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    pyqtBoundSignal.connect(signal, slot, Qt.ConnectionType.QueuedConnection)


def connect_queued_and_blocked(queued_signal: Union[pyqtSignal,
                                                    pyqtBoundSignal],
                               blocked_signal: Union[pyqtSignal,
                                                     pyqtBoundSignal],
                               slot: Union[Callable[..., None],
                                           pyqtBoundSignal]):
    """同时建立 blocked 和 queued 方式的连接

    将异步信号进行 queued 连接；同步信号进行 blocked 连接。

    要求信号发出和槽函数执行位于不同线程。

    Args:
        queued_signal (Union[pyqtSignal, pyqtBoundSignal]): 异步信号
        blocked_signal (Union[pyqtSignal, pyqtBoundSignal]): 同步信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    connect_queued(queued_signal, slot)
    connect_blocked(blocked_signal, slot)


def connect_asynch_and_synch(asynch_signal: Union[pyqtSignal, pyqtBoundSignal],
                             synch_signal: Union[pyqtSignal, pyqtBoundSignal],
                             slot: Union[Callable[..., None],
                                         pyqtBoundSignal]):
    """同时建立异步和同步方式的连接

    异步信号进行 queued 连接；将同步信号进行 direct 连接。

    常用于 worker 内，信号和槽的连接

    Args:
        asynch_signal (Union[pyqtSignal, pyqtBoundSignal]): 异步信号
        synch_signal (Union[pyqtSignal, pyqtBoundSignal]): 同步信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    connect_queued(asynch_signal, slot)
    connect_direct(synch_signal, slot)


def convert_pdf_page_to_image(pdf_path: str,
                              page: int = int(0),
                              zoom: float = 4.0) -> QPixmap:
    """将 pdf 文件单页转换为 QPixmap

    _extended_summary_

    Args:
        pdf_path (str): pdf 文件路径
        page (int, optional): 要转换的页码， 0 表示第一页。 默认为 0
        zoom (float, optional): 放缩比率。默认为 4

    Returns:
        QPixmap: 生成的 QPixmap 对象
    """
    magnify = fitz.fitz.Matrix(zoom, zoom)
    doc = fitz.fitz.Document(pdf_path)
    pixmap = QPixmap()
    pixmap.loadFromData(
        fitz.utils.get_pixmap(doc[page], matrix=magnify).tobytes("PNG"), "PNG")
    return pixmap


def convert_pdf_to_images(pdf_path: str, zoom: float = 4) -> Iterator[QPixmap]:
    """将 pdf 文件单页转换为 QPixmap 生成器

    Args:
        pdf_path (str): pdf 文件路径
        zoom (float, optional): 放缩比率，默认为 4

    Yields:
        Iterator[QPixmap]: 返回一个生成若干个 QPixmap 对象的生成器
    """
    magnify = fitz.fitz.Matrix(zoom, zoom)
    doc = fitz.fitz.Document(pdf_path)
    for page in doc:
        pixmap = QPixmap()
        pixmap.loadFromData(
            fitz.utils.get_pixmap(page, matrix=magnify).tobytes("PNG"), "PNG")
        yield pixmap


def copy_dir(old_dir_path: str, new_dir_path: str) -> str:
    """整个拷贝一个文件夹

    Args:
        old_dir_path (str): 表示要复制的旧文件夹路径
        new_dir_path (str): 表示要复制到的新文件夹路径

    Returns:
        str: 返回新生成的文件夹路径
    """
    return shutil.copytree(old_dir_path, new_dir_path)


def copy_dir_by_each_file(
        old_dir_path: str,
        new_dir_path: str,
        dir_filter: Optional[Callable[[str, str], bool]] = None,
        file_filter: Optional[Callable[[str, str], bool]] = None,
        file_copy_func: Callable[[str, str], bool] = shutil.copy) -> str:
    """通过文件/文件夹逐个筛选复制，拷贝一个文件夹

    Args:
        old_dir_path (str): 表示要复制的旧文件夹路径
        new_dir_path (str): 表示要复制到的新文件夹路径
        dir_filter (Optional[Callable[[str, str], bool]], optional): 表示文件夹筛选条件。默认为 None，表示不筛选。
        file_filter (Optional[Callable[[str, str], bool]], optional): 表示文件筛选条件。默认为 None，表示不筛选。
        file_copy_func (Callable[[str, str], bool], optional): 表示负责文件复制的函数，默认为 shutil.copy。

    Returns:
        str: 返回新生成的文件夹路径
    """

    def dfs(old_dir_path, new_dir_path):
        if (not dir_filter) or dir_filter(old_dir_path, new_dir_path):
            if not os.path.exists(new_dir_path):
                os.makedirs(new_dir_path)
            for f in os.listdir(old_dir_path):
                f1 = old_dir_path + '/' + f
                f2 = new_dir_path + '/' + f
                if os.path.isfile(f1):
                    if (not file_filter) or file_filter(f1, f2):
                        file_copy_func(f1, f2)
                else:
                    dfs(f1, f2)

    dfs(old_dir_path=old_dir_path, new_dir_path=new_dir_path)
    return new_dir_path


def copy_file(old_file_path: str, new_file_path: str) -> str:
    """拷贝一个文件

    如果 new_file_path 已经存在，则会覆盖旧文件

    Args:
        old_file_path (str): 表示要复制的旧文件路径
        new_file_path (str): 表示要复制到的新文件路径

    Returns:
        str: 返回新生成的文件路径
    """
    return shutil.copy(old_file_path, new_file_path)


def disconnect(signal: Union[pyqtSignal, pyqtBoundSignal],
               slot: Union[Callable[..., None], pyqtBoundSignal]):
    """断开信号槽连接

    Args:
        signal (Union[pyqtSignal, pyqtBoundSignal]): 信号
        slot (Union[Callable[..., None], pyqtBoundSignal]): 槽函数
    """
    pyqtBoundSignal.disconnect(signal, slot)


def float_range(start: int, end: int, step: int,
                precision: int) -> Iterator[float]:
    """十进制浮点类型的 range

    表示将 range(start, end, step) 的返回值的小数点左移 precision 位

    Args:
        start (int): 表示起点
        end (int): 表示终点（但不包含）
        step (int): 表示步长
        precision (int): 表示小数点左移位数

    Yields:
        Iterator[float]: 返回一个生成若干个 float 对象的生成器
    """
    ratio = 0.1**precision
    yield from map(lambda x: x * ratio, range(start, end, step))


def get_desttop_size() -> QRect:
    """获取桌面大小

    Returns:
        QRect: 返回表示桌面大小的矩形
    """
    return QApplication.desktop().screenGeometry()


def get_function_name(func: Callable) -> str:
    """获取函数名称

    Args:
        func (Callable): 表示要查询的函数

    Returns:
        str: 表示函数名称字符串
    """
    return func.__name__


def get_function_para_names(func: Callable) -> Tuple[str, ...]:
    """查询函数的参数名称

    Args:
        func (Callable): 表示要查询的函数

    Returns:
        Tuple[str, ...]: 返回由各个参数名称组成的元组
    """
    return func.__code__.co_varnames


def get_function_para_count(func: Callable) -> int:
    """查询一个函数的参数数量

    Args:
        func (Callable): 表示要查询的函数

    Returns:
        int: 返回参数数量
    """
    return func.__code__.co_argcount


def get_pure_filename(file_path: str) -> str:
    """获取一个文件的纯名称

    Args:
        file_path (str): 表示文件路径，可以为绝对/相对路径。

    Returns:
        str: 返回文件纯名称
    """
    return os.path.basename(file_path)


def listdir(dir_path: str, split='/') -> Iterator[str]:
    """列出一个目录下的所有文件，文件夹

    Args:
        dir_path (str): 表示目录路径
        split (str, optional): 最终路径的分隔符，默认为 '/'

    Yields:
        Iterator[str]: 返回所有子文件的生成器
    """
    if split == '/':
        for f in os.listdir(dir_path):
            yield os.path.join(dir_path, f).replace('\\', '/')
    else:
        for f in os.listdir(dir_path):
            yield os.path.join(dir_path, f).replace('/', '\\')


def listdir_file(dir_path: str, split='/') -> Iterator[str]:
    """列出一个目录下的所有文件

    Args:
        dir_path (str): 表示目录路径
        split (str, optional): 最终路径的分隔符，默认为 '/'

    Yields:
        Iterator[str]: 返回所有子文件的生成器
    """
    if split == '/':
        for f in os.listdir(dir_path):
            f = os.path.join(dir_path, f).replace('\\', '/')
            if os.path.isfile(f):
                yield f
    else:
        for f in os.listdir(dir_path):
            f = os.path.join(dir_path, f).replace('/', '\\')
            if os.path.isfile(f):
                yield f


def load_dll(dll_file_path: str) -> ctypes.WinDLL:
    """从某个 dll 文件中加载 dll 资源

    Args:
        dll_file_path (str): 表示 dll 文件路径

    Returns:
        ctypes.WinDLL: 返回 ctypes.WinDLL 对象
    """
    if sys.version_info.minor < 8:
        return ctypes.WinDLL(dll_file_path)
    else:
        return ctypes.WinDLL(dll_file_path, winmode=0)


def load_dll_function(dll_file_path: str,
                      func_name: str) -> ctypes.CDLL._FuncPtr:
    """根据 dll 文件路径，加载 dll 资源，并从中找到某个函数

    如果 dll 中不存在某个名称的函数，会引发 OSError

    Args:
        dll_file_path (str): 要加载的 dll 文件的路径
        func_name (str): 要查找的函数名称

    Returns:
        ctypes.CDLL._FuncPtr: 返回函数句柄
    """
    return load_function(dll=load_dll(dll_file_path), func_name=func_name)


def load_function(dll: ctypes.WinDLL, func_name: str) -> ctypes.CDLL._FuncPtr:
    """从 dll 资源中找到某个函数

    如果 dll 中不存在某个名称的函数，会引发 OSError

    Args:
        dll (ctypes.WinDLL): 加载的 dll 资源
        func_name (str): 要查找的函数名称

    Returns:
        ctypes.CDLL._FuncPtr: 返回函数句柄
    """
    return getattr(dll, func_name)


def numpy_array_shift(array: np.ndarray, right_shift: int) -> np.ndarray:
    """对 numpy 数组进行循环移动

    本函数不会改变原 numpy 数组的内容

    Args:
        array (np.ndarray): 表示输入的数组
        right_shift (int): 表示循环右移的量

    Returns:
        np.ndarray: 返回数组循环右移后的结果
    """
    right_shift %= len(array)
    if not right_shift:
        return array
    else:
        res = array.copy()
        res[:right_shift], res[right_shift:] = array[
            -right_shift:], array[:-right_shift]
        return res


def numpy_array_adapt_length(array: np.ndarray, length: int) -> np.ndarray:
    """通过周期复制，使 np.ndarray 达到某个长度

    Args:
        array (np.ndarray): 表示输入数组
        length (length): 表示要修改到的长度

    Returns:
        np.ndarray: 返回长度为 length 的数组
    """
    while len(array) < length:
        array = np.hstack((array, array))
    return array[:length]


def numpy_array_shift_2d(array: np.ndarray, di: int, dj: int) -> np.ndarray:
    """对二维 np.ndarray 进行滚动平移

    Args:
        array (np.ndarray): 表示输入的二维数组
        di (int): 表示按行进行的滚动平移量
        dj (int): 表示按列进行的滚动平移量

    Returns:
        np.ndarray: 返回滚动平移以后的二维数组
    """
    m, n = array.shape
    res = array.copy()
    if di > 0:
        res[di:], res[:di] = res[:m - di], res[-di:]
    elif di < 0:
        di = -di
        res[:-di], res[-di:] = res[di:], res[:di]
    if dj > 0:
        res[:, dj:], res[:, :dj] = res[:, :n - dj], res[:, -dj:]
    elif dj < 0:
        dj = -dj
        res[:, :-dj], res[:, -dj:] = res[:, dj:], res[:, :dj]
    return res


def os_path_append(path: str):
    """在执行路径上添加路径

    添加有效期为程序运行期间，不会修改系统路径。

    Args:
        path (str): 表示要添加的路径
    """
    os.environ["PATH"] = "{0};{1}".format(os.path.abspath(path),
                                          os.environ["PATH"])


def os_path_list() -> List[str]:
    """将所有执行路径以字符串列表形式返回

    Returns:
        List[str]: 返回所有的路径字符串组成的列表
    """
    return os.environ["PATH"].split(';')


def os_path_str() -> str:
    """将所有执行路径以字符串形式返回

    Returns:
        str: 返回所有的路径
    """
    return os.environ["PATH"]


def remove_to_trash(path: str) -> bool:
    """删除文件

    本操作只会把文件/文件夹送到回收站

    Args:
        path (str): 要删除的文件/文件夹路径

    Returns:
        int: 返回错误码，若为零表示删除成功
    """
    path = path.replace('/', '\\')
    res = win32comext.shell.shell.SHFileOperation(
        (0, win32comext.shell.shellcon.FO_DELETE, path, None,
         win32comext.shell.shellcon.FOF_SILENT
         | win32comext.shell.shellcon.FOF_ALLOWUNDO, None, None))
    return res[0]


def simple_str(obj: Any) -> str:
    """为了精简表示对象，所以用本函数提供一些对象的精简字符化

    Args:
        obj (Any): 表示对象

    Returns:
        str: 返回其精简表示
    """
    t = type(obj)
    if issubclass(t, np.ndarray):
        return "{0}(dtype={1}, shape={2})".format(
            str(t).split('\'')[1], obj.dtype, obj.shape)
    elif issubclass(t, str):
        if len(obj) > 10:
            return "\"{0}\"...".format(obj[:10])
        else:
            return "\"{0}\"".format(obj)
    elif issubclass(t, list):
        if len(obj) > 2:
            return "{0}(len={1}, items={{{2}, {3}, ...}})".format(
                str(t).split('\'')[1], len(obj), simple_str(obj[0]),
                simple_str(obj[1]))
        else:
            return "{0}(items={{{1}}})".format(
                str(t).split('\'')[1], ', '.join(map(simple_str, obj)))
    elif issubclass(t, dict):
        if len(obj) > 2:
            it = iter(obj.items())
            firstk, firstv = next(it)
            secondk, secondv = next(it)
            return "{0}(len={1}, items={{{2}:{3}, {4}:{5}, ...}})".format(
                str(t).split('\'')[1], len(obj), simple_str(firstk),
                simple_str(firstv), simple_str(secondk), simple_str(secondv))
        else:
            return "{0}(items={{{1}}})".format(
                str(t).split('\'')[1], ', '.join(
                    map(lambda s: simple_str(s[0]) + ':' + simple_str(s[1]),
                        obj.items())))
    elif issubclass(t, set):
        if len(obj) > 2:
            it = iter(obj)
            first = next(it)
            second = next(it)
            return "{0}(len={1}, items={{{2}, {3}, ...}})".format(
                str(t).split('\'')[1], len(obj), simple_str(first),
                simple_str(second))
        else:
            return "{0}(items={{{1}}})".format(
                str(t).split('\'')[1], ', '.join(map(simple_str, obj)))
    elif issubclass(t, SharedStateController):
        return "SharedStateController(m_value=%s)" % obj.get_value()
    elif issubclass(t, QEvent):
        return "QEvent-obj(type={0},id={1:X})".format(
            get_event_type(obj.type()), id(obj))
    else:
        return str(obj)


def sleep_for(msec: int):
    """睡眠一定毫秒数

    本函数比起 time.sleep 更为精准，误差在 1 毫秒以下。

    本函数并不等价于 time.sleep,因为在执行到 eventloop.exec 的时候，本函数会放弃线程的所有权，所以本线程会趁这个时机去处理别的事件。

    Args:
        msec (int): 表示要睡眠的毫秒数
    """
    eventloop = QEventLoop()
    QTimer.singleShot(msec, eventloop.quit)
    eventloop.exec()


def str_to_float_tuple(s: Optional[str], split: str = "; "):
    """将字符串转为浮点数元组

    Args:
        s (str): 表示要转化的字符串
        split (str): 表示分割字符，默认为 "; "
    """
    if s is None:
        return None
    return tuple(map(float, s.split(split)))


def str_to_int_tuple(s: Optional[str], split: str = "; "):
    """将字符串转为整数元组

    Args:
        s (str): 表示要转化的字符串
        split (str): 表示分割字符，默认为 "; "
    """
    if s is None:
        return None
    return tuple(map(int, s.split(split)))


def tuple_to_str(tp: Tuple, split: str = "; "):
    """将元组转为字符串

    Args:
        tp (Tuple): 表示要转化的元组
        split (str): 表示分割字符，默认为 "; "
    """
    return split.join(map(str, tp))


def weakref_local_function(*objects) -> Callable:
    """为局部函数提供对象弱引用的装饰器。

    必要性存疑。

    Returns:
        Callable: 返回闭包函数
    """
    objects = tuple(map(weakref.proxy, objects))

    def inner(func):

        def callback(*args, **kwargs):
            return func(*objects, *args, **kwargs)

        return callback

    return inner


def weakref_member_function(obj: Any, func: Callable) -> Callable:
    """为成员函数提供对象弱引用的装饰器

    必要性存疑。

    Args:
        obj (Any): _description_
        func (Callable): _description_

    Returns:
        Callable: 返回闭包函数
    """
    obj = weakref.proxy(obj)

    def callback(*args, **kwargs):
        return func(obj, *args, **kwargs)

    return callback

def wait_for_ready():
    pass

