# -*- coding:utf-8 -*-
import logging
import os.path
import shutil
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

initialized = False


def init_logger(log_level="DEBUG", log_path=None, logfile_name=None, clear=False, backup_count=0):
    global initialized
    if initialized:
        return
    logger = logging.getLogger()
    logger.setLevel(log_level)
    if logfile_name:
        if clear and os.path.isdir(log_path):
            shutil.rmtree(log_path)
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        logfile = os.path.join(log_path, logfile_name)
        handler = TimedRotatingFileHandler(logfile, "midnight", backupCount=backup_count)
        print("init logger ...", logfile)
    else:
        print("init logger ...")
        handler = logging.StreamHandler()
    fmt_str = "%(levelname)1.1s [%(asctime)s] %(message)s"
    fmt = logging.Formatter(fmt=fmt_str, datefmt=None)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    initialized = True


def _log_msg_header(*args, **kwargs):
    """ message header of log
    @param kwargs["caller"]  called object
    * NOTE: logger.xxx(... caller=self) for instance method
            logger.xxx(... caller=cls) for @classmethod
    """
    cls_name = ""
    func_name = sys._getframe().f_back.f_code.co_name
    session_id = "-"
    try:
        _caller = kwargs.get("caller", None)
        if _caller:
            if not hasattr(_caller, "__name__"):
                _caller = _caller.__class__
            cls_name = _caller.__name__
            del kwargs["caller"]
    except:
        pass
    finally:
        msg_header = f"[{session_id}] [{cls_name}].[{func_name}]".format(session_id, cls_name, func_name)
    return msg_header, kwargs


def _log(msg_header, *args, **kwargs):
    _log_msg = msg_header
    for l in args:
        if type(l) == tuple:
            ps = str(l)
        else:
            try:
                ps = "%r" % l
            except:
                ps = str(l)
        if type(l) == str:
            _log_msg += ps[1:-1] + " "
        else:
            _log_msg += ps + " "
    if len(kwargs) > 0:
        _log_msg += str(kwargs)
    return _log_msg


def info(*args, **kwargs):
    func_name, kwargs = _log_msg_header(*args, **kwargs)
    logging.info(_log(func_name, *args, **kwargs))


def warn(*args, **kwargs):
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.warning(_log(msg_header, *args, **kwargs))


def debug(*args, **kwargs):
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.debug(_log(msg_header, *args, **kwargs))


def error(*args, **kwargs):
    logging.error("*" * 60)
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.error(_log(msg_header, *args, **kwargs))
    logging.error("*" * 60)


def exception(*args, **kwargs):
    logging.error("*" * 60)
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.error(_log(msg_header, *args, **kwargs))
    traceback.print_stack()
    logging.error("*" * 60)