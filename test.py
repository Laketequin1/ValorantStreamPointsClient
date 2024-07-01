import pygame
import win32api
import win32gui
import win32con
import ctypes
import random

# Initialize the pygame library
pygame.init()

# Get the dimensions of the screen
screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

# Calculate the window dimensions based on percentages
window_width = round(screen_width * 0.3)
window_height = round(screen_height * 0.4)

# Calculate the window position (bottom left)
window_x = 0
window_y = screen_height - window_height

# Create the window with no frame
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)

# Get the window handle (HWND)
hwnd = pygame.display.get_wm_info()['window']

# Set the title of the window
pygame.display.set_caption("Pygame Window")

# Make the window always on top
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, window_x, window_y, window_width, window_height, win32con.SWP_SHOWWINDOW)

# Make the window transparent
extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# Function to add text to the window
def add_text(text):
    global lines_of_text
    lines_of_text.append(text)
    if len(lines_of_text) > max_lines:
        lines_of_text = lines_of_text[-max_lines:]

# Variables for managing text
lines_of_text = []
max_lines = 10  # Maximum number of lines to display

# Main loop flag
running = True

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Main loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill the screen with a color (RGB)
    screen.fill((0, 0, 0))  # Black
    
    size = 48

    # Render text on the screen
    font = pygame.font.Font(None, size)
    text_y = window_height
    for line in reversed(lines_of_text):
        text_surface = font.render(line, True, (255, 255, 255))  # White text
        screen.blit(text_surface, (10, text_y))
        text_y -= size * 0.8
    
    # Update the display
    pygame.display.flip()

    # Add a random text line
    add_text("HEY: " + str(random.randint(0, 10)))

    # Cap the frame rate to 30 FPS (optional, adjust as needed)
    clock.tick(30)

# Quit pygame
pygame.quit()
