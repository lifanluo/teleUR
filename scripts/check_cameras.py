#!/usr/bin/env python3
"""
Scans for available camera devices and prints a list of their indices.

This script iterates through potential camera indices (0-9) and checks if a
camera can be opened with OpenCV. It's a useful utility to quickly find out
which camera indices to use with other scripts.
"""
import cv2

def find_available_cameras(limit=10):
    """
    Iterates through camera indices and checks for their availability.
    """
    available_cameras = []
    print(f"Searching for cameras up to index {limit-1}...")
    for i in range(limit):
        cap = cv2.VideoCapture(i)
        if cap is not None and cap.isOpened():
            print(f"  - Camera index {i}: Found")
            available_cameras.append(i)
            cap.release()
        else:
            print(f"  - Camera index {i}: Not available")

    if not available_cameras:
        print("\nNo cameras found.")
    else:
        print(f"\nAvailable camera indices: {available_cameras}")

    return available_cameras

if __name__ == "__main__":
    find_available_cameras()
