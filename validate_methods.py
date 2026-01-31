from loggerric import *
from time import sleep

# C/P (Code lines: 786 by v1.4.1)
# python -m build
# twine upload dist/*

TEST_PROGRESS = False
TEST_PROMPTING = False
TEST_TIMER = False
TEST_TIMESTAMP = False
TEST_LOGGING = True

LogToFile.set_dump_location('C:/Users/lukar/Desktop', 'test_log1')
#LogToFile.start_logging()

# ---------------------------- #
# <-----> PROGRESS BAR <-----> #
# ---------------------------- #

if TEST_PROGRESS:
    # Short bar
    end_val = 50
    bar = ProgressBar(end_value=end_val, name='Short', bar_length=30)
    for i in range(1, end_val + 1):
        sleep(0.05)
        bar.update(i)

    # Long bar
    end_val = 50
    bar = ProgressBar(end_value=end_val, name='Long', bar_length=60)
    for i in range(1, end_val + 1):
        sleep(0.05)
        bar.update(i)

# ---------------------------- #
# <------> PROMPTING <-------> #
# ---------------------------- #

if TEST_PROMPTING:
    # Regular
    answer = prompt('Regular prompt')
    print(f'You said: {answer}')

    # Default
    answer = prompt('Pick nothing (Default "a" Test)', ['a', 'b', 'c'], default='a')
    print(f'Should be a = {answer}')

    answer = prompt('Pick nothing (Default "None" Test)', ['a', 'b', 'c'])
    print(f'Should be None = {answer}')

    # Case
    answer = prompt('Pick capital "A" (Case "A" Test)', ['a', 'b', 'c'], case_sensitive=True)
    print(f'Should be None = {answer}')

    answer = prompt('Pick capital "A" (Case "A" Test)', ['a', 'b', 'c'], case_sensitive=False)
    print(f'Should be a = {answer.lower()}')

    # Repeat
    answer = prompt('Pick a wrong answer (1 time only, Repeat test)', ['a', 'b', 'c'], loop_until_valid=True)
    print(f'You picked: {answer}')

# ---------------------------- #
# <--------> TIMER <---------> #
# ---------------------------- #

if TEST_TIMER:
    # Regular
    with Timer(name='Calculation Timer'):
        sleep(1.5)

# ---------------------------- #
# <------> TIMESTAMP <-------> #
# ---------------------------- #

if TEST_TIMESTAMP:
    # Default
    print('{HH}:{MI}:{SS}.{MS} T+{DH}:{DM}:{DS}.{DN}' + ' = ' + Timestamp.get())

    # Everything
    Timestamp.set_format('{YY}/{MO}/{DD} {HH}:{MI}:{SS}.{MS} T+{DH}:{DM}:{DS}.{DN}')
    print('{YY}/{MO}/{DD} {HH}:{MI}:{SS}.{MS} T+{DH}:{DM}:{DS}.{DN}' + ' = ' + Timestamp.get())

    # Disabled
    Timestamp.disable()
    print(f'There should NOT be a timestamp: {Timestamp.get()}')

    # Enabled
    Timestamp.enable()
    print(f'There SHOULD be a timestamp: {Timestamp.get()}')

# ---------------------------- #
# <---------> LOG <----------> #
# ---------------------------- #

if TEST_LOGGING:
    # Basic logging
    Log.info('Info')
    Log.warn('Warn')
    Log.error('Error')
    Log.debug('Debug')

    # Multi-arg logging
    Log.info('Info1', 'Info2')
    Log.warn('Warn1', 'Warn2')
    Log.error('Error1', 'Error2')
    Log.debug('Debug1', 'Debug2')

    # Disable all logging levels
    Log.disable(LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.DEBUG)

    # Test if all logging levels are disabled
    Log.info("Info, You shouldn't see this")
    Log.warn("Warn, You shouldn't see this.")
    Log.error("Error, You shouldn't see this.")
    Log.debug("Debug, You shouldn't see this.")

    # Re-enable them again
    Log.enable(LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.DEBUG)

    # Test if they are enabled again
    Log.info('Info, Enabled')
    Log.warn('Warn, Enabled')
    Log.error('Error, Enabled')
    Log.debug('Debug, Enabled')

    # Pretty print various variable types
    Log.pretty_print({ 'name': ['John', 'Doe'] }, indent=4)
    Log.pretty_print(['One', 'Two', 'Three'], indent=3)
    Log.pretty_print([1, 2, 3], indent=2)
    Log.pretty_print({ 1, 2, 3, 'Test' }, indent=1) # Cant log sets yet, should be white and pure format

    # Test highlight
    Log.info('This 10 should be highlighted!', highlight=10)
    Log.info('This should be highlighted!', highlight=['This', 'be'])
    Log.warn('This should be highlighted!', highlight='highlighted')
    Log.warn('This should be highlighted!', highlight=['This', 'be'])
    Log.error('This should be highlighted!', highlight='highlighted')
    Log.error('This should be highlighted!', highlight=['This', 'be'])
    Log.debug('This should be highlighted!', highlight='highlighted')
    Log.debug('This should be highlighted!', highlight=['This', 'be'])

    import random
    nr = str(random.random())
    Log.info(f'Dynamic highlight: {nr} tada!', highlight=nr)

    headers = ['Item', 'Stock', 'Price']
    rows = [('Cola', '25', '$2.99'), ('GPU', '3', '$995.00'), ('Feather', '2,500', '$0.29')]
    Log.table(headers, rows, table_name='Store Items')

    headers = ['Item', 'Stock', 'Price', 'Sale']
    rows = [('Cola', '25', '$2.99', '0%'), ('GPU', '3', '$995.00', '5%'), ('Feather', '2,500', '$0.29', '30%')]
    Log.table(headers, rows, table_name='Store Items', highlight_rows=[0], grayout_rows=[2])

    @Log.debugdec()
    def my_function(a:int, b:int, *args, **kwargs):
        c = a + b
        return c
    my_function(6, 7, 'arg', key='kwarg')

    # Test quit_after_log
    Log.error("You shouldn't see the NEXT message", quit_after_log=True)
    print('This message') # Regular print, dont rely on package