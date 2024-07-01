import pygame
import win32api
import win32gui
import win32con
import random
import time

class ActionOverlay:
    """
    ActionOverlay is a class to manage and display a transparent overlay window with text that slides out after a set duration.

    Attributes:
    -----------
    lines_of_text : list
        A list to store tuples of text and the time they were added.

    Methods:
    --------
    __init__():
        Initializes the overlay window and sets its properties.

    add_text(text: str) -> None:
        Adds a line of text with a timestamp to the overlay.

    handle_events() -> bool:
        Handles pygame events and returns whether the main loop should continue.

    render() -> None:
        Renders the text onto the overlay window and handles the sliding animation.
    """

    # Window size
    WINDOW_PERCENT_WIDTH = 0.3
    WINDOW_PERCENT_HEIGHT = 0.4

    # Colours
    WINDOW_BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    TEXT_BG_COLOR = (0, 0, 20)

    # Text padding
    TEXT_PADDING_X = 10
    TEXT_PADDING_Y = 5
    TEXT_LINE_HEIGHT = 46
    FONT_SIZE = 48

    # Text settings
    MAX_LINES = 8
    TEXT_LIFETIME_SECONDS = 5
    ANIMATION_DURATION = 0.4

    # Render settings
    FRAME_RATE = 30

    def __init__(self):
        """Initializes the overlay window and sets its properties."""
        pygame.init()

        # Get the dimensions of the screen
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # Calculate the window dimensions based on percentages
        self.window_width = round(self.screen_width * self.WINDOW_PERCENT_WIDTH)
        self.window_height = round(self.screen_height * self.WINDOW_PERCENT_HEIGHT)

        # Calculate the window position (bottom left)
        self.window_x = 0
        self.window_y = self.screen_height - self.window_height

        # Create the window with no frame
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.NOFRAME)

        # Get the window handle (HWND)
        hwnd = pygame.display.get_wm_info()['window']

        # Set the title of the window
        pygame.display.set_caption("VSP Action Overlay")

        # Make the window always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.window_x, self.window_y, self.window_width, self.window_height, win32con.SWP_SHOWWINDOW)

        # Make the window transparent
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

        # Variables for managing text
        self.lines_of_text = []

    def add_text(self, text: str) -> None:
        """
        Adds a line of text with a timestamp to the overlay.

        Parameters:
        -----------
        text : str
            The text to be added to the overlay.

        Example:
        --------
        >>> overlay.add_text("Hello, World!")
        """
        current_time = time.time()
        self.lines_of_text.append((text, current_time))
        if len(self.lines_of_text) > self.MAX_LINES:
            self.lines_of_text = self.lines_of_text[-self.MAX_LINES:]

    def handle_events(self) -> bool:
        """
        Handles pygame events and returns whether the main loop should continue.

        Returns:
        --------
        bool
            False if the quit event is detected, True otherwise.

        Example:
        --------
        >>> running = overlay.handle_events()
        >>> running
        True
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def render(self) -> None:
        """
        Renders the text onto the overlay window and handles the sliding animation.

        Example:
        --------
        >>> overlay.render()
        """
        current_time = time.time()
        self.lines_of_text = [(text, t) for text, t in self.lines_of_text if current_time - t < (self.TEXT_LIFETIME_SECONDS + self.ANIMATION_DURATION)]

        # Fill the screen with a color (RGB)
        self.screen.fill(self.WINDOW_BG_COLOR)  # Must be black background

        # Render text on the screen with rounded border
        font = pygame.font.Font(None, self.FONT_SIZE)
        text_y = self.window_height - self.TEXT_LINE_HEIGHT
        for line, t in reversed(self.lines_of_text):
            elapsed_time = current_time - t

            # Calculate the text x position based on elapsed time
            if elapsed_time > self.TEXT_LIFETIME_SECONDS:
                animation_progress = (elapsed_time - self.TEXT_LIFETIME_SECONDS) / self.ANIMATION_DURATION
                text_x = int(self.TEXT_PADDING_X - self.window_width * animation_progress)
            else:
                text_x = self.TEXT_PADDING_X

            # Render text surface
            text_surface = font.render(line, True, self.TEXT_COLOR)  # White text

            # Create rounded rectangle surface for text background
            text_rect = text_surface.get_rect()
            text_rect.left = text_x
            text_rect.top = text_y
            text_rect.width += self.TEXT_PADDING_X * 2  # Add padding
            text_rect.height += self.TEXT_PADDING_Y * 2  # Add padding
            pygame.draw.rect(self.screen, self.TEXT_BG_COLOR, text_rect, border_radius=10)  # Dark blue rounded rectangle

            # Blit text onto screen
            self.screen.blit(text_surface, (text_rect.left + self.TEXT_PADDING_X, text_rect.top + self.TEXT_PADDING_Y))  # Offset text slightly for padding

            # Adjust y position for next line
            text_y -= self.TEXT_LINE_HEIGHT  # Increase the spacing between lines

        # Update the display
        pygame.display.flip()


if __name__ == "__main__":
    overlay = ActionOverlay()

    # Main loop flag
    running = True

    # Clock for controlling frame rate
    clock = pygame.time.Clock()

    # Main loop
    while running:
        # Handle events
        running = overlay.handle_events()

        # Render the overlay
        overlay.render()

        # Add a random text line
        if random.randint(1, 50) == 1:
            msg = "HEY: " + str(random.randint(0, 10))
            overlay.add_text(msg)
            print(msg)

        # Cap the frame rate to 30 FPS (optional, adjust as needed)
        clock.tick(ActionOverlay.FRAME_RATE)

    # Quit pygame
    pygame.quit()
