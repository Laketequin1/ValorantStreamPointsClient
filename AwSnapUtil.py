import ast
import ctypes

show_warnings = True
show_verbose = False

COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"

# WinAPI functions and structures for get_pixel_colour()
user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

def verbose(message):
    if show_verbose:
        print(f"[INFO] {message}")

def warn(message):
    if show_warnings:
        print(f"{COLOR_RED}[WARNING] {message}{COLOR_RED}")

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

def get_pixel_colour(x, y):
    # Create a device context (DC) for the entire screen
    hdc_screen = user32.GetDC(None)

    pixel = gdi32.GetPixel(hdc_screen, x, y)
    r = pixel & 0x0000ff
    g = (pixel & 0x00ff00) >> 8
    b = (pixel & 0xff0000) >> 16
    color = (r, g, b)

    user32.ReleaseDC(None, hdc_screen)

    return color

def log_function(func): # TODO add indents
    def wrapper(*args, **kwargs):
        if kwargs:
            verbose(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}, {kwargs}\n")
        else:
            verbose(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}\n")
        result = func(*args, **kwargs)
        verbose(f"{COLOR_GREEN}Result{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {result}\n")
        return result
    return wrapper