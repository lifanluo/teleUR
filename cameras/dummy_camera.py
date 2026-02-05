from typing import Optional, Tuple

import numpy as np

from .camera import CameraDriver


class DummyCamera(CameraDriver):
    """A dummy camera that returns black images and zero depth.

    Useful when running without a physical RealSense device.
    """

    def __init__(self, height: int = 480, width: int = 640):
        self.height = height
        self.width = width

    def read(
        self,
        img_size: Optional[Tuple[int, int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        h, w = self.height, self.width
        if img_size is not None:
            w, h = img_size
        color = np.zeros((h, w, 3), dtype=np.uint8)
        depth = np.zeros((h, w), dtype=np.uint16)
        return color, depth
