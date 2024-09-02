from PIL import Image
import os
import numpy as np
import subprocess

# 读取txt文件
def read_txt(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = {}
    for line in lines:
        image_name, coordinates = line.split(": ")
        coordinates = list(map(int, coordinates.strip('[]\n').split(', ')))
        data[image_name] = coordinates
    return data

def run_script(script_name):
    script_path = os.path.join(current_directory, f"{script_name}.py")
    print(f"Running {script_name}...")
    try:
        subprocess.run(['python3.11', script_path, 'config.ini'], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e}\n")
        
# 主函数
def main(txt_file):
    # 清空recut文件夹
    current_directory = os.path.dirname(os.path.abspath(__file__))
    recut_folder = os.path.join(current_directory, 'recut')
    photo_folder = os.path.join(current_directory, 'output_folder')
    
    # 读取recut_folder中的第一张图片的高度
    first_image_path = os.path.join(photo_folder, "0.png")
    first_image = Image.open(first_image_path)
    height = first_image.height
    print(f"Height of the first image: {height}")
    
    for file_name in os.listdir(recut_folder):
        file_path = os.path.join(recut_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    data = read_txt(txt_file)
    for image_name, coordinates in data.items():
        print(f"Image Path: {image_name}")
        print(f"Coordinates: {coordinates}")
        print()

        # 计算数据两两间隔的中位数
        intervals = []
        for i in range(len(coordinates)-1):
            interval = coordinates[i+1] - coordinates[i]
            intervals.append(interval)
        median_interval = np.median(intervals)
        print(f"Median Interval for {image_name}: {median_interval}")
        end = []

        # 对应每个键，再计算一遍两两数据间距的中位数，若某个键对应的数组有两个元素间距小于一定值，将这两个元素中的第一个元素删掉，第二个元素分到一个新类“end”里
        break_points = {}
        expected_width=10*height
        for image_name, coordinates in data.items():
            
            new_coordinates = []
            for i in range(len(coordinates)-1):
                interval = coordinates[i+1] - coordinates[i]
                if interval < 0.3*median_interval:
                    print(f"Removed Coordinate: {coordinates[i]}")
                    end.append(coordinates[i+1])
                    continue
                new_coordinates.append(coordinates[i])
            new_coordinates.append(coordinates[-1])
            data[image_name] = new_coordinates
            i = 0
            while i < len(new_coordinates):
                num = new_coordinates[i]
                j = i+2
                while j < len(new_coordinates):
                    if new_coordinates[j] - new_coordinates[i] > expected_width:
                        if image_name not in break_points:
                            break_points[image_name] = []
                        break_points[image_name].append(new_coordinates[j])
                        i = j - 1
                        break
                    j =j+1
                i =i+1
            break_points[image_name].append(new_coordinates[-1])
            #for end_coordinates in end:
            #    break_points[image_name].append(end_coordinates)
            #print(f"Break Points for {image_name}: {break_points}")不知为什么这步加不进去
                            
                    

            
        #按照data的键值读取图像
        k=0
        for image_name in data.keys():
            k+=1
            stitch_folder = os.path.join(current_directory, 'stitch')
            image_path = os.path.join(stitch_folder, image_name)
            image = Image.open(image_path)
            
            if image_name in break_points:
                break__points= break_points[image_name]
                break__points.insert(0,0)
                for i in range(len(break__points)-1):
                    cropped_image = image.crop((break__points[i], 0, break__points[i+1], image.height))
                    output_path = f"/Users/pleiades/Documents/VSCode/python/recut/{k}_{break__points[i]}.pdf"
                    if cropped_image is not None and cropped_image.size[0] != 0 and cropped_image.size[1] != 0:
                        cropped_image.save(output_path, "PDF", resolution=100.0)
                    else:
                        print(f"Error: Cropped image is empty for {image_name}")
                    print(f"Saved Cropped Image to {output_path}")
                    
    run_script('rename')
    
    
# 参数设置
current_directory = os.path.dirname(os.path.abspath(__file__))
txt_file = os.path.join(current_directory,"align_lines.txt") # txt文件路径

main(txt_file)
