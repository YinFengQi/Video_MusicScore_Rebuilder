import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取参数
cut_up = float(config['stitch']['cut_up'])
cut_bot = float(config['stitch']['cut_bot'])
cut_right = float(config['stitch']['cut_right'])
test = config['stitch']['test'].lower() == 'true'
reco_limit = float(config['stitch']['reco_limit'])
# 使用这些参数进行处理
print("参数已接收")
final_output_path = "/Users/pleiades/Documents/VSCode/python/stitch"
# 这里是 stitch.py 的其余逻辑
import os
import cv2
import numpy as np
import shutil
#可调参数：cut_up,cut_bot,cut_right,test,reco_limit

def find_max_image_number(directory):
    # 获取目录中的所有文件
    files = os.listdir(directory)
    
    # 过滤出符合格式的文件名
    png_files = [f for f in files if f.endswith('.png') and f.split('.')[0].isdigit()]
    
    if not png_files:
        print("No valid image files found in the directory.")
        return None
    
    # 提取文件名中的数字部分并找到最大的数字
    max_number = max(int(os.path.splitext(f)[0]) for f in png_files)
    
    return max_number

def match_and_mark_images(directory, start_n=0, end_n=10):
    match_info = {}
    for n in range(start_n, end_n):
        img1_path = os.path.join(directory, f"{n}.png")
        img2_path = os.path.join(directory, f"{n+1}.png")

        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1 is None or img2 is None:
            continue
        
        # 获取图像尺寸
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape

        # 如果图像高度不一致，将其调整为相同高度
        if h1 != h2:
            new_height = min(h1, h2)
            img1 = cv2.resize(img1, (w1, new_height))
            img2 = cv2.resize(img2, (w2, new_height))
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
        
        # 提取前一个图像的右边四分之一部分，并切去顶部和底部
        cut_top = int(cut_up * h1)
        cut_bottom = int((1 - cut_bot) * h1)
        right_part_img1 = img1[cut_top:cut_bottom, int((1-cut_right)*w1):w1]
        
        # 确保模板尺寸小于或等于搜索图像尺寸
        if right_part_img1.shape[0] > h2 or right_part_img1.shape[1] > w2:
            print(f"Skipping frames {n} and {n+1}: Template is larger than search area")
            continue
        
        # 在后一个图像的全部中进行匹配
        result = cv2.matchTemplate(img2, right_part_img1, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        # 标记相似的部分
        if max_val > reco_limit:  # 设定阈值
            top_left = max_loc
            bottom_right = (top_left[0] + right_part_img1.shape[1], top_left[1] + right_part_img1.shape[0])
            
            # 保存匹配区域的信息
            match_info[n] = (top_left, bottom_right)
            
            # 将 img1 和 img2 拼接到一起形成一张图像
            combined_img = cv2.hconcat([img1, img2])
            
            # 标记 img1 上的模板部分（蓝色）
            cv2.rectangle(combined_img, 
                          (w1 - right_part_img1.shape[1], cut_top), 
                          (w1, cut_bottom), 
                          (255, 0, 0), 2)
            
            # 标记 img2 上的匹配部分（红色）
            cv2.rectangle(combined_img, 
                          (w1 + top_left[0], top_left[1]), 
                          (w1 + bottom_right[0], bottom_right[1]), 
                          (0, 0, 255), 2)

            # 保存标记后的图像
            marked_combined_dir = os.path.join(directory, 'test')
            os.makedirs(marked_combined_dir, exist_ok=True)
            cv2.imwrite(os.path.join(marked_combined_dir, f"marked_combined_{n}.png"), combined_img)
    
    return match_info


def stitch_images_into_strip(directory, max_number):
    # 调用 match_and_mark_images 函数以获取匹配信息
    match_info = match_and_mark_images(directory, start_n=0, end_n=max_number)
    
    images = sorted(
        [img for img in os.listdir(directory) if img.endswith('.png') and img.split('.')[0].isdigit()],
        key=lambda x: int(os.path.splitext(x)[0])
    )
    
    if not images:
        print("No images found in the directory.")
        return

    # 读取第一张图像并检查是否成功
    base_img = cv2.imread(os.path.join(directory, images[0]))
    if base_img is None:
        print(f"Failed to read image: {images[0]}")
        return

    stitched_img = base_img

    for i in range(1, len(images)):
        img1 = stitched_img
        img2 = cv2.imread(os.path.join(directory, images[i]))

        if img2 is None:
            print(f"Skipping frame {i}: Could not read image.")
            continue
        
        # 获取匹配区域
        if i-1 in match_info:
            top_left, bottom_right = match_info[i-1]
            # 计算拼接位置
            h1, w1, _ = img1.shape
            template_width = bottom_right[0] - top_left[0]
            
            # 确保模板尺寸小于或等于搜索图像尺寸
            if template_width > img2.shape[1]:
                print(f"Skipping frame {i}: Template width is larger than image width.")
                continue
            
            # 创建新的长条图像并拼接
            new_width = ((stitched_img.shape[1]-template_width) + (img2.shape[1] - top_left[0]))
            new_stitched_img = np.zeros((h1, new_width, 3), dtype=np.uint8)

            # 左侧部分采用当前拼接的图像
            new_stitched_img[:, :stitched_img.shape[1]-template_width] = stitched_img[:,:-template_width]

            new_stitched_img[:, stitched_img.shape[1]-template_width:] = img2[:, top_left[0]:]
            stitched_img = new_stitched_img
        else:
            print(f"No match info available for frames {i-1} and {i}.")
            # 保存当前的长条图像
            output_path = os.path.join(final_output_path, f"stitched_strip_{i-1}.png")
            if cv2.imwrite(output_path, stitched_img):
                print(f"Saved stitched strip to {output_path}.")
            else:
                print(f"Failed to save stitched strip to {output_path}.")
            # 重新开始拼接，使用下一张图像作为基准
            stitched_img = img2
        # 保存最后的长条乐谱
    output_path = os.path.join(final_output_path, f"stitched_strip_{max_number}.png")
    if cv2.imwrite(output_path, stitched_img):
        print(f"Saved stitched strip to {output_path}.")
    else:
        print(f"Failed to save stitched strip to {output_path}.")
    print("All done!")
    
    
if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_directory, 'output_folder')
    final_output_path = os.path.join(current_directory, 'stitch')
    # Clear the final output directory
    shutil.rmtree(final_output_path)
    os.makedirs(final_output_path)
    max_number = find_max_image_number(output_dir)
    if(test):
        match_and_mark_images(output_dir, start_n=0, end_n=10)
    else:
        stitch_images_into_strip(output_dir,max_number)