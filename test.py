import win32gui
import win32ui
import win32con
import time

def get_pixel_colour(pixel_pos):
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

# Timing the function execution
start_time = time.time()

for _ in range(100):
    get_pixel_colour((27, 436))

end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Time taken to run the function 100 times: {elapsed_time} seconds")