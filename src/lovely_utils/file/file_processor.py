#!C:/A_Programme/Miniconda/envs/py310 python
# -*- coding: utf-8 -*-
"""
@File    :   file_processor.py
@Time    :   2024/03/20 22:15:52
@Author  :   xiaopangdun
@Email  :   18675381281@163.com
@Version :   1.0
@Desc    :   None
"""
import os
import shutil


class FileProcessor(object):

    @staticmethod
    def rename_file(
        dir_input: str,
        dir_output: str = None,
        initial_num: int = 1,
        prefix: str = "",
        separator: str = "_",
        suffix: str = "",
        key=lambda x: int(x[:-4]),
    ):
        """Copy and rename files.

        Args:
            dir_input (str): The path of floder which save original file.
            dir_output (str): The path of floder which save target file.
            initial_num (int, optional): The initial number of the file name. Defaults to 1.
            prefix (str, optional): The prefix of file name . Defaults to "".
            separator (str, optional): The separator of file name. Defaults to "_".
            suffix (str, optional): THe suffix of file name. Defaults to "".

        Example:
            path_input = r"D:/A_Project/database/park_slot/train_harbor_vital"
            path_output = r"D:/A_Project/database/park_slot/train_harbor_vital"
            initial_num = 1
            prefix = "240316"
            separator = "_"
            suffix = "03"
            processor = FileProcessor()
            processor.copy_and_rename_files(
                path_input, path_output, initial_num, prefix, separator, suffix
            )
            # file name
            # 240316_03_00001.jpg
        """
        # check dir is exits.
        if not os.path.isdir(dir_input):
            print("Error  :floder is not exit.")
            print("path of dir_input: {}".format(dir_input))
        # get file name
        names = os.listdir(dir_input)
        names.sort(key=key)
        for name in names:
            # copy and renmae file
            path_old = os.path.join(dir_input, name)
            if dir_output and dir_input != dir_output:
                path_new = os.path.join(
                    dir_output,
                    "{}{}{}{}{:05d}{}".format(
                        prefix,
                        separator,
                        suffix,
                        separator,
                        initial_num,
                        os.path.splitext(name)[-1],
                    ),
                )
                shutil.copyfile(path_old, path_new)
                print("Success :copy {} to {}".format(path_old, path_new))
            else:
                path_new = os.path.join(
                    dir_input,
                    "{}{}{}{}{:05d}{}".format(
                        prefix,
                        separator,
                        suffix,
                        separator,
                        initial_num,
                        os.path.splitext(name)[-1],
                    ),
                )
                os.rename(path_old, path_new)
                print("Success :rename {} to {}".format(path_old, path_new))
            initial_num += 1


if __name__ == "__main__":

    import os

    folder_path = '/home/ubuntu/桌面/project/fall_detection_2504/dataset/0415/250415_05'  # 替换为目标文件夹路径
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg') and '_00_' in filename:
            new_filename = filename.replace('_00_', '_05_')
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))

    pass
