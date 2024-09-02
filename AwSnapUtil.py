import ast
import win32gui
import win32ui
import win32con
import time
import ctypes

verbose_level = 1

COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"

def verbose(message, level):
    if verbose_level >= level:
        print(f"[INFO] {message}")

def warn(message):
    if verbose_level >= 1:
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

def get_pixel_colour(pixel_pos, hwnd=None):
    if hwnd is None:
        hwnd = win32gui.GetDesktopWindow()
    
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, 1, 1)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (1, 1), dcObj, pixel_pos, win32con.SRCCOPY)
    b, g, r = dataBitMap.GetBitmapBits(True)[:3]
    win32gui.DeleteObject(dataBitMap.GetHandle())
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    return (r, g, b)

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_state():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))  # Get the cursor position
    left_button_down = ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000  # 0x01 is the virtual key code for the left mouse button
    return bool(left_button_down), (pt.x, pt.y)  # Returns the mouse position and state of the left button

# TODO add indents
def log_function(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            #if kwargs:
            #    verbose(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}, {kwargs}\n", level)
            #else:
            #    verbose(f"{COLOR_CYAN}Called{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {args}\n", level)

            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000

            verbose(f"{COLOR_GREEN}{round(execution_time_ms, 5)}ms{COLOR_RESET} {COLOR_YELLOW}{func.__name__}{COLOR_RESET}: {result}\n", level)
            return result
        return wrapper
    return decorator

def main():
    print(get_mouse_state())

if __name__ == "__main__":
    main()