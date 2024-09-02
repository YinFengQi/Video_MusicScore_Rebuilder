import subprocess
import configparser
import os

# ======== 可更改的参量 BEGIN ========
# 修改这些变量以控制脚本的行为
run_new_folder = 1
run_capture = 0
run_stitch = 0
run_remove = 0
run_detect = 0
run_recut = 0
run_pdf = 0

# 执行顺序（可在这里调整脚本执行顺序）
execution_order = ['new_folder','capture','remove','stitch','detect','recut','pdf'] 

# remove.py 参数
remove_params = {
    'is_similar_threshold': 0.1,
    'is_colorful_threshold': 20,
    'is_colorful_grey': 20,
    'is_mostly_black_black_threshold': 0.6,
    'range': 10,
    'cut_right': 0.2,
}

# stitch.py 参数
stitch_params = {
    'cut_up': 0.5,
    'cut_bot': 0.1,
    'cut_right': 0.25,
    'test': False,
    'reco_limit':0.9
}

# capture.py 参数
capture_params = {
    'start':0,
    'segment_duration':20,
    'frame_interval':1,
    'score_threshold': 200,
    'light_threshold': 250,
    'search_area': 'bottom',
}
detect_params = {
    'manual': True,
    'single_line': True,
}
pdf_params = {
    'lines':6,
}

# ======== 可更改的参量 END ========

# 脚本与文件的对应关系
current_directory = os.path.dirname(os.path.abspath(__file__))
scripts = {
    'capture': os.path.join(current_directory, 'capture.py'),
    'stitch': os.path.join(current_directory, 'stitch.py'),
    'remove': os.path.join(current_directory, 'remove.py'),
    'detect': os.path.join(current_directory, 'detect.py'),
    'recut': os.path.join(current_directory, 'recut.py'),
    'pdf': os.path.join(current_directory, 'pdf.py'),
    'new_folder': os.path.join(current_directory, 'new_folder.py'),
}

# 生成配置文件
def create_config(filename, params):
    config = configparser.ConfigParser()
    for section, settings in params.items():
        config[section] = {key: str(value) for key, value in settings.items()}
    with open(filename, 'w') as configfile:
        config.write(configfile)

# 运行函数
def run_script(script_name):
    script_path = scripts[script_name]
    print(f"Running {script_name}...")
    try:
        subprocess.run(['python3.11', script_path, 'config.ini'], check=True)
        print(f"{script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e}\n")

# 控制逻辑
if __name__ == "__main__":
    # 创建配置文件
    create_config('config.ini', {
        'remove': remove_params,
        'stitch': stitch_params,
        'capture': capture_params,
        'detect': detect_params,
        'pdf': pdf_params,
    })

    for script in execution_order:
        if script == 'capture' and run_capture:
            run_script('capture')
        elif script == 'stitch' and run_stitch:
            run_script('stitch')
        elif script == 'remove' and run_remove:
            run_script('remove')
        elif script == 'detect' and run_detect:
            run_script('detect')
        elif script == 'recut' and run_recut:
            run_script('recut')
        elif script == 'pdf' and run_pdf:
            run_script('pdf')
        elif script == 'new_folder' and run_new_folder:
            run_script('new_folder')