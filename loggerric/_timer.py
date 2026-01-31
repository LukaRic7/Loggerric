from time import perf_counter
from colorama import Fore
from loggerric._timestamp import *
from loggerric._log_to_file import *

class Timer:
    """
    **Time how long a code snippet takes to execute.**

    *Arguments*:
    - `name` (str): Name of the timer.

    *Example*:
    ```python
    with Timer(name='Timer Name'):
        ...
    ```
    """
    # Initialization
    def __init__(self, name:str='Timer'):        
        # Define class scoped variables
        self.name = name
        self.end_time = 0
        self.elapsed = 0

    # Entering 'with' operator
    def __enter__(self):
        # Log the start time in variable, and log to STDIO
        self.start_time = perf_counter()
        ts = Timestamp.get(return_with_ansi=True)
        message = f'{ts}{Fore.BLUE}{self.name}: {Fore.CYAN}Started...{Fore.RESET}'
        print(message)

        # Log to file
        if LogToFileLevel.TIMER in LogToFile._active_levels and LogToFile._should_dump:
            LogToFile._log(escape_ansi(message))
        
    # Exiting 'with' operator
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log the end time, and calculate the time elapsed
        self.end_time = perf_counter()
        self.elapsed = self.end_time - self.start_time

        # Check if duration should be converted to milliseconds
        is_ms = False
        if self.elapsed < 1:
            is_ms = True
            self.elapsed *= 1_000
        
        # Log the duration
        ts = Timestamp.get(return_with_ansi=True)
        message = f'{ts}{Fore.BLUE}{self.name}: {Fore.CYAN}Finished... {Fore.YELLOW}{self.elapsed:,.5f} {"ms" if is_ms else "s"}{Fore.CYAN} Elapsed.{Fore.RESET}'
        print(message)

        # Log to file
        if LogToFileLevel.TIMER in LogToFile._active_levels and LogToFile._should_dump:
            LogToFile._log(escape_ansi(message))