import pygame
import win32api
import win32gui
import win32con
import ctypes

# Initialize the pygame library
pygame.init()

# Set the dimensions of the window
window_width = 800
window_height = 600

# Create the window with no frame
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)

# Get the window handle (HWND)
hwnd = pygame.display.get_wm_info()['window']

# Set the title of the window
pygame.display.set_caption("Pygame Window")

# Make the window always on top
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# Make the window transparent
# Get the current window style
extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
# Add layered and transparent extended styles
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
# Set the transparency color key to black (0, 0, 0)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# Main loop flag
running = True

# Main loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill the screen with a color (RGB)
    screen.fill((0, 0, 0))  # Black

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
