import ctypes
import keyboard

# Define constants for key codes
VK_RETURN = 0x0D  # Enter key
VK_ESCAPE = 0x1B  # Escape key

# Low-level function to check if a key is pressed
def is_key_pressed(key_code):
    return ctypes.windll.user32.GetAsyncKeyState(key_code) & 0x8000 != 0

def some_function():
    # Placeholder for the actual function implementation
    return is_key_pressed(VK_RETURN)

def main():
    chat_open = False

    while True:
        # Check the state of the 'some_function' and keys
        some_function_active = some_function()
        enter_pressed = is_key_pressed(VK_RETURN)
        esc_pressed = is_key_pressed(VK_ESCAPE)
        
        if some_function_active:
            if not chat_open and enter_pressed:
                chat_open = True
                print("Chat is now open")
            elif chat_open and (enter_pressed or esc_pressed):
                chat_open = False
                print("Chat is now closed")
        
        # Exit the loop if escape key is pressed (for demo purposes)
        if esc_pressed:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
