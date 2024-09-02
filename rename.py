import os
import numpy as np
#无可调参数

def rename_images_in_directory(directory):
    # 获取目录中的所有文件
    all_files = os.listdir(directory)
    
    # 过滤出符合条件的文件
    images = []
    for file in all_files:
        if file.startswith('frame_'):
            parts = file.split('_')
            if len(parts) > 1 and parts[1].split('.')[0].isdigit():
                images.append(file)
    
    # 按文件名中的数字部分排序
    def extract_number(file):
        return int(file.split('_')[1].split('.')[0])
    
    sorted_images = sorted(images, key=extract_number)
    
    # 重命名文件
    for i, file in enumerate(sorted_images):
        file_extension = os.path.splitext(file)[1]
        new_name = f"{i}{file_extension}"
        os.rename(os.path.join(directory, file), os.path.join(directory, new_name))
    
    print("Images renamed successfully.")
def rename_png_in_directory(directory):
    # 获取目录中的所有文件
    all_files = os.listdir(directory)
    
    # 过滤出符合条件的 PNG 文件
    png_files = []
    for file in all_files:
        if file.endswith('.png') and file[:-4].isdigit():
            png_files.append(file)
    
    # 按文件名中的数字部分排序
    sorted_files = sorted(png_files, key=lambda x: int(x[:-4]))
    
    # 重命名文件
    for i, file in enumerate(sorted_files):
        file_extension = os.path.splitext(file)[1]
        new_name = f"{i}{file_extension}"
        os.rename(os.path.join(directory, file), os.path.join(directory, new_name))
    
    print("PNG files renamed successfully.")
def rename_pdf_in_directory(directory):
    # 获取目录中的所有文件
    all_files = os.listdir(directory)
    
    # 过滤出符合条件的 PDF 文件
    pdf_files = []
    for file in all_files:
        if file.endswith('.pdf'):
            name_parts = file.split('.')[0].split('_')
            if len(name_parts) == 2 and name_parts[0].isdigit() and name_parts[1].isdigit():
                pdf_files.append(file)
    
    # 按文件名中的数字部分排序
    def sort_key(file):
        name_parts = file.split('.')[0].split('_')
        return (int(name_parts[0]), int(name_parts[1]))
    
    sorted_files = sorted(pdf_files, key=sort_key)
    
    # 重命名文件
    for i, file in enumerate(sorted_files):
        file_extension = os.path.splitext(file)[1]
        new_name = f"{i}{file_extension}"
        os.rename(os.path.join(directory, file), os.path.join(directory, new_name))
    
    print("Images renamed successfully.")



if __name__ == "__main__":
    output2_dir = "/Users/pleiades/Documents/VSCode/python/recut"  # Replace with your actual input directory path
    output_dir = "/Users/pleiades/Documents/VSCode/python/output_folder"  # Replace with your actual output directory path
    
    # Rename images in input directory
    rename_pdf_in_directory(output2_dir)
    
    # Rename images in output directory
    rename_images_in_directory(output_dir)
    rename_png_in_directory(output_dir)
