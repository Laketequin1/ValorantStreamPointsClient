import usb.backend.libusb1
import usb.core

backend = usb.backend.libusb1.get_backend()
devices = usb.core.find(find_all=True, backend=backend)

for dev in devices:
    print(f"Device: {dev.idVendor:04x}:{dev.idProduct:04x}")
