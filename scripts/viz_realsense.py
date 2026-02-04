#!/usr/bin/env python3
"""
Visualize RealSense camera streams (RGB, depth, infrared).

Usage:
    python scripts/viz_realsense.py --device-id 0 --mode rgb
    python scripts/viz_realsense.py --device-id 0 --mode depth
    python scripts/viz_realsense.py --device-id 0 --mode all

Modes:
    rgb         - RGB color stream only
    depth       - Depth map (colorized)
    ir          - Infrared streams
    all         - RGB + Depth side-by-side (default)

Controls:
    'q'         - Quit
    's'         - Save current frame(s)
    'd'         - Toggle depth colormap
"""
import argparse
import time
import os
from datetime import datetime

import cv2
import numpy as np

try:
    import pyrealsense2 as rs
except ImportError:
    print("ERROR: pyrealsense2 not installed. Install with: pip install pyrealsense2")
    exit(1)


def colorize_depth(depth_frame, depth_scale=0.001):
    """Colorize depth frame for visualization."""
    depth_array = np.asanyarray(depth_frame.get_data())
    depth_colormap = cv2.applyColorMap(
        cv2.convertScaleAbs(depth_array, alpha=0.03), cv2.COLORMAP_JET
    )
    return depth_colormap


def main():
    parser = argparse.ArgumentParser(description="Visualize RealSense camera streams")
    parser.add_argument(
        "--device-id", type=int, default=0, help="RealSense device index"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["rgb", "depth", "ir", "all"],
        default="all",
        help="Visualization mode",
    )
    parser.add_argument(
        "--width", type=int, default=640, help="Frame width"
    )
    parser.add_argument(
        "--height", type=int, default=480, help="Frame height"
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Frame rate"
    )
    parser.add_argument(
        "--save-dir", type=str, default="./realsense_captures", help="Save directory"
    )
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    # Create pipeline
    pipeline = rs.pipeline()
    config = rs.config()

    # Enable streams
    config.enable_stream(rs.stream.color, args.width, args.height, rs.format.bgr8, args.fps)
    config.enable_stream(rs.stream.depth, args.width, args.height, rs.format.z16, args.fps)

    if args.mode == "ir":
        config.enable_stream(
            rs.stream.infrared, 1, args.width, args.height, rs.format.y8, args.fps
        )
        config.enable_stream(
            rs.stream.infrared, 2, args.width, args.height, rs.format.y8, args.fps
        )

    try:
        profile = pipeline.start(config)
        device = profile.get_device()
        print(f"✓ Connected to {device.get_info(rs.camera_info.name)}")
        print(f"  Serial: {device.get_info(rs.camera_info.serial_number)}")

        # Align depth to color
        align = rs.align(rs.stream.color)

        colormap_mode = 0  # 0=JET, 1=TURBO, 2=HOT
        colormaps = {0: "JET", 1: "TURBO", 2: "HOT"}

        prev_time = time.time()
        fps_counter = 0

        while True:
            # Wait for frames
            frames = pipeline.wait_for_frames()
            frames = align.process(frames)

            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()

            if not color_frame or not depth_frame:
                print("Failed to get frames")
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # Colorize depth
            if colormap_mode == 0:
                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
                )
            elif colormap_mode == 1:
                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_TURBO
                )
            else:
                depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_HOT
                )

            # Create display based on mode
            if args.mode == "rgb":
                display = color_image
            elif args.mode == "depth":
                display = depth_colormap
            elif args.mode == "ir":
                ir_frame_1 = frames.get_infrared_frame(1)
                ir_frame_2 = frames.get_infrared_frame(2)
                if ir_frame_1 and ir_frame_2:
                    ir1 = np.asanyarray(ir_frame_1.get_data())
                    ir2 = np.asanyarray(ir_frame_2.get_data())
                    ir1_color = cv2.cvtColor(ir1, cv2.COLOR_GRAY2BGR)
                    ir2_color = cv2.cvtColor(ir2, cv2.COLOR_GRAY2BGR)
                    display = np.hstack((ir1_color, ir2_color))
                else:
                    display = color_image
            else:  # all
                display = np.hstack((color_image, depth_colormap))

            # Add FPS and info
            fps_counter += 1
            now = time.time()
            if fps_counter >= 10:
                fps = fps_counter / (now - prev_time)
                prev_time = now
                fps_counter = 0
            else:
                fps = 0

            cv2.putText(
                display,
                f"FPS: {fps:.1f} | Colormap: {colormaps[colormap_mode]} | Mode: {args.mode}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.imshow(f"RealSense Device {args.device_id}", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("Quitting...")
                break
            elif key == ord("s"):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                color_path = os.path.join(args.save_dir, f"color_{ts}.png")
                depth_path = os.path.join(args.save_dir, f"depth_{ts}.png")
                cv2.imwrite(color_path, color_image)
                cv2.imwrite(depth_path, depth_colormap)
                print(f"✓ Saved {color_path} and {depth_path}")
            elif key == ord("d"):
                colormap_mode = (colormap_mode + 1) % 3
                print(f"Colormap: {colormaps[colormap_mode]}")

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        print("RealSense pipeline stopped")


if __name__ == "__main__":
    main()
