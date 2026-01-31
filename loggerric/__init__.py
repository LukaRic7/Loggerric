from loggerric._log_to_file import LogToFile, LogToFileLevel
from loggerric._progress_bar import ProgressBar
from loggerric._timestamp import Timestamp
from loggerric._log import Log, LogLevel
from loggerric._prompt import prompt
from loggerric._timer import Timer
from colorama import init
from loggerric._threadsafe_logger import ThreadSafeLogger, get_logger, ROOT_LOGGER

# Expose these functions/classes
__all__ = ['Timestamp', 'LogLevel', 'Log', 'prompt', 'ProgressBar', 'Timer',
           'LogToFile', 'LogToFileLevel', 'ThreadSafeLogger', 'get_logger', 'ROOT_LOGGER']

# Initialize Colorama
init(autoreset=True)