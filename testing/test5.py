import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((640, 480))  # Create a window of 640x480 pixels
pygame.display.set_caption("Basic Blue Screen")

# Set the background color
blue_color = (0, 0, 255)  # RGB for blue

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check for the window close button event
            running = False

    # Fill the screen with blue
    screen.fill(blue_color)

    # Update the display
    pygame.display.flip()

# Quit Pygame and close the window
pygame.quit()