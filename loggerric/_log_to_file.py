from enum import Enum, auto
from colorama import Fore
import os, re
import io
import threading
import queue
import atexit
import time

def escape_ansi(text:str) -> str:
    """
    **Used to escape ansi (terminal color).**

    *Parameters*:
    - `text` (str): The text including the ansi.

    *Example*:
    ```python
    no_ansi = escape_ansi(text='myTextThatIncludesAnsi')
    ```
    """
    regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return regex.sub('', text)

class LogToFileLevel(Enum):
    """
    **Enums used for file logging.**
    """
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    DEBUG = auto()
    PRETTY_PRINT = auto()
    TABLE = auto()
    PROGRESS_BAR = auto()
    TIMER = auto()
    PROMPT = auto()

class LogToFile:
    """
    **Contains methods for the automatic file logging.**
    """
    _active_levels = {
        LogToFileLevel.INFO, LogToFileLevel.WARN, LogToFileLevel.ERROR,
        LogToFileLevel.DEBUG, LogToFileLevel.PROMPT,
        LogToFileLevel.PRETTY_PRINT, LogToFileLevel.TABLE,
        LogToFileLevel.PROGRESS_BAR, LogToFileLevel.TIMER,
    }

    _should_dump = False
    _dump_path = os.path.join(os.getenv('HOMEDRIVE'), os.getenv('HOMEPATH'),
                              'loggerric_log_dump.log')

    # Internal queue/writer for thread-safe writes
    __writer_queue: "queue.Queue[str]" = queue.Queue()
    _writer_thread: threading.Thread | None = None
    _writer_running: bool = False
    _writer_file: io.TextIOBase | None = None
    _writer_lock = threading.Lock()

    @classmethod
    def set_dump_location(cls, full_directory:str, file_name:str) -> None:
        """
        **Set a location for the log file.**

        *Parameters*:
        - `full_directory` (str): Full path to the parent directory
        of the log file.
        - `file_name` (str): File name for the log, without extension.

        *Example*:
        ```python
        LogToFile.set_dump_location(full_directory='C:/Users',
                                    file_name='important_file')
        ```
        """
        path_exists = os.path.exists(full_directory)
        assert path_exists, f'Directory "{full_directory}" does not exist!'
        
        cls._dump_path = os.path.join(full_directory, file_name + '.log')

    @classmethod
    def start_logging(cls) -> None:
        """
        **Start logging to file.**
        """
        cls._should_dump = True
        # Start background writer thread if not already running
        if not cls._writer_running:
            cls._start_writer()

        print(f'{Fore.BLUE}Logging To File: {Fore.GREEN}Started{Fore.RESET}')

    @classmethod
    def stop_logging(cls) -> None:
        """
        **Stop logging to file.**
        """
        cls._should_dump = False
        # Signal writer to stop and flush
        cls._stop_writer()

        print(f'{Fore.BLUE}Logging To File: {Fore.RED}Stopped{Fore.RESET}')

    @classmethod
    def enable(cls, levels:LogToFileLevel) -> None:
        """
        **Enable levels to log.**

        *Parameters*:
        - `levels` (LogToFileLevel): The levels to enable.

        *Example*:
        ```python
        LogToFile.enable(LogToFileLevel.WARN, ...)
        ```
        """
        cls._active_levels.update(levels)

    @classmethod
    def disable(cls, levels:LogToFileLevel) -> None:
        """
        **Disable levels to log.**

        *Parameters*:
        - `levels` (LogToFileLevel): The levels to disable.

        *Example*:
        ```python
        LogToFile.disable(LogToFileLevel.TIMER, ...)
        ```
        """
        cls._active_levels.difference_update(levels)

    @classmethod
    def _log(cls, data:str) -> None:
        """
        Enqueue data to background writer. If background writer is not
        available, fall back to direct append with a lock.
        """
        if not data:
            return

        line = str(data) + '\n'

        # If writer running, enqueue
        if cls._writer_running:
            try:
                cls._writer_queue.put_nowait(line)
                return
            except queue.Full:
                # Fall through to synchronous write if queue is full
                pass

        # Fallback synchronous write protected by lock
        with cls._writer_lock:
            with open(cls._dump_path, 'a+t', encoding='utf-8') as file:
                file.write(line)

    @classmethod
    def _start_writer(cls) -> None:
        """Start the background writer thread. Safe to call multiple times."""
        if cls._writer_running:
            return

        # Ensure directory exists for path
        parent = os.path.dirname(cls._dump_path)
        if parent and not os.path.exists(parent):
            try:
                os.makedirs(parent, exist_ok=True)
            except Exception:
                pass

        # Open file handle once for append
        try:
            cls._writer_file = open(cls._dump_path, 'a+t', encoding='utf-8')
        except Exception:
            cls._writer_file = None

        cls._writer_running = True

        def _writer_loop():
            while cls._writer_running or not cls._writer_queue.empty():
                try:
                    try:
                        item = cls._writer_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue

                    if item is None:
                        # Sentinel for immediate shutdown
                        break

                    if cls._writer_file is not None:
                        try:
                            cls._writer_file.write(item)
                            cls._writer_file.flush()
                        except Exception:
                            # On write error, ignore to avoid crashing the thread
                            pass
                    else:
                        # If file handle could not be opened, try direct append
                        with cls._writer_lock:
                            with open(cls._dump_path, 'a+t', encoding='utf-8') as f:
                                f.write(item)

                    cls._writer_queue.task_done()
                except Exception:
                    # Catch-all to keep the loop alive
                    time.sleep(0.1)

            # Close file handle
            if cls._writer_file is not None:
                try:
                    cls._writer_file.close()
                except Exception:
                    pass
                cls._writer_file = None

        cls._writer_thread = threading.Thread(target=_writer_loop, daemon=True, name='loggerric-file-writer')
        cls._writer_thread.start()

        # Ensure clean shutdown
        atexit.register(cls._stop_writer)

    @classmethod
    def _stop_writer(cls, timeout:float=2.0) -> None:
        """Stop the writer thread and flush pending items."""
        if not cls._writer_running:
            return

        cls._writer_running = False

        # Put sentinel to unblock queue.get if needed
        try:
            cls._writer_queue.put_nowait(None)
        except Exception:
            pass

        # Wait for thread to finish
        t = cls._writer_thread
        if t is not None and t.is_alive():
            t.join(timeout)

        # If still alive, we leave it (daemon thread)
        cls._writer_thread = None