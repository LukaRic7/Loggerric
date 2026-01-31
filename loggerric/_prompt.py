from colorama import Fore
from loggerric._timestamp import *
from loggerric._log_to_file import *

def prompt(question:str, options:list[str]=[], default:str=None,
           loop_until_valid:bool=False, case_sensitive:bool=True) -> str | None:
    """
    **Prompts standard I/O and returns the answer.**

    If options are given but not chosen by the user during prompting,
    return value will be `None`

    *Parameters*:
    - `question` (str): The question appearing in the prompt.
    - `options` (list[str]): Options that the user can pick
    from during prompting.
    - `default` (str): If options are not `None`, optionally
    specify a default value.
    - `loop_until_valid` (bool): Loop the prompting until the users
    answer is in the options parameter.
    - `case_sensitive` (bool): Weather or not the answer (with options)
    is case sensitive.

    *Example (No Options)*:
    ```python
    answer = prompt(question='Insert your name')
    ```

    *Example (Options)*:
    ```python
    answer = prompt(question="What's the best?", options=['a', 'b', 'c'],
                    default='b', loop_until_valid=True, case_sensitive=False)
    ```
    """
    try:
        # If no options ommitted prompt immediately
        if len(options) == 0:
            q = f'{Timestamp.get(return_with_ansi=True)}{Fore.BLUE}{question}: {Fore.CYAN}'
            answer = input(q) or None

            # Log to file
            if LogToFileLevel.PROMPT in LogToFile._active_levels and LogToFile._should_dump:
                LogToFile._log(escape_ansi(q) + answer)
            
            return answer

        # Format options
        options_formatted = f'{Fore.BLUE} | '.join(Fore.YELLOW + o for o in options)
        
        # Lower case if not case sensitive
        raw_options = None
        if not case_sensitive:
            raw_options = options
            options = [o.lower() for o in options]

        # Prompt user
        answer = ''
        ts = Timestamp.get(return_with_ansi=True)
        q = f'{ts}{Fore.BLUE}{question} [ {options_formatted}{Fore.BLUE} ]{f" ({Fore.YELLOW}{default}{Fore.BLUE})" if default else ""}:{Fore.CYAN} '
        while (answer if case_sensitive else answer.lower()) not in options:
            answer = input(q)

            # Log to file
            if LogToFileLevel.PROMPT in LogToFile._active_levels and LogToFile._should_dump:
                LogToFile._log(escape_ansi(q) + answer)

            if not loop_until_valid or default:
                break

            # If the answer is invalid, tell the user
            if (answer if case_sensitive else str(answer).lower()) not in options:
                ts = Timestamp.get(return_with_ansi=True)
                message = f'{ts}{Fore.RED}Invalid Option: "{Fore.YELLOW}{answer}{Fore.RED}"{Fore.RESET}'
                print(message)
                
                if LogToFileLevel.PROMPT in LogToFile._active_levels and LogToFile._should_dump:
                    LogToFile._log(escape_ansi(message))

        # Validate answer
        if len(answer) == 0 and default != None:
            return default
        if (answer if case_sensitive else answer.lower()) in options:
            return raw_options[options.index(answer.lower())] if raw_options else answer
        
        # Implementor decides what to happen if user answers "wrong"
        return None
    except KeyboardInterrupt:
        print(f'{Timestamp.get(return_with_ansi=True)}{Fore.RED}Prompt Cancelled by User!{Fore.RESET}')