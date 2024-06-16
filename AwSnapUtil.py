import ast

show_warnings = True
show_verbose = False

COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"

def warn(message): # Displays warning/error messages
    if show_warnings == True: # If warning messages active
        print(f"{COLOR_RED}[WARNING] {message}{COLOR_RED}") # Print warning message

def eval_message(message):
    """
    Safely return the eval of a string.
    
    The function attempts to safely return the eval of a string with ast.literal_eval. If the string can not be evaled due to a ValueError then call warn and return None.
    
    This is useful for converting the string with a dictionary inside to just a dictionary, without causing any security risks.

    Parameters
    ----------
    message : string
        A evaluable string.

    Returns
    -------
    any
        The result of the evaled string.
        
    ** ValueError **
    If string cannot be evaled due to ValueError raised:
    
    NoneType
        None.
        
    Examples
    --------
    >>> message = eval_message("{'one':1, 'two':2, 'three':3}")
    >>> print(message)
    {'one':1, 'two':2, 'three':3}

    ** ValueError **
    If string cannot be evaled due to ValueError raised:
    
    >>> message = eval_message("{'one':1, 'two:2, 'three':3}")
    [WARNING] Unable to eval message recieved: "{'one':1, 'two:2, 'three':3}"
    >>> print(message)
    None
    """
    if type(message) == str and message:
        try:
            return ast.literal_eval(message)
        except (ValueError, SyntaxError) as e:
            warn(f'Unable to eval message recieved: "{message}" because of the error: {e}')
    elif type(message) != str:
        warn(f"Message type is not str: {type(message)}")
        return ""
    else:
        warn(f"Message length is 0")
        return None

def log_function(func):
    def wrapper(*args, **kwargs):
        if kwargs:
            print(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}, {kwargs}\n")
        else:
            print(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}\n")
        result = func(*args, **kwargs)
        print(f"{COLOR_GREEN}Result{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {result}\n")
        return result
    return wrapper

