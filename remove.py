import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取参数
is_similar_threshold = float(config['remove']['is_similar_threshold'])
is_colorful_threshold = float(config['remove']['is_colorful_threshold'])
is_colorful_grey = float(config['remove']['is_colorful_grey'])
is_mostly_black_black_threshold = float(config['remove']['is_mostly_black_black_threshold'])
photo_range = int(config['remove']['range'])
cut_right = float(config['remove']['cut_right'])

print("参数已接收")

# 这里是 remove.py 的其余逻辑
import cv2
import numpy as np
import os
import subprocess
#可调参数：is_similar的threshold,is_clolrful的threshold，is_mostly_black的black_threshold
def run_script(script_name):
    script_path = os.path.join(current_directory, f"{script_name}.py")
    print(f"Running {script_name}...")
    try:
        subprocess.run(['python3.11', script_path, 'config.ini'], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e}\n")
def is_similar(img1,img2,is_similar_threshold=is_similar_threshold):
    
        if img1 is None or img2 is None:
            return 0
        
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        
        if h1 != h2:
            new_height = min(h1, h2)
            img1 = cv2.resize(img1, (w1, new_height))
            img2 = cv2.resize(img2, (w2, new_height))
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            
        cutup = 0.2
        cutbot = 0.2
        cut_top = int(cutup * h1)
        cut_bottom = int((1 - cutbot) * h1)
        right_part_img1 = img1[cut_top:cut_bottom, int( (1-cut_right)*w1):w1]
        
        result = cv2.matchTemplate(img2, right_part_img1, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.9:  # 设定阈值
            top_left = max_loc
        else:
            return 0
        key=(abs(top_left[0]-(1-cut_right)*w1))
        if (key<is_similar_threshold*w1):
            return 1
        else:
            return 0
    


def is_colorful(image, is_colorful_threshold=is_colorful_threshold):
    # 将图像转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 定义一个低饱和度的阈值，将其视为灰度像素
    saturation_threshold = is_colorful_grey
    
    # 计算饱和度高于阈值的彩色像素数量
    colorful_pixels = np.sum(hsv_image[:, :, 1] > saturation_threshold)
    
    # 计算彩色像素占总像素的百分比
    total_pixels = image.shape[0] * image.shape[1]
    colorful_percentage = (colorful_pixels / total_pixels) * 100
    
    return colorful_percentage > is_colorful_threshold


def remove_similar_frames(output_dir):
    images = sorted([os.path.join(output_dir, img) for img in os.listdir(output_dir) if img.endswith('.png')])
    
    if len(images) > 0:
        unique_images = []  # 用于存储唯一图片
        deleted = [False] * len(images)
        
        for i in range(len(images)):
            if deleted[i]:
                continue  # 跳过已删除的图片
    
            current_image = cv2.imread(images[i])
            if current_image is None:
                continue
            
            # 移除彩色占比高于阈值的帧
            if is_colorful(current_image, is_colorful_threshold):
                os.remove(images[i])
                deleted[i] = True
                continue
            
            is_unique = True
            
            # 在前后 similarity_range 帧中查找相似图片
            for j in range(max(0, i - photo_range), min(len(images), i + photo_range + 1)):
                if j != i and not deleted[j]:
                    previous_image = cv2.imread(images[j])
                    if previous_image is not None and is_similar(previous_image, current_image):
                        is_unique = False
                        break
            
            if is_unique:
                unique_images.append(current_image)
            else:
                os.remove(images[i])  # 如果相似，删除当前图片
                deleted[i] = True  # 标记图片已被删除
        
        for i in range(10):
            if deleted[i]:
                continue  # 跳过已删除的图片
    
            current_image = cv2.imread(images[i])
            if current_image is None:
                continue
    
            similar_found = False
            for j in range(10):
                if j == i or deleted[j]:
                    continue
                reference_image = cv2.imread(images[j])
                if reference_image is not None and is_similar(reference_image, current_image):
                    similar_found = True
                    break
    
            if similar_found:
                os.remove(images[i])
                deleted[i] = True  # 标记图片已被删除
        print("Similar frames removed successfully.")
        return unique_images
    else:
        print("No images found in the directory.")
        return []
def main(output_dir):

    remove_similar_frames(output_dir)
    run_script('rename')
    

# 示例用法
current_directory = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_directory, 'output_folder')  # 替换为你的输出文件夹路径
main(output_dir)