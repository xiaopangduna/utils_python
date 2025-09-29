from pathlib import Path

# ===== 配置部分 =====
# 图片文件夹路径
IMG_DIR = Path("/home/ubuntu/Desktop/project/2504_fall_detection/dataset/20250928/luohubei_image")
# 新文件名前缀
PREFIX = "luohubei_20250928_fall_detection_test_frame"
# 序号位数（5 表示 00001, 00002...）
SEQ_DIGITS = 5

# ===== 执行部分 =====
if not IMG_DIR.exists():
    print(f"错误：图片文件夹不存在 -> {IMG_DIR}")
    exit(1)

# 获取所有 .jpg 文件，并按文件名排序
jpg_files = sorted([f for f in IMG_DIR.glob("*.jpg") if f.is_file()])

if not jpg_files:
    print(f"在 {IMG_DIR} 中没有找到任何 .jpg 文件")
    exit(0)

# 遍历并改名
for idx, old_path in enumerate(jpg_files, start=1):
    # 生成序号（补零）
    seq_str = f"{idx:0{SEQ_DIGITS}d}"
    new_name = f"{PREFIX}{seq_str}.jpg"
    new_path = IMG_DIR / new_name

    # 重命名
    old_path.rename(new_path)
    print(f"重命名: {old_path.name} -> {new_name}")

print(f"\n✅ 重命名完成！共处理 {len(jpg_files)} 张图片")

# from pathlib import Path

# # ===== 配置 =====
# IMG_DIR = Path("/home/ubuntu/Desktop/project/2504_fall_detection/dataset/20250928/liangmaoshan_image")  # 图片所在文件夹
# OLD_PREFIX = "luohubei"
# NEW_PREFIX = "liangmaoshan"

# # ===== 执行 =====
# if not IMG_DIR.exists():
#     print(f"错误：文件夹不存在 -> {IMG_DIR}")
#     exit(1)

# count = 0
# for img_path in IMG_DIR.glob("*.jpg"):
#     if img_path.name.startswith(OLD_PREFIX):
#         new_name = img_path.name.replace(OLD_PREFIX, NEW_PREFIX, 1)  # 只替换第一个匹配
#         new_path = img_path.with_name(new_name)
#         img_path.rename(new_path)
#         print(f"重命名: {img_path.name} -> {new_name}")
#         count += 1

# print(f"\n✅ 完成！共重命名 {count} 个文件")