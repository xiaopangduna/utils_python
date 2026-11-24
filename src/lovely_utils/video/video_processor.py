# -*- coding: utf-8 -*-
"""Tools for reading videos and writing image sequences."""

import os

import cv2


class VideoProcessor(object):
    @staticmethod
    def extract_frame_from_video(
        path_video: str, path_save: str, freq: int = 5, prefix: str = "frame"
    ) -> int:
        """Extract frames from a video file at a fixed frame interval.

        Args:
            path_video: Path of the video file.
            path_save: Directory where extracted frames are saved.
            freq: Save one frame every ``freq`` frames. Defaults to 5.
            prefix: Filename prefix. Defaults to ``"frame"``.

        Returns:
            Number of frames written.

        Raises:
            ValueError: ``freq`` is less than 1.
            RuntimeError: The video file cannot be opened.
        """
        if freq < 1:
            raise ValueError(f"freq must be >= 1, got {freq}")

        if not os.path.isdir(path_save):
            os.makedirs(path_save)

        cap = cv2.VideoCapture(path_video)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open video: {path_video}")

        count = 0
        saved = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % freq == 0:
                    path_img = os.path.join(
                        path_save, "{}_{:0>5d}.jpg".format(prefix, count)
                    )
                    if not cv2.imwrite(path_img, frame):
                        raise RuntimeError(f"Failed to save image: {path_img}")
                    print("Success :save image to {}".format(path_img))
                    saved += 1
                count += 1
        finally:
            cap.release()
        return saved

    @staticmethod
    def merge_image_to_video(
        dir_image,
        path_video,
        img_size: tuple,
        fourcc=cv2.VideoWriter_fourcc(*"XVID"),
        frame_rate: int = 30,
        fn=lambda x: int(x.stem),
    ):
        """Merge images in a directory into a video.

        Args:
            dir_image: Directory of source images.
            path_video: Output video path.
            img_size: Video size as ``(width, height)``.
            fourcc: OpenCV fourcc code.
            frame_rate: Output frame rate.
            fn: Unused sort key kept for call-site compatibility.
        """
        print("-" * 70)
        print("Start merge image to video")
        out = cv2.VideoWriter(
            str(path_video), fourcc, frame_rate, img_size, True
        )
        count = 0
        path_images = [p for p in dir_image.iterdir()]
        path_images.sort()
        # path_images.sort(key=fn)
        for path_image in path_images:
            img = cv2.imread(str(path_image))
            out.write(img)
        if img.shape[0] != img_size[1] or img.shape[1] != img_size[0]:
            print(
                "Warn : Image sizes are inconsistent: image size {}*{} != video size {}*{}".format(
                    img.shape[1],
                    img.shape[0],
                    img_size[0],
                    img_size[1],
                )
            )
        print(
            "Extract {}/{} frame from {} to {}".format(
                count, len(path_images), dir_image, path_video
            )
        )
        print("End merge image to video")
        print("*" * 70)
