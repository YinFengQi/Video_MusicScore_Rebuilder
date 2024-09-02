import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取参数
start = int(config['capture']['start'])
segment__duration = int(config['capture']['segment_duration'])
frame__interval = int(config['capture']['frame_interval'])
score_threshold = float(config['capture']['score_threshold'])
light_threshold = float(config['capture']['light_threshold'])
search_area = config['capture']['search_area']

# 使用这些参数进行处理
print("参数已接收")

import cv2
import numpy as np
import os
import shutil
import subprocess
#可调参数：start_time, end_time, frame_interval,乐谱区域的threshol,process的light_threshold,

# 运行函数
def run_script(script_name):
    script_path = os.path.join(current_directory, f"{script_name}.py")
    print(f"Running {script_name}...")
    try:
        subprocess.run(['python3.11', script_path, 'config.ini'], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e}\n")

def capture_frames(video_path, output_dir, start_time, end_time, frame_interval):
    cap = cv2.VideoCapture(video_path)
    
    # 转换时间到毫秒
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000
    frame_interval_ms = frame_interval * 1000
    
    current_time = start_time_ms
    video_duration_ms = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) * 1000)

    while current_time <= end_time_ms and current_time <= video_duration_ms:
        # 设置视频到指定的时间
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time)
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理并保存帧
        score_area = extract_score_area(frame)
        frame_output_path = os.path.join(output_dir, f"frame_{current_time}.png")
        cv2.imwrite(frame_output_path, score_area)
        
        current_time += frame_interval_ms
    
    cap.release()


def extract_score_area(frame, score_threshold=score_threshold, search_area=search_area):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, score_threshold, 255, cv2.THRESH_BINARY)
    
    height, width = binary.shape
    
    # 根据用户选择决定搜索范围的起始点
    if search_area == 'bottom':
        start_y = height // 2
        end_y = height
    elif search_area == 'top':
        start_y = height // 2
        end_y = 0  # 从中线开始向上搜索
    else:
        raise ValueError("search_area must be 'top' or 'bottom'")
    
    boundary = start_y  # 初始边界为中线
    if search_area == 'bottom':
        for y in range(start_y, end_y):
            row = frame[y, :]
            above_row = frame[y-1, :]
            
            diff = np.mean(np.abs(row.astype(int) - above_row.astype(int)))

            if diff > 50:
                boundary = y
                break
        
        # 提取识别出的乐谱区域
        score_area = frame[boundary:end_y, 0:width]
    
    elif search_area == 'top':
        for y in range(start_y, end_y, -1):  # 向上搜索
            row = frame[y, :]
            below_row = frame[y+1, :]  # 在下方的行
            
            diff = np.mean(np.abs(row.astype(int) - below_row.astype(int)))

            if diff > 50:
                boundary = y
                break
        
        # 提取识别出的乐谱区域
        score_area = frame[0:boundary, 0:width]
    
    return score_area

def preprocess_image(image, light_threshold):
    light_pixels = image > light_threshold
    image[light_pixels] = 255
    return image


def process_video_in_segments(video_path, output_dir, segment_duration=segment__duration, frame_interval=frame__interval,start=start):
    cap = cv2.VideoCapture(video_path)
    total_duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
    cap.release()
    
    # 分段处理视频
    for start_time in range(start, total_duration, segment_duration):
        end_time = min(start_time + segment_duration, total_duration)
        capture_frames(video_path, output_dir, start_time=start_time, end_time=end_time,frame_interval=frame_interval)


def main(video_path, output_dir):
    # 清空输出文件夹
    shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 查找第一个视频
    video_files = [file for file in os.listdir(video_path) if file.endswith('.mp4')]
    if len(video_files) > 0:
        first_video = os.path.join(video_path, video_files[0])
        process_video_in_segments(first_video, output_dir)
        
        # 对文件夹中的图像进行预处理
        images = sorted([os.path.join(output_dir, img) for img in os.listdir(output_dir) if img.endswith('.png')])
        
        for img_path in images:
            image = cv2.imread(img_path)
            if image is not None:
                preprocessed_image = preprocess_image(image, light_threshold)
                cv2.imwrite(img_path, preprocessed_image)  # 覆盖保存预处理后的图像
        print("处理完成")
    else:
        print("未找到视频文件")
    run_script('rename')
        
        

current_directory = os.path.dirname(os.path.abspath(__file__))

video_path = os.path.join(current_directory, 'video')
output_dir = os.path.join(current_directory, 'output_folder')
main(video_path, output_dir)