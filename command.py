import subprocess
import configparser
import os
import tkinter as tk
from tkinter import messagebox

# ======== 可更改的参量 BEGIN ========
# 以下是可更改的参量，可以根据需要进行修改，也可在图形化界面进行修改
# 执行顺序（可在这里调整脚本执行顺序）
execution_order = ['new_folder','capture','remove','stitch','detect','recut','pdf'] #别改这个

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

            # 创建图形化界面
# 在主窗口右侧添加run_new_folder等参数的调整按钮 
def create_gui():
    # 创建主窗口
    window = tk.Tk()
    window.title("Video Score Rebuilder")
    
    # 创建滚动条
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 创建文本框
    text_box = tk.Text(window, yscrollcommand=scrollbar.set)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH)
    
    # 设置滚动条与文本框的关联
    scrollbar.config(command=text_box.yview)
    
    # 创建参数调整按钮
    def adjust_params():
        # 获取文本框中的内容
        config_content = text_box.get("1.0", tk.END)
        
        # 将文本框中的内容写入配置文件
        with open('config.ini', 'w') as config_file:
            config_file.write(config_content)
        
        # 提示用户配置文件已更新
        messagebox.showinfo("Success", "Config file updated successfully.")
        

    run_new_folder = tk.BooleanVar()
    run_capture = tk.BooleanVar()
    run_stitch = tk.BooleanVar()
    run_remove = tk.BooleanVar()
    run_detect = tk.BooleanVar()
    run_recut = tk.BooleanVar()
    run_pdf = tk.BooleanVar()

    # 创建 Checkbutton 并绑定到全局变量
    run_new_folder_button = tk.Checkbutton(window, text="New Folder", variable=run_new_folder)
    run_new_folder_button.pack()

    run_capture_button = tk.Checkbutton(window, text="Capture", variable=run_capture)
    run_capture_button.pack()
    
    run_remove_button = tk.Checkbutton(window, text="Remove", variable=run_remove)
    run_remove_button.pack()

    run_stitch_button = tk.Checkbutton(window, text="Stitch", variable=run_stitch)
    run_stitch_button.pack()

    run_detect_button = tk.Checkbutton(window, text="Detect", variable=run_detect)
    run_detect_button.pack()

    run_recut_button = tk.Checkbutton(window, text="Recut", variable=run_recut)
    run_recut_button.pack()

    run_pdf_button = tk.Checkbutton(window, text="PDF", variable=run_pdf)
    run_pdf_button.pack()
    # 创建参数调整按钮
    adjust_params_button = tk.Button(window, text="Adjust Params", command=adjust_params)
    adjust_params_button.pack()
    
    def close_window():
        window.destroy()

    run_button = tk.Button(window, text="Run Script", command=close_window)
    run_button.pack()
    # 读取配置文件内容并显示在文本框中
    with open('config.ini', 'r') as config_file:
        config_content = config_file.read()
        text_box.insert(tk.END, config_content)
        
    
    # 运行主循环
    window.mainloop()
    return run_new_folder.get(), run_capture.get(), run_stitch.get(), run_remove.get(), run_detect.get(), run_recut.get(), run_pdf.get()

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
    
    run_new_folder, run_capture, run_stitch, run_remove, run_detect, run_recut, run_pdf =create_gui()
    
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
