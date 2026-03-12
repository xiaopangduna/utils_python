#!/usr/bin/env python3
"""
PCD到KITTI BIN格式转换工具

用于将PCD格式的点云数据转换为KITTI数据集使用的BIN格式，以便在OpenPCDet等深度学习框架中使用。
BIN格式是KITTI数据集使用的格式，存储[x, y, z, intensity]四个值的二进制数据。
"""

import numpy as np
import struct
import os
from pathlib import Path
import argparse


def parse_pcd_header(file_path):
    """
    解析PCD文件头部信息
    
    Args:
        file_path: PCD文件路径
        
    Returns:
        dict: 包含头部信息的字典
    """
    header_info = {}
    
    with open(file_path, 'r') as f:
        line_num = 0
        while True:
            line = f.readline().strip()
            if not line:
                continue
            line_num += 1
            
            parts = line.split()
            if not parts:
                continue
                
            key = parts[0]
            if key == 'VERSION':
                header_info['version'] = parts[1]
            elif key == 'FIELDS':
                header_info['fields'] = parts[1:]
            elif key == 'SIZE':
                header_info['size'] = [int(x) for x in parts[1:]]
            elif key == 'TYPE':
                header_info['type'] = parts[1:]
            elif key == 'COUNT':
                header_info['count'] = [int(x) for x in parts[1:]]
            elif key == 'WIDTH':
                header_info['width'] = int(parts[1])
            elif key == 'HEIGHT':
                header_info['height'] = int(parts[1])
            elif key == 'VIEWPOINT':
                header_info['viewpoint'] = [float(x) for x in parts[1:]]
            elif key == 'POINTS':
                header_info['points'] = int(parts[1])
            elif key == 'DATA':
                header_info['data_type'] = parts[1]  # ascii or binary
                break  # 数据类型行标志着头部结束
    
    # 计算字段偏移量
    offsets = [0]
    for i in range(len(header_info['fields']) - 1):
        offsets.append(offsets[-1] + header_info['size'][i])
    header_info['offsets'] = offsets
    
    return header_info


def read_pcd_ascii(file_path, header_info):
    """
    读取ASCII格式的PCD文件
    
    Args:
        file_path: PCD文件路径
        header_info: PCD头部信息
        
    Returns:
        numpy.ndarray: 点云数据
    """
    # 跳过头部，读取数据部分
    with open(file_path, 'r') as f:
        line_num = 0
        while True:
            line = f.readline().strip()
            if not line:
                continue
            parts = line.split()
            if parts and parts[0] == 'DATA':
                break
        
        # 读取数据
        data_lines = f.readlines()
        
    # 解析每一行数据
    points = []
    for line in data_lines:
        values = [float(x) for x in line.split()]
        points.append(values)
    
    return np.array(points)


def read_pcd_binary(file_path, header_info):
    """
    读取二进制格式的PCD文件
    
    Args:
        file_path: PCD文件路径
        header_info: PCD头部信息
        
    Returns:
        numpy.ndarray: 点云数据
    """
    # 计算每点的总字节数
    total_size_per_point = sum(header_info['size'])
    
    # 找到数据部分的起始位置
    with open(file_path, 'rb') as f:
        line_num = 0
        while True:
            line = f.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            parts = line.split()
            if parts and parts[0] == 'DATA':
                break
        
        # 读取二进制数据
        binary_data = f.read()
        
    # 解析二进制数据
    points = []
    point_count = header_info['points']
    
    for i in range(point_count):
        point_start = i * total_size_per_point
        point_values = []
        
        for j, field_type in enumerate(header_info['type']):
            field_offset = header_info['offsets'][j]
            field_size = header_info['size'][j]
            
            value_start = point_start + field_offset
            value_end = value_start + field_size
            
            field_data = binary_data[value_start:value_end]
            
            # 根据字段类型解析数据
            if field_type == 'F':  # float32
                value = struct.unpack('f', field_data)[0]
            elif field_type == 'I':  # uint32
                value = struct.unpack('I', field_data)[0]
            elif field_type == 'U':  # uint8
                value = struct.unpack('B', field_data)[0]
            elif field_type == 'U2':  # uint16
                value = struct.unpack('H', field_data)[0]
            else:  # 默认为float32
                value = struct.unpack('f', field_data)[0]
                
            point_values.append(value)
        
        points.append(point_values)
    
    return np.array(points)


def extract_xyz_intensity(data, fields, intensity_default=0.0):
    """
    从点云数据中提取x, y, z, intensity
    
    Args:
        data: 原始点云数据
        fields: 字段名称列表
        intensity_default: 默认强度值
        
    Returns:
        numpy.ndarray: [N, 4] 格式的点云数据 [x, y, z, intensity]
    """
    # 查找x, y, z, intensity字段的索引
    try:
        x_idx = fields.index('x')
    except ValueError:
        x_idx = -1
        
    try:
        y_idx = fields.index('y')
    except ValueError:
        y_idx = -1
        
    try:
        z_idx = fields.index('z')
    except ValueError:
        z_idx = -1
        
    try:
        intensity_idx = fields.index('intensity')
    except ValueError:
        intensity_idx = -1
    
    # 创建输出数组
    points_with_intensity = np.zeros((data.shape[0], 4), dtype=np.float32)
    
    if x_idx >= 0:
        points_with_intensity[:, 0] = data[:, x_idx]
    if y_idx >= 0:
        points_with_intensity[:, 1] = data[:, y_idx]
    if z_idx >= 0:
        points_with_intensity[:, 2] = data[:, z_idx]
    
    if intensity_idx >= 0:
        points_with_intensity[:, 3] = data[:, intensity_idx]
    else:
        # 如果没有强度信息，使用默认值
        points_with_intensity[:, 3] = intensity_default
    
    return points_with_intensity


def transform_kitti_points(points_with_intensity, rotate_z_180=True, translate_x=0.0):
    """
    对点云数据进行KITTI格式变换
    
    Args:
        points_with_intensity: [N, 4] 格式的点云数据 [x, y, z, intensity]
        rotate_z_180: 是否绕z轴旋转180度（即x和y坐标取反）
        translate_x: x轴平移量
        
    Returns:
        numpy.ndarray: 变换后的点云数据
    """
    transformed_points = points_with_intensity.copy()
    
    if rotate_z_180:
        # 绕z轴旋转180度，即x和y坐标取反
        transformed_points[:, 0] = -transformed_points[:, 0]  # x坐标取反
        transformed_points[:, 1] = -transformed_points[:, 1]  # y坐标取反
    
    # x轴平移
    transformed_points[:, 0] += translate_x
    # transformed_points[:, 2] -= 0.5
    
    return transformed_points


def convert_pcd_to_kitti_bin(pcd_file_path, bin_file_path, intensity_default=0.0, 
                             apply_transform=True, rotate_z_180=True, translate_x=30.0):
    """
    转换单个PCD文件为KITTI BIN格式
    
    Args:
        pcd_file_path: 输入PCD文件路径
        bin_file_path: 输出BIN文件路径
        intensity_default: 默认强度值
        apply_transform: 是否应用KITTI格式变换（旋转+平移）
        rotate_z_180: 是否绕z轴旋转180度
        translate_x: x轴平移量
        
    Returns:
        bool: 转换是否成功
    """
    try:
        # 解析PCD头部
        header_info = parse_pcd_header(pcd_file_path)
        
        # 根据数据类型读取PCD文件
        if header_info['data_type'] == 'ascii':
            data = read_pcd_ascii(pcd_file_path, header_info)
        elif header_info['data_type'] == 'binary':
            data = read_pcd_binary(pcd_file_path, header_info)
        else:
            print(f"错误: 不支持的数据类型 {header_info['data_type']}")
            return False
        
        # 提取x, y, z, intensity数据
        points_with_intensity = extract_xyz_intensity(
            data, 
            header_info['fields'], 
            intensity_default
        )
        
        # 根据参数决定是否应用KITTI格式变换
        if apply_transform:
            kitti_points = transform_kitti_points(
                points_with_intensity,
                rotate_z_180=rotate_z_180,
                translate_x=translate_x
            )
        else:
            kitti_points = points_with_intensity
        
        # 保存为KITTI BIN格式
        with open(bin_file_path, 'wb') as f:
            # 将数据转换为float32并展平
            data_flat = kitti_points.astype(np.float32).flatten()
            # 写入二进制数据
            f.write(data_flat.tobytes())
        
        if apply_transform:
            print(f"成功将 {pcd_file_path} 转换为KITTI格式 {bin_file_path}")
            print(f"应用了KITTI变换: 绕z轴旋转180度={rotate_z_180}, x轴平移={translate_x}")
        else:
            print(f"成功将 {pcd_file_path} 转换为 {bin_file_path}（无KITTI变换）")
        
        return True
        
    except Exception as e:
        print(f"转换PCD文件 {pcd_file_path} 时发生错误: {e}")
        return False


def convert_directory_pcd_to_kitti_bin(pcd_dir, bin_dir, intensity_default=0.0, 
                                      apply_transform=True, rotate_z_180=True, translate_x=30.0):
    """
    转换目录中所有PCD文件为KITTI BIN格式
    
    Args:
        pcd_dir: 包含PCD文件的目录
        bin_dir: 输出BIN文件的目录
        intensity_default: 默认强度值
        apply_transform: 是否应用KITTI格式变换（旋转+平移）
        rotate_z_180: 是否绕z轴旋转180度
        translate_x: x轴平移量
        
    Returns:
        int: 成功转换的文件数量
    """
    pcd_dir = Path(pcd_dir)
    bin_dir = Path(bin_dir)
    
    # 创建输出目录
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有PCD文件
    pcd_files = list(pcd_dir.glob("*.pcd"))
    
    success_count = 0
    
    for pcd_file in pcd_files:
        # 生成对应的BIN文件名
        bin_file = bin_dir / f"{pcd_file.stem}.bin"
        
        # 转换文件
        if convert_pcd_to_kitti_bin(
            str(pcd_file), 
            str(bin_file), 
            intensity_default,
            apply_transform,
            rotate_z_180,
            translate_x
        ):
            success_count += 1
    
    print(f"成功转换 {success_count}/{len(pcd_files)} 个文件为KITTI格式")
    return success_count


def main():
    parser = argparse.ArgumentParser(description='PCD到KITTI BIN格式转换工具')
    parser.add_argument('--input', '-i', required=True, help='输入PCD文件路径或目录')
    parser.add_argument('--output', '-o', required=True, help='输出KITTI BIN文件路径或目录')
    parser.add_argument('--intensity-default', '-id', type=float, default=0.0, 
                       help='默认强度值（当PCD中没有强度信息时使用）')
    parser.add_argument('--apply-transform', action='store_true', 
                       help='应用KITTI格式变换（旋转+平移）')
    parser.add_argument('--no-transform', action='store_true', 
                       help='不应用任何KITTI格式变换（默认应用变换）')
    parser.add_argument('--no-rotate-z', action='store_true', 
                       help='不对z轴进行180度旋转（默认开启，仅在应用变换时生效）')
    parser.add_argument('--translate-x', type=float, default=0.0, 
                       help='x轴平移量（默认0.0，仅在应用变换时生效）')
    
    args = parser.parse_args()
    
    # 确定是否应用变换
    if args.no_transform:
        apply_transform = False
    elif args.apply_transform:
        apply_transform = True
    else:
        # 默认应用变换
        apply_transform = True
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_file():
        # 单个文件转换
        if input_path.suffix.lower() != '.pcd':
            print(f"错误: 输入文件不是PCD格式: {args.input}")
            return 1
        
        if output_path.suffix.lower() != '.bin':
            print(f"错误: 输出文件不是BIN格式: {args.output}")
            return 1
        
        success = convert_pcd_to_kitti_bin(
            str(input_path), 
            str(output_path), 
            args.intensity_default,
            apply_transform,
            rotate_z_180=not args.no_rotate_z,
            translate_x=args.translate_x
        )
        
        return 0 if success else 1
    
    elif input_path.is_dir():
        # 目录转换
        success_count = convert_directory_pcd_to_kitti_bin(
            str(input_path), 
            str(output_path), 
            args.intensity_default,
            apply_transform,
            rotate_z_180=not args.no_rotate_z,
            translate_x=args.translate_x
        )
        
        return 0 if success_count > 0 else 1
    
    else:
        print(f"错误: 输入路径不存在: {args.input}")
        return 1


if __name__ == "__main__":
    exit(main())