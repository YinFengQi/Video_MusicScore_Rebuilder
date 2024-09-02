import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取参数
manual = config['detect']['manual'].lower() == 'true'
single_line = config['detect']['single_line'].lower() == 'true'

import cv2
import numpy as np
import os
import shutil

def read_stitched_images(image_path):
    stitched_images = []
    for filename in os.listdir(image_path):
        if "stitched" in filename:
            stitched_images.append(os.path.join(image_path, filename))
    stitched_images.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    return stitched_images

def preprocess_image(image_path):
    # 读取图像
    img = cv2.imread(image_path)
    
    # 转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 将较浅的灰色变为白色
    _, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
      
    # 保存处理后的图像
    preprocess_folder = os.path.join(os.path.dirname(image_path), 'preprocess')
    os.makedirs(preprocess_folder, exist_ok=True)
    processed_path = os.path.join(preprocess_folder, 'processed.png')
    cv2.imwrite(processed_path, binary)
    
    return processed_path

def compare_lines(image_path):
    # 读取图像
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 逐行比较相邻行的像素差异
    max_diff = 0
    diff_values = []  # 存储每行的差值
    for i in range(1, gray.shape[0]):
        diff=0
        for j in range(1, gray.shape[1]):
            diff += np.abs(int(gray[i, j]) - int(gray[i-1, j]))
        if diff > max_diff:
            max_diff = diff
        diff_values.append(diff)  # 将差值添加到列表中
    
    # 可视化输出每行的差值
    import matplotlib.pyplot as plt
    plt.plot(diff_values)
    plt.xlabel('Row')
    plt.ylabel('Difference')
    plt.title('Difference between adjacent rows')
    plt.show()
    
    return max_diff

def find_max_diff_y(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 逐行比较相邻行的像素差异
    reco_diff=0.8*compare_lines(image_path)
    for i in range(1, gray.shape[0]):
        diff=0
        for j in range(1, gray.shape[1]):
            diff =diff+ np.abs(int(gray[i, j]) - int(gray[i-1, j]))
        if diff > reco_diff:
            break
    return i

def select_point(image_path):
    # 读取图像
    zoom_factor = 1.0
    selected_point = None
    img = cv2.imread(image_path)
    height = img.shape[0]
    width = img.shape[1]
    new_width = int(height * 3)
    img = cv2.resize(img, (new_width, height))
    def on_mouse(event, x, y, flags, param):
        nonlocal selected_point
        if event == cv2.EVENT_LBUTTONDOWN:
            # 记录点击的点
            selected_point = (int(x / zoom_factor), int(y / zoom_factor))
            cv2.destroyAllWindows()

    def update_display():
        zoomed_img = cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Select Point", zoomed_img)

    # 创建窗口并设置鼠标回调
    cv2.namedWindow("Select Point", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Select Point", on_mouse)

    # 显示图像
    update_display()

    # 等待用户选择点或按键
    while selected_point is None:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 按 'q' 键退出
            break
        elif key == 82:  # 上键
            zoom_factor *= 1.1
            update_display()
        elif key == 84:  # 下键
            zoom_factor /= 1.1
            zoom_factor = max(zoom_factor, 1.0)
            update_display()

    return selected_point

def detect_measures(image_path, output_path):
    aligned_lines=[]
    # 读取图像
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if manual:
        # 手动选择y坐标
        max_diff_y = select_point(image_path)[1]
    else:
        max_diff_y = find_max_diff_y(image_path)

    # 在图像对应的y处画一条横线
    cv2.line(img, (0, max_diff_y), (img.shape[1], max_diff_y), (0, 0, 255), 1)
    
    # 二值化处理
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)


    # 检测垂直线
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # 查找轮廓
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    red_lines = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # 检查垂直线的高度是否在指定范围内
        if h >= img.shape[0] / 10 and h <= img.shape[0] / 2:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            red_lines.append((x, y, w, h))
            
    aligned_lines = []

    if len(red_lines) >= 2:
        if single_line:
            red_lines.sort(key=lambda line: line[0])  # 按x坐标排序
            for i in range(len(red_lines)):
                aligned_lines.append((red_lines[i][0], red_lines[i][1]))
        else:
            red_lines.sort(key=lambda line: line[0])  # 按x坐标排序
            for i in range(len(red_lines) - 1):
                for j in range(i + 1, min(i + 4, len(red_lines))):
                    line1 = red_lines[i]
                    line2 = red_lines[j]
                    if abs(line1[0] - line2[0]) <= 5:  # 判断两条线是否对齐
                        cv2.rectangle(img, (line1[0], line1[1]), (line1[0] + line1[2], line1[1] + line1[3]), (0, 0, 255), 2)
                        cv2.rectangle(img, (line2[0], line2[1]), (line2[0] + line2[2], line2[1] + line2[3]), (0, 0, 255), 2)
                        if line1[0] not in aligned_lines and line1[1] < img.shape[0] / 2:
                            aligned_lines.append((line1[0], line1[1]))
                        if line2[0] not in aligned_lines and line2[1] < img.shape[0] / 2:
                            aligned_lines.append((line2[0], line2[1]))
        
    #删除离谱线过远的元素
    aligned_lines = [line for line in aligned_lines if abs(line[1] - max_diff_y) < 10]
                    
    # 在原图像上标记检测到的小节线                
    for x in aligned_lines:
        cv2.line(img, (x[0], 0), (x[0], img.shape[0]), (255, 0, 0), 1)
    # 保存结果图像
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Save the detected measures image
    output_filename = "detected_" + os.path.basename(output_path)
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, img)
    print(f"Saved detected measures to {output_path}.")
    if not aligned_lines:
        raise ValueError("No aligned lines detected.")
    x_coordinates = [line[0] for line in aligned_lines]
    return x_coordinates

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))

    image_folder = os.path.join(current_directory, 'stitch')  # 替换为你的图片文件夹路径
    output_folder = os.path.join(current_directory, 'detect')  # 替换为你想保存的结果文件夹路径

    # 读取文件夹中的所有图片
    image_paths = read_stitched_images(image_folder)
    # 清空输出文件夹
    shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    # 遍历每张图片进行处理和检测
    aligned_lines_list = []
    for image_path in image_paths:
        # 预处理图像
        processed_path = preprocess_image(image_path)

        # 检测小节线并保存结果图像
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        aligned_lines = detect_measures(processed_path, output_path)
        aligned_lines_list.append(aligned_lines)
        # 遍历每张图片的对齐线坐标
        for aligned_lines in aligned_lines_list:
            # 存储每个长条图像返回的align_lines值
            with open(os.path.join(current_directory, "align_lines.txt"), "w") as file:
                for i, aligned_lines in enumerate(aligned_lines_list):
                    file.write(f"{os.path.basename(image_paths[i])}: {aligned_lines}\n")