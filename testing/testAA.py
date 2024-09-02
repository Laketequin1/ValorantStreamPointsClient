import win32gui

def enum_window_titles():
    """Enumerate all window titles."""
    # Define a callback function to be called for each window
    def callback(hwnd, window_titles):
        # Get the window's title
        title = win32gui.GetWindowText(hwnd)
        # Get the window's class name
        class_name = win32gui.GetClassName(hwnd)
        # If the window has a title, add it to the list
        if title:
            window_titles.append((hwnd, title, class_name))
        return True  # Continue enumeration

    # List to store window titles
    window_titles = []
    
    # Enumerate all top-level windows
    win32gui.EnumWindows(callback, window_titles)

    # Print all window titles
    for hwnd, title, class_name in window_titles:
        print(f"HWND: {hwnd}, Title: '{title}', Class: '{class_name}'")

# Example usage
enum_window_titles()
