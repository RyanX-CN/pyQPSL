import logging
import os
from datetime import datetime
from enum import Enum
from typing import Optional
from .InitConfig import QPSL_Log_Directory, init_config_set, init_config_getset, SingleChoiceBox


class QPSL_LOG_LEVEL(Enum):
    '''
    由于第三方库也有很多的输出，所以我们采用自定义等级
    姑且认为第三方库的日志，同等级下不如我们程序内部的日志重要。所以在同样的名字下，我们的等级值下比别人高 9
    type: ALL 可有可无的话
    QPSL_LOG_LEVEL.ALL = 9
    type: DBG 调试程序时需要看到的信息
    QPSL_LOG_LEVEL.DBG = 19
    type: INF 即使不调试程序也需要看到的信息
    QPSL_LOG_LEVEL.INF = 29
    type: WARN 做实验需要看到的关键提示，获取实验数据需要看到的信息
    QPSL_LOG_LEVEL.WARN = 39
    type: ERR 运行出错，需要注意查看
    QPSL_LOG_LEVEL.ERR = 49
    type: CRT 出现不可修复的错误
    QPSL_LOG_LEVEL.CRT = 49
    '''
    ALL = 9  # 任何信息
    DBG = 19  # 为了 debug
    INF = 29  # 普通信息
    WARN = 39  # 需要注意的信息
    ERR = 49  # 错误信息
    CRT = 59  # 崩溃信息


class ColoredConsoleHandler(logging.StreamHandler):
    color_dict = {
        QPSL_LOG_LEVEL.DBG.value: "\033[37m",  #white
        QPSL_LOG_LEVEL.INF.value: "\033[32m",  #green
        QPSL_LOG_LEVEL.WARN.value: "\033[33m",  #yellow
        QPSL_LOG_LEVEL.ERR.value: "\033[31m",  #red
        QPSL_LOG_LEVEL.CRT.value: "\033[35m",  #purple
    }

    def format(self, record):
        return "{0}{1}\033[0m".format(
            ColoredConsoleHandler.color_dict.get(record.levelno, "\033[30m"),
            super().format(record))


class QPSLLogger:
    __slots__ = "m_level"

    def __init__(self,
                 level: Optional[int] = None,
                 exc_info=True,
                 stack_info=True):
        self.m_level = level

    def __call__(self,
                 msg: object,
                 level: Optional[int] = None,
                 exc_info=False,
                 stack_info=False):
        if not level:
            level = self.m_level
        logging.getLogger().log(level=level,
                                msg=msg,
                                exc_info=exc_info,
                                stack_info=stack_info)


for level in QPSL_LOG_LEVEL._member_map_.values():
    logging.addLevelName(level.value, level.name)
if not os.path.exists(QPSL_Log_Directory):
    os.mkdir(QPSL_Log_Directory)
__QPSL_file_handler = logging.FileHandler(
    filename=datetime.now().strftime(QPSL_Log_Directory + "/%Y%m%d.txt"),
    mode="at",
    encoding="utf8",
    delay=False)
__QPSL_File_Log_Level = QPSL_LOG_LEVEL._member_map_[init_config_getset(
    keys=("log", "file_log_level"), value="ALL")].value
__QPSL_file_handler.setLevel(__QPSL_File_Log_Level)
__QPSL_console_handler = ColoredConsoleHandler()
__QPSL_Console_Log_Level = QPSL_LOG_LEVEL._member_map_[init_config_getset(
    keys=("log", "console_log_level"), value="INF")].value
__QPSL_console_handler.setLevel(__QPSL_Console_Log_Level)
__candidate_formats = [
    "{levelname:<10} {asctime} {message}",
    "{levelname:<8} {asctime} {message:<50}   {pathname}, line {lineno}",
]
__QPSL_Detailed_Log = init_config_getset(keys=("log", "detailed_log"),
                                         value=False)
logging.basicConfig(format=__candidate_formats[__QPSL_Detailed_Log],
                    style='{',
                    handlers=[__QPSL_file_handler, __QPSL_console_handler])
logging.getLogger().setLevel(logging.NOTSET)


def loading_info(message: str):
    logging.getLogger()._log(level=QPSL_LOG_LEVEL.INF.value,
                             msg=message,
                             args=())


def loading_warning(message: str):
    logging.getLogger()._log(level=QPSL_LOG_LEVEL.WARN.value,
                             msg=message,
                             args=())


def loading_error(message: str):
    logging.getLogger()._log(level=QPSL_LOG_LEVEL.ERR.value,
                             msg=message,
                             args=())


# 管理 log 等级的选择盒子
QPSL_Log_Level_Choice_Box = SingleChoiceBox(name="console_log_level",
                                            config_key=None)


def __console_log_level_callback(level: str):
    __QPSL_console_handler.setLevel(
        level=QPSL_LOG_LEVEL._member_map_[level].value)
    init_config_set(keys=("log", "console_log_level"), value=level)


QPSL_Log_Level_Choice_Box.set_choice_list(
    choices=QPSL_LOG_LEVEL._member_names_,
    callback=__console_log_level_callback)
QPSL_Log_Level_Choice_Box.set_choice_as(
    choice=QPSL_LOG_LEVEL._value2member_map_[__QPSL_Console_Log_Level].name,
    with_callback=False)
