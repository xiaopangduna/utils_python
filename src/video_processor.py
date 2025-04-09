#!C:/A_Programme/Miniconda/envs/py310 python
# -*- coding: utf-8 -*-
"""
@File    :   video_processor.py
@Time    :   2024/03/20 21:39:05
@Author  :   xiaopangdun
@Email  :   18675381281@163.com
@Version :   1.0
@Desc    :  This is a library of tools for working with video,includes features:
    video frame extraction,
"""

import os
from pathlib import Path

import cv2


class VideoProcessor(object):
    @staticmethod
    def extract_frame_from_video(
        path_video: str, path_save: str, freq: int = 5, prefix: str = "frame"
    ):
        """Extract frames from a video file at a certain frequency.

        Args:
            path_video (str): The path of video.
            path_save (str): The path of folder to save frames.
            freq (int): The frequency of extract frames.Default to 5.
            prefix (str): The prefix of the image name.Default to "frame".
        Example:
            path_video = r"D:/A_Project/database/03_cam0_bev_3_300.avi"
            path_save = r"D:/A_Project/database/park_slot/tain_harbor_vital"
            video_processor = VideoProcessor()
            video_processor.extract_frame_from_video(path_video, path_save)
        """
        # check path_save is exist
        if not os.path.isdir(path_save):
            os.makedirs(path_save)

        cap = cv2.VideoCapture(path_video)
        # check video is open
        if not cap.isOpened():
            print("Error  :Failed to open video")
            print("video path : {}".format(path_video))
        count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % freq == 0:
                path_img = os.path.join(
                    path_save, "{}_{:0>5d}.jpg".format(prefix, count)
                )
                cv2.imwrite(path_img, frame)
                print("Success :save image to {}".format(path_img))
            count += 1
        cap.release()

    @staticmethod
    def merge_image_to_video(
        dir_image: Path,
        path_video: Path,
        img_size: tuple,
        fourcc=cv2.VideoWriter_fourcc(*"XVID"),
        frame_rate: int = 30,
        fn=lambda x: int(x.stem),
    ):
        """

        Args:
            path_video (str): The path of video.
            path_save (str): The path of folder to save frames.
            freq (int): The frequency of extract frames.Default to 5.
            prefix (str): The prefix of the image name.Default to "frame".
        Example:
            path_video = r"D:/A_Project/database/03_cam0_bev_3_300.avi"
            path_save = r"D:/A_Project/database/park_slot/tain_harbor_vital"
            video_processor = VideoProcessor()
            video_processor.extract_frame_from_video(path_video, path_save)
        """
        print("-" * 70)
        print("Start merge image to video")
        out = cv2.VideoWriter(
            str(path_video), fourcc, frame_rate, img_size, True
        )
        count = 0
        path_images = [p for p in dir_image.iterdir()]
        # path_images.sort()
        path_images.sort(key=fn)
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


if __name__ == "__main__":
    # -----------------------------------------------------------------
    # # extract_frame_from_video
    # path_video = r"D:\A_Project\database\03_cam0_bev_3_300.avi"
    # path_save = r"D:\A_Project\database\park_slot\tain_harbor_vital"
    # video_processor = VideoProcessor()
    # video_processor.extract_frame_from_video(path_video, path_save)

    # -----------------------------------------------------------------
    # # extract_frame_from_video

    dir_images = [
        Path(
            r"/home/ubuntu/桌面/project/fall_detection_2504/dataset/0407_exp2"
        )
    ]
    dir_save = Path(r"/home/ubuntu/桌面/project/fall_detection_2504/dataset")
    img_size = (640, 480)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    frame_rate = 5              
    processor = VideoProcessor()
    for dir_image in dir_images:
        path_video = dir_save.joinpath(dir_image.name + ".avi")
        processor.merge_image_to_video(
            dir_image, path_video, img_size, fourcc, frame_rate,fn=lambda x: int(x.stem.split("_")[-1])
        )
    pass
