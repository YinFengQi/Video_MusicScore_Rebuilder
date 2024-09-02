import os

# 获取脚本文件所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"脚本文件所在目录: {script_dir}")

# 基于脚本文件所在目录构建相对路径
output_folder = os.path.join(script_dir, "output_folder")
stitch_folder = os.path.join(script_dir, "stitch")
recut_folder = os.path.join(script_dir, "recut")

print(f"输出文件夹路径: {output_folder}")
print(f"拼接文件夹路径: {stitch_folder}")
print(f"裁剪文件夹路径: {recut_folder}")

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_folder(file_path)
            os.rmdir(file_path)


clear_folder(output_folder)
clear_folder(stitch_folder)
clear_folder(recut_folder)