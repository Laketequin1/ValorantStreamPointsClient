import keyboard

# Block the keys
keyboard.block_key('w')
keyboard.block_key('a')
keyboard.block_key('s')
keyboard.block_key('d')

print("W, A, S, and D keys are blocked. Press ESC to exit.")

# Keep the script running until ESC is pressed
keyboard.wait('esc')

# Unblock the keys
keyboard.unblock_key('w')
keyboard.unblock_key('a')
keyboard.unblock_key('s')
keyboard.unblock_key('d')

print("W, A, S, and D keys are unblocked.")