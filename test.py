import pygame
import win32api
import win32gui
import win32con
import random
import time

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
    current_time = time.time()
    lines_of_text.append((text, current_time))
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

    # Check for expired text
    current_time = time.time()
    lines_of_text = [(text, t) for text, t in lines_of_text if current_time - t < 5]

    # Fill the screen with a color (RGB)
    screen.fill((0, 0, 0))  # Must be black background

    # Render text on the screen with rounded border
    font = pygame.font.Font(None, 48)
    text_y = window_height - 46
    for line, _ in reversed(lines_of_text):
        # Render text surface
        text_surface = font.render(line, True, (255, 255, 255))  # White text

        # Create rounded rectangle surface for text background
        text_rect = text_surface.get_rect()
        text_rect.left = 10
        text_rect.top = text_y
        text_rect.width += 20  # Add padding
        text_rect.height += 10  # Add padding
        pygame.draw.rect(screen, (0, 0, 20), text_rect, border_radius=10)  # Dark blue rounded rectangle

        # Blit text onto screen
        screen.blit(text_surface, (20, text_rect.top + 5))  # Offset text slightly for padding

        # Adjust y position for next line
        text_y -= 46  # Increase the spacing between lines

    # Update the display
    pygame.display.flip()

    # Add a random text line
    if random.randint(1, 50) == 1:
        msg = "HEY: " + str(random.randint(0, 10))
        add_text(msg)
        print(msg)

    # Cap the frame rate to 30 FPS (optional, adjust as needed)
    clock.tick(30)

# Quit pygame
pygame.quit()
