#!/usr/bin/env python3
"""
Open two cameras with OpenCV and display them side-by-side.

Usage:
    python scripts/open_two_cams.py --left 0 --right 1 --width 640 --height 480

Features:
 - Configurable device indices for the two cameras
 - Sets capture resolution (if supported)
 - Shows combined window with both streams side-by-side
 - Press 's' to save a snapshot of both frames, 'q' to quit
"""
import argparse
import time
import os
from datetime import datetime

import cv2
import numpy as np


def make_black_frame(width, height, text="No signal"):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, text, (10, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return frame


def open_capture(idx, width=None, height=None):
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        return None
    # try to set resolution if provided
    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
    return cap


def main():
    parser = argparse.ArgumentParser(description="Open two cameras and display them side-by-side using OpenCV")
    parser.add_argument("--left", type=int, default=1, help="Device index for left camera")
    parser.add_argument("--right", type=int, default=9, help="Device index for right camera")
    parser.add_argument("--width", type=int, default=640, help="Requested frame width")
    parser.add_argument("--height", type=int, default=480, help="Requested frame height")
    parser.add_argument("--save-dir", type=str, default="./captures", help="Directory to save snapshots")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    cap_left = open_capture(args.left, args.width, args.height)
    cap_right = open_capture(args.right, args.width, args.height)

    if cap_left is None and cap_right is None:
        print(f"Unable to open cameras {args.left} and {args.right}")
        return

    window_name = f"Cameras {args.left} | {args.right}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    prev_time = time.time()
    fps = 0.0
    frame_count = 0

    try:
        while True:
            frames = []
            for cap, idx in ((cap_left, args.left), (cap_right, args.right)):
                if cap is None:
                    frame = make_black_frame(args.width, args.height, text=f"Cam {idx} not open")
                else:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        frame = make_black_frame(args.width, args.height, text=f"Cam {idx} no frame")
                    else:
                        # resize to requested size to keep both equal
                        frame = cv2.resize(frame, (args.width, args.height))
                frames.append(frame)

            combined = np.hstack(frames)

            # update fps
            frame_count += 1
            if frame_count >= 10:
                now = time.time()
                fps = frame_count / (now - prev_time)
                prev_time = now
                frame_count = 0

            cv2.putText(combined, f"FPS: {fps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow(window_name, combined)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                left_path = os.path.join(args.save_dir, f"cam{args.left}_{ts}.png")
                right_path = os.path.join(args.save_dir, f"cam{args.right}_{ts}.png")
                cv2.imwrite(left_path, frames[0])
                cv2.imwrite(right_path, frames[1])
                print(f"Saved {left_path} and {right_path}")

    finally:
        for cap in (cap_left, cap_right):
            if cap is not None:
                cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
