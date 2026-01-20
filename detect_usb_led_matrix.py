"""
USB LED MATRIX DETECTION
Specs: 16x32 pixels, 173x70mm, 5V @ 2A, USB connection
"""
import usb.core
import usb.util

def find_led_matrix():
    """Find USB LED matrix panel"""
    print("🔍 Scanning USB devices for LED matrix panel...")
    print("   Specs: 16x32 pixels, 173x70mm, 5V @ 2A\n")

    # Get all USB devices
    devices = usb.core.find(find_all=True)

    found_devices = []
    for device in devices:
        try:
            # Get device info
            vendor_id = device.idVendor
            product_id = device.idProduct

            # Try to get manufacturer and product strings
            try:
                manufacturer = usb.util.get_string(device, device.iManufacturer)
            except:
                manufacturer = "Unknown"

            try:
                product = usb.util.get_string(device, device.iProduct)
            except:
                product = "Unknown"

            # Look for LED matrix keywords
            keywords = ['led', 'matrix', 'panel', 'display', 'rgb', 'light']
            if any(kw in str(manufacturer).lower() for kw in keywords) or \
               any(kw in str(product).lower() for kw in keywords):
                found_devices.append({
                    'vendor_id': f"0x{vendor_id:04x}",
                    'product_id': f"0x{product_id:04x}",
                    'manufacturer': manufacturer,
                    'product': product,
                    'device': device
                })
                print(f"✅ Found potential LED device:")
                print(f"   Vendor ID:  {vendor_id:04x}")
                print(f"   Product ID: {product_id:04x}")
                print(f"   Manufacturer: {manufacturer}")
                print(f"   Product: {product}\n")
        except Exception as e:
            pass

    if not found_devices:
        print("❌ No LED matrix found in USB devices")
        print("\n📋 All USB devices:")
        devices = usb.core.find(find_all=True)
        for i, dev in enumerate(devices):
            print(f"   Device {i}: VID={dev.idVendor:04x} PID={dev.idProduct:04x}")

    return found_devices

if __name__ == "__main__":
    find_led_matrix()
