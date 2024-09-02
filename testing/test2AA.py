import win32gui
import win32ui
import win32con
from PIL import Image
import os

def save_window_image(hwnd, image_path="captured_window.png"):
    try:
        # Get the dimensions of the target window
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        if width <= 0 or height <= 0:
            print(f"Window {hwnd} has invalid dimensions. Skipping...")
            return

        # Get the window's device context (DC)
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        # Create a bitmap object with the dimensions of the window and compatible with the source DC
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)  # Capture the entire window
        cDC.SelectObject(dataBitMap)
        
        # Capture the window image using BitBlt
        cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)
        
        # Save the bitmap to an image file
        save_bitmap_to_image(dataBitMap, image_path, width, height)
        
        # Cleanup: Delete GDI objects and release DC
        win32gui.DeleteObject(dataBitMap.GetHandle())
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        
        print(f"Image saved to {image_path}")
    
    except Exception as e:
        print(f"Error capturing HWND {hwnd}: {e}")

def save_bitmap_to_image(bitmap, image_path, width, height):
    """Save the given bitmap to an image file using Pillow."""
    try:
        # Get the bitmap's bits
        bmp_str = bitmap.GetBitmapBits(True)
        
        # Create an image using PIL
        img = Image.frombytes(
            'RGBA',
            (width, height),
            bmp_str,
            'raw',
            'BGRA',
            0,
            1
        )
        
        # Save the image to the specified path
        img.save(image_path)
    
    except Exception as e:
        print(f"Error saving image to {image_path}: {e}")

def enum_and_save_window_images(output_dir="window_images"):
    """Enumerate all windows and save each window's image with its title as filename."""
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def callback(hwnd, _):
        try:
            # Get the window's title
            title = win32gui.GetWindowText(hwnd)
            if not title:
                title = f"window_{hwnd}"
            title = title.replace(':', '_').replace('/', '_').replace('\\', '_')
            image_path = os.path.join(output_dir, f"{title}.png")

            # Save the window image
            save_window_image(hwnd, image_path)
        
        except Exception as e:
            print(f"Error processing HWND {win32gui.GetWindowText(hwnd)}: {e}")

    # List to store window handles
    win32gui.EnumWindows(callback, None)

# Example usage
enum_and_save_window_images()
