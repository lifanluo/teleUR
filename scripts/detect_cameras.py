#!/usr/bin/env python3
"""Find available USB cameras and RealSense devices."""
import cv2
import os

try:
    import pyrealsense2 as rs
    has_rs = True
except ImportError:
    has_rs = False

print("=" * 60)
print("CAMERA DETECTION TOOL")
print("=" * 60)

# Check RealSense
if has_rs:
    print("\n📷 RealSense Cameras:")
    ctx = rs.context()
    devices = ctx.query_devices()
    if len(devices) == 0:
        print("  ❌ No RealSense devices found")
    else:
        for i, dev in enumerate(devices):
            name = dev.get_info(rs.camera_info.name)
            serial = dev.get_info(rs.camera_info.serial_number)
            print(f"  ✓ Device {i}: {name} (Serial: {serial})")
else:
    print("\n⚠️  pyrealsense2 not installed (run: pip install pyrealsense2)")

# Check USB cameras (OpenCV)
print("\n🎥 USB Cameras (OpenCV):")
found_any = False
for i in range(20):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"  ✓ Camera {i}: {w}x{h}")
            found_any = True
        cap.release()

if not found_any:
    print("  ❌ No USB cameras found")

# Check /dev/video* devices
print("\n📝 Video Devices (/dev/video*):")
for i in range(30):
    dev = f"/dev/video{i}"
    if os.path.exists(dev):
        print(f"  /dev/video{i}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("  - Use camera indices from '✓' lines above")
print("  - Avoid indices of /dev/video that are metadata streams")
print("  - Example: python run_env.py --tactile-left-camera-id 1 --tactile-right-camera-id 2")
print("=" * 60)
