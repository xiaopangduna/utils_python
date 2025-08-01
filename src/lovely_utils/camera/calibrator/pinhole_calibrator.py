from pathlib import Path
from typing import Any, Optional
from .base_calibrator import BaseCalibrator


class PinholeCalibrator(BaseCalibrator):
    def calibrate_intrinsic(self, images: list[Path] = [],remove_unvalid_image: bool = True, **kwargs) -> None:
        """
        Calibrate the camera.
        """
        images = [Path(img) for img in images]
        valid_images = []
        unvalid_images = []
        for path_img in images:
            if not path_img.exists():
                if remove_unvalid_image:
                    images.remove(path_img)
                else:
                    raise FileNotFoundError(f"Image {path_img} not found.")
        pass

    def apply_intrinsic(self, **kwargs) -> None:
        """
        Apply the intrinsic calibration to the camera.
        """
        pass

    def validate_intrinsic(self, **kwargs) -> None:
        """
        Validate the camera.
        """
        pass

    def calibrate_extrinsic(self, **kwargs) -> None:
        """
        Calibrate the camera.
        """
        pass

    def apply_extrinsic(self, **kwargs) -> None:
        """
        Apply the extrinsic calibration to the camera.
        """
        pass

    def validate_extrinsic(self, **kwargs) -> None:
        """
        Validate the camera.
        """
        pass
